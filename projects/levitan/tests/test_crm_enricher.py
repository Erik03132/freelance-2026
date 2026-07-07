"""Tests for CRM enrichment."""

import pytest

from levitan.crm_enricher import CrmEnricher, MockCrmProvider, ContactInfo


@pytest.fixture
def enricher():
    return CrmEnricher(provider=MockCrmProvider())


@pytest.mark.asyncio
async def test_enrich_found(enricher):
    result = await enricher.enrich("+7 (918) 639-30-30")
    assert result.name == "Иван Петров"
    assert result.company == "ООО Технологии"
    assert result.position == "Директор"


@pytest.mark.asyncio
async def test_enrich_not_found(enricher):
    result = await enricher.enrich("+7 (495) 123-45-67")
    assert result.is_empty
    assert result.phone == "74951234567"


@pytest.mark.asyncio
async def test_default_provider():
    enricher = CrmEnricher()
    assert isinstance(enricher._provider, MockCrmProvider)


@pytest.mark.asyncio
async def test_empty_contact():
    c = ContactInfo()
    assert c.is_empty


@pytest.mark.asyncio
async def test_non_empty_contact():
    c = ContactInfo(name="Name")
    assert not c.is_empty
