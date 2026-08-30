---
name: nous-inference-api
description: "Nous inference API: real Hermes IDs, pricing, first call."
---

# Nous Research Inference API

The OpenAI-compatible inference backend behind Hermes Agent (the user sometimes
calls it "Ромес Агент" — that is Nova/Hermes transliteration; it is Nous Research).
You can call the same models directly from your own scripts, agents, or curl.

## Base facts (verified against live /v1/models + portal docs, 2026-08-19)

- **Base URL:** `https://inference-api.nousresearch.com/v1` — fully OpenAI-compatible.
  Use the OpenAI SDK and just swap `base_url` + `api_key`.
- **Live model count:** ~370 models (Hermes 4 family + Anthropic, OpenAI, Google,
  DeepSeek, Qwen, xAI, Z.ai/GLM, etc.). NOT only the 3 listed in the /api-docs page.
- **Auth:** Bearer token. Get key at `portal.nousresearch.com` → Settings → API Keys.
  Store in `NOUS_API_KEY` env var. NEVER print the raw key in chat or commit it.
- **Rate limits (default paid user):** 180 RPM, 720,000 TPM.
  Tiers: Free 50/500k, Plus 400/4M, Super 800/8M, Ultra 1600/16M.
- **Request params (from OpenAPI spec):** `model`, `messages`/`prompt` (required);
  `temperature` 0–2 (default 1), `max_tokens` 1–32000, `stream` bool.

## CRITICAL: real model IDs mismatch the docs

The /api-docs page lists `Hermes-4-70B`, `Hermes-4-405B`, `Hermes-4.3-36B`.
**Those strings 404 on the live API.** The REAL ids (from `/v1/models`) are:

- `nousresearch/hermes-4-70b`  (128k ctx) — prompt $0.05 / completion $0.20 per 1M tok
- `nousresearch/hermes-4-405b` (128k ctx) — prompt $0.09 / completion $0.37 per 1M tok

Hermes 4 is extremely cheap vs frontier (Claude/GPT are $1.6-12 per 1M). Use 70B
for ~90% of work; 405B for max reasoning/architecture. Confirm exact ids by
calling `GET /v1/models` (filter for `"hermes"` in id/name) before hardcoding.

Other cheap/free picks seen live: `meituan/longcat-2.0:free`, `upstage/solar-pro4`
(free), `z-ai/glm-latest`, `google/gemini-3.7-flash`, `moonshotai/kimi-k3`.

## Reasoning behavior (Hermes 4 / DeepHermes)

- Enable with system prompt: "You are a deep thinking AI, you may use extremely
  long chains of thought... enclose your thoughts inside <think></think> tags..."
- Output location depends on call style:
  - Hermes 4 + reasoning system prompt, NO prefill -> reasoning in `reasoning_content` field.
  - Hermes 4 + prefill `<think>` in assistant response -> reasoning between `<think></think>` in content.
- Use the `reasoning`/`reasoning_effort` params where supported, else the system prompt.

## First-request checklist (what to tell a brand-new payer)

1. Get API key from portal, put in `NOUS_API_KEY` (not in chat/git).
2. Smoke test with curl (see templates/first_request.sh).
3. For Python, OpenAI SDK with base_url swap (see templates/first_request.py).
4. Start on free/cheap models; only spend credits when needed.
5. Always set `max_tokens` explicitly.

## Payment options

- **Option 1 - API key + account credits (default, recommended).** Bearer token.
- **Option 2 - x402 (beta).** Solana USDC, no account needed, pay-per-request,
  on-chain. You get a `402` with payment requirements, sign via x402 client lib,
  resend with `X-PAYMENT` header. **CAUTION:** x402 requires the price BEFORE
  execution, so you are charged for `max_tokens` (or a high default) REGARDLESS
  of actual usage. ALWAYS set `max_tokens` explicitly with x402, and expect a
  small surcharge vs key-based billing.

## Gotchas

- Docs page is a partial summary - `GET /v1/models` is the source of truth for
  ids and live prices.
- `max_tokens` upper bound is 32000 (spec); per-model `max_completion_tokens`
  may be lower.
- Reasoning output may NOT be in `content` - check `reasoning_content`.
- Cloudflare Turnstile wraps portal.nousresearch.com pages in a browser; the
  API itself is clean JSON, no challenge.

See `references/live_model_data.md` for the raw verified model/id/pricing excerpts.
See `templates/first_request.sh` and `templates/first_request.py` for copy-ready starters.
