"""
Freelance Agent CLI — отклик на фриланс-задачу с 30% работы и дорожной картой.

Использование:
  python main.py propose "текст задачи"
  python main.py propose --file /tmp/task.txt --title "Название" --budget 10000
  cat /tmp/task.txt | python main.py propose
"""

import argparse
import sys
from pathlib import Path

from mcp_servers.proposal_engine.generator import ProposalGenerator


def cmd_propose(args):
    task = args.task or ""
    if args.file:
        task = Path(args.file).read_text(encoding="utf-8")
    elif not task.strip() and not sys.stdin.isatty():
        task = sys.stdin.read()
    if not task.strip():
        print("Укажи задачу: аргументом, --file, или через pipe.")
        return

    gen = ProposalGenerator()
    result = gen.generate(task, title=args.title or "", budget=args.budget or 0)
    print(result)


def cmd_analyze(args):
    task = args.task or ""
    if args.file:
        task = Path(args.file).read_text(encoding="utf-8")
    elif not task.strip() and not sys.stdin.isatty():
        task = sys.stdin.read()
    if not task.strip():
        print("Укажи задачу.")
        return

    from mcp_servers.proposal_engine.scout import ScoutAgent
    scout = ScoutAgent()
    import json
    result = scout.analyze(args.title or "", task, args.budget or 0)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Freelance Agent — отклики с 30% работы")
    sub = parser.add_subparsers(dest="command")

    propose_p = sub.add_parser("propose", help="Сгенерировать отклик на задачу")
    propose_p.add_argument("task", nargs="*", default="")
    propose_p.add_argument("--file", help="Файл с описанием задачи")
    propose_p.add_argument("--title", help="Название задачи")
    propose_p.add_argument("--budget", type=int, default=0, help="Бюджет в рублях")

    analyze_p = sub.add_parser("analyze", help="Проанализировать задачу (без генерации)")
    analyze_p.add_argument("task", nargs="*", default="")
    analyze_p.add_argument("--file", help="Файл с описанием задачи")
    analyze_p.add_argument("--title", help="Название задачи")
    analyze_p.add_argument("--budget", type=int, default=0, help="Бюджет в рублях")

    args = parser.parse_args()
    if args.command == "propose":
        args.task = " ".join(args.task) if isinstance(args.task, list) else args.task
        cmd_propose(args)
    elif args.command == "analyze":
        args.task = " ".join(args.task) if isinstance(args.task, list) else args.task
        cmd_analyze(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
