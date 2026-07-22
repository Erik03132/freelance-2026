"""
Freelance Agent CLI — отклик на фриланс-задачу.

Команды:
  propose — честный отклик (для техзадач на разработку)
  kwork   — скрытая автоматизация (отклик как оператор)
  analyze — анализ задачи без генерации

Использование:
  python main.py propose "текст задачи"
  python main.py kwork "текст задачи оператора" --budget 50000
  cat /tmp/task.txt | python main.py kwork
  python main.py analyze "текст задачи"
"""

import argparse
import sys
from pathlib import Path

from mcp_servers.proposal_engine.generator import ProposalGenerator


def _read_task(args):
    task = args.task or ""
    if args.file:
        task = Path(args.file).read_text(encoding="utf-8")
    elif not task.strip() and not sys.stdin.isatty():
        task = sys.stdin.read()
    if not task.strip():
        print("Укажи задачу: аргументом, --file, или через pipe.")
        return None
    return task


def cmd_propose(args):
    task = _read_task(args)
    if task is None:
        return
    gen = ProposalGenerator()
    result = gen.generate(task, title=args.title or "", budget=args.budget or 0)
    print(result)


def cmd_kwork(args):
    """Отклик на задачу про «оператора» — скрытая автоматизация."""
    task = _read_task(args)
    if task is None:
        return
    gen = ProposalGenerator()
    result = gen.generate_kwork(task, title=args.title or "", budget=args.budget or 0)
    print(result)


def cmd_analyze(args):
    task = _read_task(args)
    if task is None:
        return
    from mcp_servers.proposal_engine.scout import ScoutAgent
    scout = ScoutAgent()
    import json
    result = scout.analyze(args.title or "", task, args.budget or 0)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Freelance Agent — отклики и автоматизация")
    sub = parser.add_subparsers(dest="command")

    propose_p = sub.add_parser("propose", help="Честный отклик с 30%% решения")
    propose_p.add_argument("task", nargs="*", default="")
    propose_p.add_argument("--file", help="Файл с описанием задачи")
    propose_p.add_argument("--title", help="Название задачи")
    propose_p.add_argument("--budget", type=int, default=0, help="Бюджет в рублях")

    kwork_p = sub.add_parser("kwork", help="Скрытая автоматизация (отклик как оператор)")
    kwork_p.add_argument("task", nargs="*", default="")
    kwork_p.add_argument("--file", help="Файл с описанием задачи")
    kwork_p.add_argument("--title", help="Название задачи")
    kwork_p.add_argument("--budget", type=int, default=0, help="Бюджет в рублях")

    analyze_p = sub.add_parser("analyze", help="Анализ задачи (без генерации)")
    analyze_p.add_argument("task", nargs="*", default="")
    analyze_p.add_argument("--file", help="Файл с описанием задачи")
    analyze_p.add_argument("--title", help="Название задачи")
    analyze_p.add_argument("--budget", type=int, default=0, help="Бюджет в рублях")

    args = parser.parse_args()
    if args.command == "propose":
        args.task = " ".join(args.task) if isinstance(args.task, list) else args.task
        cmd_propose(args)
    elif args.command == "kwork":
        args.task = " ".join(args.task) if isinstance(args.task, list) else args.task
        cmd_kwork(args)
    elif args.command == "analyze":
        args.task = " ".join(args.task) if isinstance(args.task, list) else args.task
        cmd_analyze(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
