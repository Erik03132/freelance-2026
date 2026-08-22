#!/usr/bin/env python3
"""
Levitan — нагрузочный probe гейта стабильности (AVM-0b).

ЦЕЛЬ (AVM-0b из projects/ai-bureau/ai-voice-manager/ACTIVE_TASKS.md):
  убедиться, что дешёвый/бесплатный каскад моделей под нагрузкой НЕ роняет звонок
  (нет глухого/немого звонка из-за 402 Payment Required / 429 rate-limit / 502).

ЧТО ДЕЛАЕТ:
  шлёт N параллельных chat.completions в OmniRoute (VPS :20128 по умолчанию),
  каждый — СЛУЧАЙНЫЙ вопрос из пула (имитация реального диалога), и классифицирует
  ответ: ok / 402 / 429 / 502 / timeout / other. Считает долю успеха.

СТЕК (SSoT): agent/levitan_agent.py -> OmniRoute VPS (:20128).
  Скрипт НЕ дублирует стек и НЕ звонит — только prob'ит LLM-эндпоинт агента.

ИДЕМПОТЕНТНОСТЬ: только чтение (POST к LLM без сайд-эффектов), повтор безопасен.
PIPELINE-SAFE: JSON в stdout (или --out), ошибки в stderr, код выхода != 0 при падении гейта.
CP-1: flags, --help с примерами, --dry-run, не хардкодит cwd (принимает --base-url).

Примеры:
  python3 agent/stability_probe.py --help
  python3 agent/stability_probe.py --base-url http://127.0.0.1:20128/v1 --model free-cascade --requests 40 --concurrency 8
  python3 agent/stability_probe.py --dry-run --requests 40
  python3 agent/stability_probe.py --base-url http://127.0.0.1:20128/v1 --out /tmp/avm_probe.json
"""

import argparse
import concurrent.futures as cf
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request

# OmniRoute — локальный/VPS эндпоинт агента. НЕ пускаем через корпоративный прокси
# (LLM_PROXY со spec socks5h ломает urllib: "unknown url type: socks5h", и SSE/стриминг
# режется). Сбрасываем proxy-env для этого процесса (как в omni-auto-router/server.py).
for _p in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_p, None)
os.environ["NO_PROXY"] = "127.0.0.1,localhost"
os.environ["no_proxy"] = "127.0.0.1,localhost"

DEFAULT_BASE = "http://127.0.0.1:20128/v1"
DEFAULT_MODEL = "free-cascade"  # как в omni-auto-router server.py
DEFAULT_KEY_ENV = "OMNIR_VPS_KEY"  # fallback: OPENROUTER_API_KEY

PROBE_SYSTEM = "Ты — голосовой менеджер компании. Отвечай кратко (1-2 предложения), по существу."
# Пул разных вопросов клиента — имитация реального диалога (AVM-0b: ловим нестабильность на разных запросах).
PROBE_QUESTIONS = [
    "Сколько стоит доставка?",
    "А вы работаете в выходные?",
    "Какая гарантия на товар?",
    "Можно ли оплатить картой?",
    "Сколько времени занимает замер?",
    "Вы делаете доставку за МКАД?",
    "Подскажите ваш график работы",
    "Это всё ещё актуально по цене?",
    "Можно ли отменить заказ?",
    "Кто у вас контактное лицо для договора?",
    "Что входит в базовый тариф?",
    "Сколько примерно стоит такая услуга?",
]


def build_body(model):
    q = random.choice(PROBE_QUESTIONS)
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": PROBE_SYSTEM},
            {"role": "user", "content": q},
        ],
        "max_tokens": 60,
        "temperature": 0.3,
        "stream": False,
    }, q


def parse_args():
    ap = argparse.ArgumentParser(
        description="AVM-0b stability probe: гоняет OmniRoute под нагрузкой, ловит 402/429/502.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Примеры:\n"
            "  stability_probe.py --base-url http://127.0.0.1:20128/v1 --model free-cascade --requests 40 --concurrency 8\n"
            "  stability_probe.py --dry-run --requests 40\n"
            "  stability_probe.py --base-url http://127.0.0.1:20128/v1 --out /tmp/avm_probe.json\n"
        ),
    )
    ap.add_argument(
        "--base-url",
        default=DEFAULT_BASE,
        help=f"OpenAI-compatible база OmniRoute (default: {DEFAULT_BASE})",
    )
    ap.add_argument(
        "--model", default=DEFAULT_MODEL, help=f"model из запроса (default: {DEFAULT_MODEL})"
    )
    ap.add_argument("--requests", type=int, default=20, help="сколько запросов всего (default: 20)")
    ap.add_argument("--concurrency", type=int, default=5, help="параллельных запросов (default: 5)")
    ap.add_argument(
        "--timeout", type=float, default=30.0, help="таймаут на 1 запрос, сек (default: 30)"
    )
    ap.add_argument(
        "--min-success-rate",
        type=float,
        default=0.95,
        help="доля ok для прохождения гейта (default: 0.95)",
    )
    ap.add_argument(
        "--api-key-env",
        default=DEFAULT_KEY_ENV,
        help=f"env с ключом (fallback: OPENROUTER_API_KEY) (default: {DEFAULT_KEY_ENV})",
    )
    ap.add_argument("--out", default=None, help="записать JSON-отчёт в файл (иначе только stdout)")
    ap.add_argument("--dry-run", action="store_true", help="ничего не шлёт; выводит, что сделал бы")
    return ap.parse_args()


