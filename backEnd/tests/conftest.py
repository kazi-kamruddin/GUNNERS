import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

# Import all models so Base.metadata contains all 17 tables
from app.models import (  # noqa: F401
    Club,
    Competition,
    Conversation,
    ConversationMember,
    DirectMessage,
    Insight,
    Match,
    Notification,
    Player,
    Post,
    PostComment,
    PostReaction,
    Prediction,
    Profile,
    Season,
    SyncRun,
    TacticalBoard,
)
from tests.helpers import TEST_JWT_SECRET, auth_headers, make_supabase_jwt  # noqa: F401

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Ensure deterministic test configuration isolated from any local .env
settings.TESTING = True
settings.SUPABASE_JWT_SECRET = TEST_JWT_SECRET

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_test_db():
    # Restore test JWT secret in case a test monkeypatched/mutated settings
    settings.TESTING = True
    settings.SUPABASE_JWT_SECRET = TEST_JWT_SECRET

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def session_factory():
    return TestSessionLocal
