# Live Nous Inference API model data (verified 2026-08-19)

Source: `GET https://inference-api.nousresearch.com/v1/models` (370 entries) +
`https://portal.nousresearch.com/info` + `/api/openapi` spec.

## Hermes 4 family — exact IDs that work on the API

```json
{
  "id": "nousresearch/hermes-4-70b",
  "context_length": 131072,
  "pricing": {"prompt": "0.0000000500", "completion": "0.0000002000"},
  // => $0.05 / $0.20 per 1M tokens
  "description": "Hermes 4 70B is a hybrid reasoning model from Nous Research,
                  built on Meta-Llama-3.1-70B."
}
{
  "id": "nousresearch/hermes-4-405b",
  "context_length": 131072,
  "pricing": {"prompt": "0.0000000900", "completion": "0.0000003700"},
  // => $0.09 / $0.37 per 1M tokens
  "description": "Hermes 4 is a large-scale reasoning model built on
                  Meta-Llama-3.1-405B and released by Nous Research."
}
```

WARNING: Docs page lists `Hermes-4-70B` / `Hermes-4-405B` — those 404. Use the
`nousresearch/`-prefixed ids above.

## Other models seen live (cheap / free for testing)

| id | ctx | notes |
|----|-----|-------|
| `meituan/longcat-2.0:free` | 1M | free, text |
| `upstage/solar-pro4` | — | free tier seen |
| `z-ai/glm-latest` -> `z-ai/glm-5.3` | 1M | prompt $0.00112 / comp $0.00352 per 1M, reasoning mandatory |
| `google/gemini-3.7-flash` | 1M | multimodal, prompt $0.0003 / comp $0.0015 per 1M |
| `moonshotai/kimi-k3` | 1M | 2.8T params, vision, prompt $0.0024 / comp $0.012 per 1M |
| `x-ai/grok-4.6` | 500k | prompt $0.0016 / comp $0.0048 per 1M |

Prices are USD per token in the `pricing` object; multiply by 1,000,000 for /1M.

## OpenAPI request schema (chat/completions)

```
required: model (str), messages[] {role: system|user|assistant, content: str}
optional: temperature 0.0-2.0 (def 1), max_tokens 1-32000 (def 100),
          stream bool (def false)
response 200: { id, object:"chat.completion", created, model,
                choices[{index, message:{role,content}, finish_reason}] }
auth: Bearer <API_KEY>  (securitySchemes.BearerAuth, type http, scheme bearer)
```

## Portal pricing reference (non-model tooling, from /info)

- Hermes Cloud instances: Small $0.29/day running, Medium $0.56/day, Large $1.09/day
  (Stopped $0.03/day storage). Billed daily from credit, excludes inference.
- browser-use: $0.0011/min session, $4.20/GB proxy bandwidth.
- Firecrawl: $0.0005/credit. Whisper: $0.0063/min audio.
- x402 has a small surcharge over key-based billing.
