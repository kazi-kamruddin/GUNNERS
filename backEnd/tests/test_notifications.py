import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_notifications_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Fetch unread count for user
        count_res = await ac.get("/api/v1/notifications/unread-count?user_id=usr_fan_10")
        assert count_res.status_code == 200
        assert "unread_count" in count_res.json()

        # 2. Fetch notifications
        list_res = await ac.get("/api/v1/notifications?user_id=usr_fan_10")
        assert list_res.status_code == 200
        notifs = list_res.json()
        assert len(notifs) > 0
        notif_id = notifs[0]["id"]

        # 3. Mark single as read
        read_res = await ac.post(f"/api/v1/notifications/{notif_id}/read")
        assert read_res.status_code == 200

        # 4. Mark all as read
        all_read_res = await ac.post(f"/api/v1/notifications/read-all?user_id=usr_fan_10")
        assert all_read_res.status_code == 200
