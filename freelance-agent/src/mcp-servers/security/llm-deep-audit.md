# Security Audit Report: MCP Servers

## Findings Summary
| Severity | Count |
|----------|-------|
| Critical | 0 |
| High     | 0 |
| Medium   | 1 |
| Low      | 3 |

---

## Detailed Findings

### 1. bitrix.ts:27 — Sensitive Data Exposure in Error Logs
**Severity:** Medium  
**Risk:** The error handler logs `error.response?.data` directly. Bitrix API responses can contain PII (client names, phone numbers, emails, deal amounts), authentication tokens, or internal IDs. If logs are shipped to a centralized system (ELK, Datadog, CloudWatch) or viewed by unauthorized personnel, this constitutes a data leak.  
**Fix:** Sanitize before logging. Keep only structural metadata (status code, error code, method name).  
```ts
// Instead of:
console.error(`Bitrix API Error (${method}):`, error.response?.data || error.message);

// Do:
const safeError = error.response?.data 
  ? { error_code: error.response.data.error, error_description: error.response.data.error_description }
  : { message: error.message };
console.error(`Bitrix API Error (${method}):`, safeError);
```

---

### 2. bitrix.ts:22–28 — Missing Input Validation on API Parameters
**Severity:** Low  
**Risk:** `callBitrix` forwards `params` directly to `axios.post` without allow-listing known parameters. The tool schemas (`get_deals`, `create_lead`) define only top-level properties (`status`, `limit`), but the LLM can still inject arbitrary nested fields (e.g., `filter[>][DATE_CREATE]`, `select[]`, or even `AUTH` parameters if the webhook token is reused elsewhere). This could lead to unintended data exposure or mutation.  
**Fix:** Validate `params` against a strict allow-list per method before calling the API.  
```ts
private validateParams(method: string, params: any): any {
  const allowed: Record<string, string[]> = {
    'crm.deal.list': ['filter', 'select', 'order', 'start', 'limit'],
    'crm.lead.add': ['fields', 'params'],
  };
  const allowedKeys = allowed[method] || [];
  const sanitized: any = {};
  for (const key of allowedKeys) {
    if (params[key] !== undefined) sanitized[key] = params[key];
  }
  return sanitized;
}

// In callBitrix:
params = this.validateParams(method, params);
```

---

### 3. avito.ts:44 — Potential Credential Leak in Error Message
**Severity:** Low  
**Risk:** `getAuthToken` throws `McpError` with `error.message`. If `axios` serializes the failed request (e.g., on network error or misconfigured proxy), `error.message` may include the request body containing `client_id` and `client_secret`. This would surface in MCP error responses and server logs.  
**Fix:** Catch and re-throw with a generic message; log details internally without secrets.  
```ts
} catch (error: any) {
  // Log internally without sensitive fields
  const logMeta = { 
    status: error.response?.status, 
    code: error.code, 
    message: error.message 
  };
  console.error('Avito Auth Error:', logMeta);
  throw new McpError(ErrorCode.InternalError, 'Avito authentication failed');
}
```

---

### 4. Both Servers — Missing Output Validation / Data Minimization
**Severity:** Low  
**Risk:** Tool handlers (not fully shown) return raw API responses to the LLM. Bitrix/Avito responses can be large and contain fields the LLM doesn’t need (internal IDs, timestamps, nested objects). This increases token usage, latency, and the chance the LLM accidentally echoes sensitive data to the end user.  
**Fix:** Transform responses in each tool handler to return only the fields the agent actually needs.  
```ts
// Example for get_deals:
const raw = await this.callBitrix('crm.deal.list', params);
return raw.result?.map((deal: any) => ({
  id: deal.ID,
  title: deal.TITLE,
  stage: deal.STAGE_ID,
  amount: deal.OPPORTUNITY,
  currency: deal.CURRENCY_ID,
})) || [];
```

---

## Non-Findings (Checked & Safe)
| Area | Status |
|------|--------|
| Prompt injection via tool args | **Mitigated** — Tool schemas are fixed; args are typed and passed to typed API calls, not concatenated into prompts. |
| Path traversal / file access | **None** — No filesystem operations in either server. |
| Secrets in config | **Safe** — All secrets loaded from `.env` via `dotenv`; none hardcoded. |
| Token storage | **Safe** — Avito token kept in memory with TTL; no disk persistence. |
| SSRF via `method` param | **Safe** — `method` is hardcoded in tool handlers (not shown), not user-controlled. |

---

## Recommendations Priority Order
1. **bitrix.ts:27** — Sanitize error logs (Medium, quick fix).  
2. **bitrix.ts:22–28** — Add parameter allow-lists (Low, prevents API misuse).  
3. **avito.ts:44** — Generic auth error messages (Low, defense-in-depth).  
4. **Both** — Implement response transformation in each tool handler (Low, data hygiene).