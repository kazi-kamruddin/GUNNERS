import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.helpers import auth_headers


@pytest.mark.asyncio
async def test_create_conversation_and_send_messages():
    arsenal_headers = auth_headers("usr_fan_arsenal", display_name="GoonerSam")
    other_headers = auth_headers("usr_fan_rival", display_name="RivalFan")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Start conversation with initial message (sender/initiator derived from JWT)
        create_res = await ac.post(
            "/api/v1/messages/conversations",
            json={
                "recipient_id": "usr_fan_rival",
                "initiator_name": "GoonerSam",
                "initiator_club_id": "arsenal",
                "initial_message": "Good luck in the derby this Sunday!",
            },
            headers=arsenal_headers,
        )
        assert create_res.status_code == 201
        conv_data = create_res.json()
        conv_id = conv_data["id"]
        assert "usr_fan_arsenal" in conv_data["members"]
        assert "usr_fan_rival" in conv_data["members"]
        assert conv_data["last_message"] is not None
        assert conv_data["last_message"]["sender_id"] == "usr_fan_arsenal"
        assert conv_data["last_message"]["content"] == "Good luck in the derby this Sunday!"

        # 2. Existing conversation check (idempotent / returns same conversation)
        dup_res = await ac.post(
            "/api/v1/messages/conversations",
            json={
                "recipient_id": "usr_fan_arsenal",
                "initiator_name": "RivalFan",
                "initiator_club_id": "arsenal",
            },
            headers=other_headers,
        )
        assert dup_res.status_code == 201
        assert dup_res.json()["id"] == conv_id

        # 3. Send message in conversation
        msg_res = await ac.post(
            f"/api/v1/messages/conversations/{conv_id}/messages",
            json={
                "sender_id": "spoofed_sender",
                "sender_name": "RivalFan",
                "sender_club_id": "arsenal",
                "content": "Looking forward to a great tactical battle!",
            },
            headers=other_headers,
        )
        assert msg_res.status_code == 201
        msg = msg_res.json()
        assert msg["sender_id"] == "usr_fan_rival"
        assert msg["sender_name"] == "RivalFan"
        assert msg["content"] == "Looking forward to a great tactical battle!"

        # 4. Fetch message history as a member
        history_res = await ac.get(
            f"/api/v1/messages/conversations/{conv_id}/messages",
            headers=arsenal_headers,
        )
        assert history_res.status_code == 200
        messages = history_res.json()
        assert len(messages) == 2
        assert messages[0]["content"] == "Good luck in the derby this Sunday!"
        assert messages[1]["content"] == "Looking forward to a great tactical battle!"


@pytest.mark.asyncio
async def test_list_conversations_scoped_to_authenticated_user():
    alpha_headers = auth_headers("user_alpha", display_name="Alpha")
    gamma_headers = auth_headers("user_gamma", display_name="Gamma")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(
            "/api/v1/messages/conversations",
            json={
                "recipient_id": "user_beta",
                "initiator_name": "Alpha",
                "initiator_club_id": "arsenal",
                "initial_message": "Hello Beta",
            },
            headers=alpha_headers,
        )

        # List for user_alpha (no query param needed; matching user_id also allowed)
        res_a = await ac.get("/api/v1/messages/conversations", headers=alpha_headers)
        assert res_a.status_code == 200
        convs_a = res_a.json()
        assert len(convs_a) == 1
        assert "user_beta" in convs_a[0]["members"]

        # List for user_gamma with 0 conversations -> honest []
        res_g = await ac.get("/api/v1/messages/conversations", headers=gamma_headers)
        assert res_g.status_code == 200
        assert res_g.json() == []


@pytest.mark.asyncio
async def test_cannot_message_self():
    headers = auth_headers("same_user", display_name="Me")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/messages/conversations",
            json={
                "recipient_id": "same_user",
                "initiator_name": "Me",
                "initiator_club_id": "arsenal",
            },
            headers=headers,
        )
        assert res.status_code == 400
        assert "Cannot start conversation with yourself" in res.json()["detail"]
