"""Smoke tests for call_session module (data model only, no external deps)."""

import pydantic
import pytest
from datetime import datetime
from levitan.call_session import TranscriptEntry


def test_transcript_entry_creation():
    entry = TranscriptEntry(role="agent", text="Здравствуйте!")
    assert entry.role == "agent"
    assert entry.text == "Здравствуйте!"
    assert isinstance(entry.timestamp, datetime)


def test_transcript_entry_client_role():
    entry = TranscriptEntry(role="client", text="Алло")
    assert entry.role == "client"
    assert entry.text == "Алло"


def test_transcript_entry_default_timestamp():
    entry1 = TranscriptEntry(role="agent", text="test1")
    entry2 = TranscriptEntry(role="agent", text="test2")
    assert entry2.timestamp >= entry1.timestamp


def test_transcript_entry_immutable():
    entry = TranscriptEntry(role="agent", text="test")
    assert entry.text == "test"
