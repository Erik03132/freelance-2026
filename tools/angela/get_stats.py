import urllib.request
import json
import datetime

WH_URL = "https://incubird.bitrix24.ru/rest/41624/w2b11s24upbycolk/"
TODAY = "2026-04-21T00:00:00+03:00"

def get_list(method, filter_params):
    url = f"{WH_URL}{method}?{filter_params}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get('result', [])
    except Exception as e:
        print(f"Error {method}: {e}")
        return []

# Fetch LEADS created today
leads = get_list("crm.lead.list.json", "filter[>DATE_CREATE]=2026-04-21T00:00:00%2B03:00&select[]=ID")

# Fetch DEALS created/modified today
deals_create = get_list("crm.deal.list.json", "filter[>DATE_CREATE]=2026-04-21T00:00:00%2B03:00&select[]=ID&select[]=OPPORTUNITY&select[]=ASSIGNED_BY_ID&select[]=TITLE")
deals_modify = get_list("crm.deal.list.json", "filter[>DATE_MODIFY]=2026-04-21T00:00:00%2B03:00&select[]=ID&select[]=OPPORTUNITY&select[]=ASSIGNED_BY_ID&select[]=TITLE")

print(f"Leads created today: {len(leads)}")
print(f"Deals created today: {len(deals_create)}")
print(f"Deals modified today: {len(deals_modify)}")

if len(deals_modify) > 0:
    for d in deals_modify[:10]:
        print(f" - Deal {d.get('ID')}: {d.get('TITLE')} | {d.get('OPPORTUNITY')} RUB | Mgr ID {d.get('ASSIGNED_BY_ID')}")
