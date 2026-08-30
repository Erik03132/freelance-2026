import json

d = json.load(open("/Users/igorvasin/.hermes/cron/jobs.json"))
for j in d["jobs"]:
    if j.get("id") == "2411147d50d6":
        print("NAME   :", j.get("name"))
        print("SCHED  :", j.get("schedule"))
        print("SCRIPT :", repr(j.get("script", ""))[:400])
        print("PROMPT :", repr(j.get("prompt", ""))[:200])
        print("DELIVER:", j.get("deliver"))
