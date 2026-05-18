from src.app.models.search import ProviderRun, SearchRun


def test_search_run_model_creation():
    search_run = SearchRun(
        search_id="abc123",
        query="Trip to Lisbon",
        inventories=["stay"],
        request_payload={"destination": "Lisbon"},
        warnings=[],
        result_count=1,
    )
    provider_run = ProviderRun(
        provider="duffel",
        inventory_type="stay",
        configured=True,
        success=True,
        cache_hit=False,
        result_count=1,
        duration_ms=120,
    )
    search_run.provider_runs.append(provider_run)

    assert search_run.search_id == "abc123"
    assert search_run.provider_runs[0].provider == "duffel"
