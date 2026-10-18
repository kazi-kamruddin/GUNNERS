import argparse
import asyncio
import sys
from app.core.database import AsyncSessionLocal, engine, Base
from app.services.ingestion import FootballIngestionService

async def main():
    parser = argparse.ArgumentParser(description="GUNNERS Football Data Sync Pipeline")
    parser.add_argument("--mock", action="store_true", help="Force curated mock/baseline match data")
    parser.add_argument("--key", type=str, default=None, help="Override football-data.org API key")
    args = parser.parse_args()

    print("==================================================")
    print("   GUNNERS Football Data Synchronization Job      ")
    print("==================================================")

    # Ensure tables exist in target DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        try:
            result = await FootballIngestionService.run_sync(
                db=session,
                api_key=args.key,
                force_mock=args.mock
            )
            print("--------------------------------------------------")
            print(f"Status:         {result['status']}")
            print(f"Source:         {result['source']}")
            print(f"Matches Synced: {result['matches_synced']}")
            print(f"Duration:       {result['duration_seconds']:.2f} seconds")
            print(f"Completed At:   {result['completed_at']}")
            print("==================================================")
            print("Sync job finished successfully.")
        except Exception as exc:
            print(f"[FATAL] Football sync job failed: {exc}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
