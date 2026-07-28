# Eval-Testing Skill

## When to Use
Use when you need to create, run, or maintain eval suites for AI-powered projects. Mandatory per AGENTS.md item #9: every AI project must have an eval suite.

## Core Concept
Eval-driven development = tests that verify AI/LLM behavior, not just code correctness. Think: "does the router correctly classify this query?" or "does the RAG retrieve the right context?"

## Eval Suite Structure

```
tests/eval_<project>.py    # Main eval file
tests/eval_fixtures.json   # Test data (optional)
tests/eval_report.md       # Generated report (optional)
```

## Eval Categories

### 1. Router Regression
Verify intent classification stays stable after prompt changes.
```python
def test_router_intent_classification():
    cases = [
        ("сколько стоит корм", "pricing"),
        ("какие породы есть", "breeds"),
        ("где находится магазин", "location"),
    ]
    for query, expected_intent in cases:
        result = route_query(query)
        assert result == expected_intent, f"'{query}' -> {result}, expected {expected_intent}"
```

### 2. Capability Tests
Verify the system can handle required domains.
```python
def test_handles_russian_input():
    result = agent_respond("Привет, хочу купить корм для котов")
    assert result is not None
    assert len(result) > 10
```

### 3. Accuracy Tests
Verify specific inputs produce correct outputs.
```python
def test_faq_accuracy():
    cases = [
        ("цена", "pricing_answer"),
        ("доставка", "delivery_answer"),
    ]
    for query, expected_key in cases:
        answer = get_faq_answer(query)
        assert expected_key in answer.lower()
```

### 4. Edge Cases
Verify graceful handling of unusual inputs.
```python
def test_empty_input():
    result = agent_respond("")
    assert result is not None  # should not crash

def test_long_input():
    result = agent_respond("x" * 10000)
    assert result is not None
```

### 5. Regression Tests
Capture bugs as tests to prevent recurrence.
```python
def test_bug_123_router_misclassify():
    """Bug: 'опрос' was classified as 'survey' instead of 'pro'."""
    result = route_query("опрос")
    assert result == "pro"
```

## Running Evals

### Manual
```bash
cd tests/
python3 -m pytest eval_<project>.py -v
```

### Pre-commit Hook
```bash
# Install:
cp tests/eval_precommit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### CI Integration
```yaml
# .github/workflows/eval.yml
- name: Run evals
  run: cd tests && python3 -m pytest eval_*.py -v
```

## Eval-Driven Development Workflow

1. **Before changing prompts/models/core:** Run eval suite → note baseline
2. **Make the change**
3. **Run eval suite again:** All tests must pass
4. **If regression detected:** Fix before committing (AGENTS.md: mandatory scaffold update)
5. **Log in self_improve_log.md:** `signal → update target → change → result`

## LLM-as-Judge (Advanced)

For subjective quality evaluation, use a second LLM as judge:
```python
def test_response_quality():
    response = agent_respond("расскажи о доставке")
    judge_prompt = f"""Rate this response on a scale of 1-5:
    Response: {response}
    Criteria: accuracy, completeness, tone
    Return only the number."""
    score = call_llm(judge_prompt, complexity="simple")
    assert int(score) >= 3
```

## Template: New Project Eval

```python
"""Eval suite for <PROJECT_NAME>."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 1. Router regression
# 2. Capability
# 3. Accuracy
# 4. Edge cases
# 5. Regression (add as bugs are found)
```

## Anti-Patterns
- Testing implementation details instead of behavior
- Hardcoded test data that doesn't reflect real usage
- Running evals only after changes (run before too for baseline)
- Ignoring flaky tests (fix or remove)
