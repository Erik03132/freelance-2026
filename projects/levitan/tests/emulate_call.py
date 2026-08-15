"""
Эмулятор диалога без телефона (A-план, шаг 1).
Гоняет полные сценарии «клиент ↔ агент» на детерминированной логике funnel.py (SSoT),
симулирует LLM-путь (TTFT по текущим измерениям) и заглушку-преемпт (фича из плана A).
Замеряет resp_lat, покрытие fast-path, «медленные» ходы. Требует БЕЗ livekit/телефонии.

Запуск:  python3 tests/emulate_call.py            # baseline (без заглушки)
         python3 tests/emulate_call.py --placeholder  # с заглушкой
"""

import sys
import time
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parent.parent / "agent"
sys.path.insert(0, str(AGENT_DIR))

import funnel  # noqa: E402

TTFT_S = float(sys.argv[sys.argv.index("--ttft") + 1]) if "--ttft" in sys.argv else 2.0
USE_PLACEHOLDER = "--placeholder" in sys.argv


def _next_placeholder() -> str:
    return funnel.next_placeholder()


class _Msg:
    def __init__(self, role, content):
        self.role = role
        self.content = content


class _Ctx:
    def __init__(self, items):
        self.items = items


class _LLM:
    def __init__(self, phone=""):
        self._asked_quantity = False
        self._asked_delivery = False
        self._caller_phone = phone
        self._preempt_fired = False


class Emulator:
    def __init__(self, phone="9859234644"):
        self.llm = _LLM(phone)
        self.ctx = _Ctx([])
        self.turns = []
        self.resp_lat = []
        self.fast_hits = 0
        self.llm_hits = 0
        self.placeholder_hits = 0
        self.saved_leads = []

    def say_assistant(self, text):
        if "доставки" in text or "доставк" in text:
            self.llm._asked_delivery = True
        if self.llm._asked_delivery is False and "голов вам нужно" in text:
            pass  # флаг количества взводит сам funnel
        self.ctx.items.append(_Msg("assistant", text))

    def user_says(self, text):
        self.ctx.items.append(_Msg("user", text))

    def _llm_reply(self, text):
        """Симуляция LLM-ответа: фиксированная задержка TTFT."""
        time.sleep(TTFT_S)
        self.llm_hits += 1
        return f"(LLM) {text}"

    def agent_turn(self):
        t0 = time.time()
        # 1) preempt/placeholder: на «незнакомый» вопрос — мгновенная заглушка
        norm = funnel.normalize(funnel._last_user_text(self.ctx))
        fast = funnel._fast_path_reply(self.ctx, self.llm)
        if fast is not None:
            self.fast_hits += 1
            self.resp_lat.append(time.time() - t0)
            self.say_assistant(fast)
            return fast, "fast", time.time() - t0
        # 2) незнакомый вопрос -> заглушка (мгновенно) + LLM в фоне
        if USE_PLACEHOLDER and norm:
            ph = _next_placeholder()
            self.placeholder_hits += 1
            self.resp_lat.append(time.time() - t0)
            self.say_assistant(ph)
            print(f"      [placeholder] -> {ph!r}")
            # LLM «доканчивает» с TTFT, замер его отдельно
            t_llm = time.time()
            answer = self._llm_reply("(ответ LLM)")
            self.say_assistant(answer)
            return answer, "placeholder+llm", time.time() - t0
        # 3) чистый LLM-путь (без заглушки)
        self.resp_lat.append(time.time() - t0)
        answer = self._llm_reply("(ответ LLM)")
        self.say_assistant(answer)
        return answer, "llm", time.time() - t0

    def summary(self):
        n = len(self.turns)
        avg = sum(self.resp_lat) / len(self.resp_lat) if self.resp_lat else 0
        slow = [r for r in self.resp_lat if r > 2.5]
        return {
            "turns": n,
            "avg_resp_lat": round(avg, 2),
            "fast": self.fast_hits,
            "placeholder": self.placeholder_hits,
            "llm": self.llm_hits,
            "slow_gt_2_5s": len(slow),
            "saved_leads": len(self.saved_leads),
        }


SCENARIOS = {
    "broilers_success": [
        "Да",
        "двести пятьдесят голов",
        "да",
    ],
    "broilers_negative": [
        "Нет",
    ],
    "mixed_topics": [
        "Да",
        "сто голов",
        "А сколько весит цыплёнок?",
        "да",
    ],
    "first_turn_question": [
        "А какой у вас график работы?",
        "Сколько стоит доставка в Краснодар?",
    ],
    "faq_real_questions": [
        "сколько стоит бройлер",
        "какие породы есть",
        "доставка по крыму есть",
        "что с вакцинацией",
        "можно ли приехать и забрать",
        "работаете ли вы в воскресенье",
        "а какая гарантия на птицу",
        "примут ли возврат если цыплёнок сдохнет",
    ],
}


def run_scenario(name, script):
    print(f"\n=== Сценарий: {name} ({'заглушка' if USE_PLACEHOLDER else 'baseline'}) ===")
    em = Emulator()
    for i, utt in enumerate(script, 1):
        em.user_says(utt)
        ans, kind, lat = em.agent_turn()
        em.turns.append((utt, ans, kind, lat))
        mark = "🟢" if kind == "fast" else ("🟡" if kind.startswith("placeholder") else "🔴")
        print(f"{mark} клиент[{i}]: {utt!r}\n   агент: {ans!r}  [{kind}, resp_lat={lat:.2f}s]")
    return em


def main():
    print(f"TTFT_sim={TTFT_S}s, placeholder={USE_PLACEHOLDER}")
    results = {}
    for name, script in SCENARIOS.items():
        em = run_scenario(name, script)
        results[name] = em.summary()
    print("\n=== Итоги ===")
    print(
        f"{'сценарий':<22} {'turns':<6} {'avg':<6} {'fast':<6} {'ph':<5} {'llm':<5} {'slow>2.5':<9} {'leads'}"
    )
    for k, v in results.items():
        print(
            f"{k:<22} {v['turns']:<6} {v['avg_resp_lat']:<6} {v['fast']:<6} "
            f"{v['placeholder']:<5} {v['llm']:<5} {v['slow_gt_2_5s']:<9} {v['saved_leads']}"
        )


if __name__ == "__main__":
    main()
