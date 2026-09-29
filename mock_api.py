"""
Mock API for testing the Twitch Cheer Bot without a real backend.
This simulates the Django backend API responses.
"""
from datetime import datetime, timedelta
from typing import Dict, Any


class MockApi:
    """Mock API for testing purposes"""
    
    def __init__(self):
        self.donations = []
        self.disabled_users = []
        self.completed_donations = []
    
    def get_donations(self) -> Dict[str, Any]:
        """Get mock donations for testing"""
        
        # Create a donation 30 seconds from now for testing
        future_time = (datetime.now() + timedelta(seconds=30)).strftime("%H:%M:%S")
        
        mock_data = {
            "donations": [
                {
                    'id': 1,
                    'user': 'test_bot_1',
                    'admin': 'test_admin',
                    'stream_chat_link': 'https://www.twitch.tv/popout/test_streamer/chat?popout=',
                    'time': future_time,
                    'amount': 100,
                    'message': 'Test cheer from mock API',
                    'cookies': []
                }
            ]
        }
        
        print("getting donations... (MOCK MODE)")
        return mock_data
    
    def set_donation_done(self, id: int) -> str:
        """Mark donation as done (mock)"""
        self.completed_donations.append(id)
        print(f"MOCK: Donation {id} marked as done")
        return "Donation updated"
    
    def disable_user(self, name: str) -> str:
        """Disable user (mock)"""
        self.disabled_users.append(name)
        print(f"MOCK: User {name} disabled")
        return "User disabled"


# Replace the real Api with MockApi for testing
import api
api.Api = MockApi
