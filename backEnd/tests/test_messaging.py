import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_create_conversation_and_send_messages():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Start conversation with initial message
        create_res = await ac.post("/api/v1/messages/conversations", json={
            "initiator_id": "usr_fan_arsenal",
            "recipient_id": "usr_fan_chelsea",
            "initiator_name": "GoonerSam",
            "initiator_club_id": "arsenal",
            "initial_message": "Good luck in the derby this Sunday!"
        })
        assert create_res.status_code == 201
        conv_data = create_res.json()
        conv_id = conv_data["id"]
        assert "usr_fan_arsenal" in conv_data["members"]
        assert "usr_fan_chelsea" in conv_data["members"]
        assert conv_data["last_message"] is not None
        assert conv_data["last_message"]["content"] == "Good luck in the derby this Sunday!"

        # 2. Existing conversation check (idempotent / returns same conversation)
        dup_res = await ac.post("/api/v1/messages/conversations", json={
            "initiator_id": "usr_fan_chelsea",
            "recipient_id": "usr_fan_arsenal",
            "initiator_name": "BlueLion",
            "initiator_club_id": "chelsea"
        })
        assert dup_res.status_code == 201
        assert dup_res.json()["id"] == conv_id

        # 3. Send message in conversation
        msg_res = await ac.post(f"/api/v1/messages/conversations/{conv_id}/messages", json={
            "sender_id": "usr_fan_chelsea",
            "sender_name": "BlueLion",
            "sender_club_id": "chelsea",
            "content": "Thanks mate, you'll need the luck more than us!"
        })
        assert msg_res.status_code == 201
        msg = msg_res.json()
        assert msg["sender_name"] == "BlueLion"
        assert msg["content"] == "Thanks mate, you'll need the luck more than us!"

        # 4. Fetch message history
        history_res = await ac.get(f"/api/v1/messages/conversations/{conv_id}/messages")
        assert history_res.status_code == 200
        messages = history_res.json()
        assert len(messages) == 2
        assert messages[0]["content"] == "Good luck in the derby this Sunday!"
        assert messages[1]["content"] == "Thanks mate, you'll need the luck more than us!"

@pytest.mark.asyncio
async def test_list_conversations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create a conversation
        await ac.post("/api/v1/messages/conversations", json={
            "initiator_id": "user_alpha",
            "recipient_id": "user_beta",
            "initiator_name": "Alpha",
            "initiator_club_id": "arsenal",
            "initial_message": "Hello Beta"
        })

        # List for user_alpha
        res_a = await ac.get("/api/v1/messages/conversations?user_id=user_alpha")
        assert res_a.status_code == 200
        convs_a = res_a.json()
        assert len(convs_a) >= 1
        assert any("user_beta" in c["members"] for c in convs_a)

        # List for non-existent conversation user
        res_none = await ac.get("/api/v1/messages/conversations?user_id=user_unknown_999")
        assert res_none.status_code == 200
        assert len(res_none.json()) == 0

@pytest.mark.asyncio
async def test_cannot_message_self():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/messages/conversations", json={
            "initiator_id": "same_user",
            "recipient_id": "same_user",
            "initiator_name": "Me",
            "initiator_club_id": "arsenal"
        })
        assert res.status_code == 400
        assert "Cannot start conversation with yourself" in res.json()["detail"]
