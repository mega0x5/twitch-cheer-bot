"""
Test script to verify the bot works with mock API.
Run this to test the Playwright automation without real donations.
"""
import sys
import asyncio

# Import mock API to replace real API
import mock_api

# Now import bot (which will use the mocked Api class)
from bot import Bot


async def test_bot():
    """Test the bot with mock data"""
    print("=" * 50)
    print("TESTING BOT WITH MOCK API")
    print("=" * 50)
    print("\nThis will:")
    print("1. Use mock donation data (no real API needed)")
    print("2. Launch Playwright browser")
    print("3. Navigate to Twitch (in DEBUG mode, won't actually cheer)")
    print("4. Verify the automation flow works")
    print("\nPress Ctrl+C to cancel at any time")
    print("=" * 50)
    print()
    
    # Set DEBUG mode to avoid actual donations
    import credentials
    credentials.DEBUG_MODE = True
    
    bot = Bot()
    await bot.run()
    
    print("\n" + "=" * 50)
    print("TEST COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    try:
        asyncio.run(test_bot())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