def classify(status, err_text):
    """Вернуть (code, bucket) по HTTP-статусу."""
    if status is None:
        return ("timeout_or_connerr", "other")
    if 200 <= status < 300:
        return (str(status), "ok")
    if status == 402:
        return (str(status), "402")
    if status == 429:
        return (str(status), "429")
    if status == 502:
        return (str(status), "502")
    if status == 503:
        return (str(status), "503")
    return (str(status), "other")


def one_request(base_url, model, api_key, timeout, idx):
    url = base_url.rstrip("/") + "/chat/completions"
    body, question = build_body(model)
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("User-Agent", "levitan-stability-probe/1.0")
    t0 = time.time()
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        status = resp.getcode()
        _ = resp.read()
        elapsed = time.time() - t0
        code, bucket = classify(status, None)
        return {
            "idx": idx,
            "status": code,
            "bucket": bucket,
            "question": question,
            "elapsed_s": round(elapsed, 2),
            "error": None,
        }
    except urllib.error.HTTPError as e:
        elapsed = time.time() - t0
        status = e.code
        err_text = ""
        try:
            err_text = e.read().decode()[:200]
        except Exception:
            pass
        code, bucket = classify(status, err_text)
        return {
            "idx": idx,
            "status": code,
            "bucket": bucket,
            "question": question,
            "elapsed_s": round(elapsed, 2),
            "error": err_text,
        }
    except Exception as e:
        elapsed = time.time() - t0
        return {
            "idx": idx,
            "status": "timeout_or_connerr",
            "bucket": "other",
            "question": question,
            "elapsed_s": round(elapsed, 2),
            "error": str(e)[:200],
        }


def run_probe(args, api_key):
    results = []
    with cf.ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = [
            ex.submit(one_request, args.base_url, args.model, api_key, args.timeout, i)
            for i in range(args.requests)
        ]
        for f in cf.as_completed(futs):
            results.append(f.result())
    results.sort(key=lambda r: r["idx"])
    return results


def summarize(results, args):
    total = len(results)
    buckets = {}
    for r in results:
        buckets[r["bucket"]] = buckets.get(r["bucket"], 0) + 1
    ok = buckets.get("ok", 0)
    rate = ok / total if total else 0.0
    elapsed_list = [
        r.get("elapsed_s")
        for r in results
        if r.get("bucket") == "ok" and r.get("elapsed_s") is not None
    ]
    avg_lat = round(sum(elapsed_list) / len(elapsed_list), 2) if elapsed_list else None
    max_lat = max(elapsed_list) if elapsed_list else None
    gate_pass = rate >= args.min_success_rate
    return {
        "probe": "avm-0b-stability",
        "base_url": args.base_url,
        "model": args.model,
        "total": total,
        "ok": ok,
        "success_rate": round(rate, 4),
        "min_success_rate": args.min_success_rate,
        "gate_pass": gate_pass,
        "buckets": buckets,
        "avg_ok_latency_s": avg_lat,
        "max_ok_latency_s": max_lat,
        "ts": int(time.time()),
    }


def main():
    args = parse_args()
    api_key = os.getenv(args.api_key_env) or os.getenv("OPENROUTER_API_KEY") or ""

    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "would_send": args.requests,
                    "concurrency": args.concurrency,
                    "base_url": args.base_url,
                    "model": args.model,
                    "timeout": args.timeout,
                    "min_success_rate": args.min_success_rate,
                    "api_key_present": bool(api_key),
                    "note": "Ничего не отправлено. Гейт не проверялся.",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    print(
        f"[probe] base={args.base_url} model={args.model} "
        f"n={args.requests} conc={args.concurrency} key={'set' if api_key else 'MISSING'}",
        file=sys.stderr,
        flush=True,
    )
    results = run_probe(args, api_key)
    summary = summarize(results, args)

    report = {"summary": summary, "results": results}
    out_json = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(out_json + "\n")
        print(f"[probe] report -> {args.out}", file=sys.stderr, flush=True)
    print(out_json)

    if not summary["gate_pass"]:
        print(
            f"[probe] GATE FAIL: success_rate={summary['success_rate']} "
            f"< min={summary['min_success_rate']} (buckets={summary['buckets']})",
            file=sys.stderr,
            flush=True,
        )
        return 2  # явный ненулевой код — гейт не закрыт
    print(f"[probe] GATE PASS: success_rate={summary['success_rate']}", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
