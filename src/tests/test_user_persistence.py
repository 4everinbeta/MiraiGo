import pytest
from src.app.models.user import User
from src.app.models.user_session import SearchHistory, UserPreference
from src.app.services.search import SearchService
from src.app.schemas.search import SearchRequest, InventoryType, TravelerCounts, SearchDateRange


def test_user_session_models_persistence(db_session):
    # 1. Create a user
    user = User(
        full_name="Alice Explorer",
        email="alice@miraigo.com",
        hashed_password="hashed_secure_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None

    # 2. Add search history for the user
    history1 = SearchHistory(
        user_id=user.id,
        search_id="test-uuid-1",
        query="Flight from London to Kyoto"
    )
    history2 = SearchHistory(
        user_id=user.id,
        search_id="test-uuid-2",
        query="Best hotels in Tokyo"
    )
    db_session.add(history1)
    db_session.add(history2)
    db_session.commit()

    # 3. Add user preferences
    pref = UserPreference(
        user_id=user.id,
        default_origin="LHR",
        preferred_inventory=["flight", "stay"],
        currency="GBP"
    )
    db_session.add(pref)
    db_session.commit()

    # Refresh and assert relationships
    db_session.refresh(user)
    assert len(user.search_histories) == 2
    assert user.search_histories[0].query == "Flight from London to Kyoto"
    assert user.preference is not None
    assert user.preference.default_origin == "LHR"
    assert user.preference.currency == "GBP"

    # Test cascade delete
    db_session.delete(user)
    db_session.commit()

    # Verify cascades
    assert db_session.query(SearchHistory).filter(SearchHistory.user_id == user.id).count() == 0
    assert db_session.query(UserPreference).filter(UserPreference.user_id == user.id).count() == 0


@pytest.mark.asyncio
async def test_search_service_persists_user_telemetry(db_session, monkeypatch):
    # Setup user
    user = User(
        full_name="Bob Voyager",
        email="bob@miraigo.com",
        hashed_password="bob_secure_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    service = SearchService()

    # Search with user_id context
    request = SearchRequest(
        user_id=user.id,
        query="Stays in Kyoto",
        destination="Kyoto",
        origin="Denver",
        inventory=[InventoryType.STAY],
        travelers=TravelerCounts(adults=2),
        currency_code="USD"
    )

    response = await service.search(request, db=db_session)

    # Check search history persisted
    history = db_session.query(SearchHistory).filter(SearchHistory.user_id == user.id).first()
    assert history is not None
    assert history.search_id == response.search_id
    assert "Kyoto" in history.query

    # Check user preferences persisted/upserted
    pref = db_session.query(UserPreference).filter(UserPreference.user_id == user.id).first()
    assert pref is not None
    assert pref.default_origin == "Denver"
    assert pref.currency == "USD"
    assert "stay" in pref.preferred_inventory
