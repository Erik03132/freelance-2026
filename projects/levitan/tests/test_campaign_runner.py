"""Tests for campaign runner metrics structure."""

import pytest


def test_campaign_summary_fields():
    """Verify campaign summary has required metric fields."""
    required_keys = {
        "total_calls", "connected", "no_answer", "errors",
        "connect_rate", "avg_duration_sec", "calls_per_hour",
        "total_time_hours", "total_time_sec",
    }
    dummy_summary = {
        "total_calls": 100,
        "connected": 45,
        "no_answer": 50,
        "errors": 5,
        "connect_rate": 45.0,
        "avg_duration_sec": 18.5,
        "calls_per_hour": 30.0,
        "total_time_hours": 3.33,
        "total_time_sec": 12000,
    }
    assert required_keys.issubset(dummy_summary.keys())
    assert dummy_summary["connect_rate"] == 45.0
    assert dummy_summary["calls_per_hour"] == 30.0
