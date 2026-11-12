import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.notifications import Notification
from tests.helpers import auth_headers


@pytest.mark.asyncio
async def test_notifications_honest_empty_state():
    headers = auth_headers("usr_clean_user")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        count_res = await ac.get("/api/v1/notifications/unread-count", headers=headers)
        assert count_res.status_code == 200
        assert count_res.json()["unread_count"] == 0

        list_res = await ac.get("/api/v1/notifications", headers=headers)
        assert list_res.status_code == 200
        assert list_res.json() == []


@pytest.mark.asyncio
async def test_notifications_lifecycle(session_factory):
    async with session_factory() as session:
        session.add_all(
            [
                Notification(
                    id="notif_1",
                    user_id="usr_fan_10",
                    type="cheer",
                    title="New Cheer",
                    message="ClockEndTactician cheered your post",
                    link="/terrace",
                    is_read=False,
                ),
                Notification(
                    id="notif_2",
                    user_id="usr_fan_10",
                    type="comment",
                    title="New Reply",
                    message="NorthBankFan replied to your tactical thread",
                    link="/terrace",
                    is_read=False,
                ),
                Notification(
                    id="notif_other",
                    user_id="usr_other_99",
                    type="cheer",
                    title="Other User Cheer",
                    message="Not for usr_fan_10",
                    link="/terrace",
                    is_read=False,
                ),
            ]
        )
        await session.commit()

    headers = auth_headers("usr_fan_10")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Fetch unread count -> strictly 2 for usr_fan_10
        count_res = await ac.get("/api/v1/notifications/unread-count", headers=headers)
        assert count_res.status_code == 200
        assert count_res.json()["unread_count"] == 2

        # 2. Fetch notifications -> only usr_fan_10's 2 rows
        list_res = await ac.get("/api/v1/notifications", headers=headers)
        assert list_res.status_code == 200
        notifs = list_res.json()
        assert len(notifs) == 2
        assert all(n["user_id"] == "usr_fan_10" for n in notifs)

        # 3. Mark single as read
        read_res = await ac.post("/api/v1/notifications/notif_1/read", headers=headers)
        assert read_res.status_code == 200

        count_after_one = await ac.get("/api/v1/notifications/unread-count", headers=headers)
        assert count_after_one.json()["unread_count"] == 1

        # 4. Mark all as read
        all_read_res = await ac.post("/api/v1/notifications/read-all", headers=headers)
        assert all_read_res.status_code == 200

        count_after_all = await ac.get("/api/v1/notifications/unread-count", headers=headers)
        assert count_after_all.json()["unread_count"] == 0
