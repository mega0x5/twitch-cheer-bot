import os
import requests
from typing import Dict, Any, Optional
from credentials import API_HOST, TOKEN


class Api:

    def __requests_url__(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> requests.Response:
        """Request data from specific endpoint and quit if error happens

        Args:
            endpoint (str): endpoint to request, like "donations" or "update-donation/1"
            params (Optional[Dict[str, str]]): additional query parameters

        Returns:
            requests.Response: response of requests to the endpoint
        """

        # Request data to specific url with Authorization header (safer than query param)
        url = f"{API_HOST}/{endpoint}/"
        headers = {"Authorization": f"Token {TOKEN}"}
        
        # Add any additional params
        if params:
            response = requests.get(url, headers=headers, params=params)
        else:
            response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response
        else:
            print(f"Error requesting data from API. Status: {response.status_code}")
            print(f"Response: {response.text}")
            quit()

    def get_donations(self) -> Dict[str, Any]:
        """Get pending donations for active bots from the API

        Returns:
            dict: donations data.

            Example:
            {
                "success": True,
                "count": 1,
                "donations": [
                    {
                        'id': 20,
                        'user': 'soyunfarsantee', 
                        'stream_chat_link': 'https://www.twitch.tv/popout/blue_rebel_/chat?popout=', 
                        'time': '00:21:51', 
                        'amount': 1, 
                        'message': 'Holaaaaa', 
                        'cookies': [...] 
                    }
                    ...
                ]
            }
        """

        print("getting donations...")

        # Get data from api
        res = self.__requests_url__("donations")
        data = res.json()
        
        # Handle new response format
        if data.get("success"):
            return data
        else:
            print(f"API returned error: {data.get('error', 'Unknown error')}")
            quit()
    
    def set_donation_done(self, id: int) -> bool:
        """Set status donation to done

        Args:
            id (int): donation id
            
        Returns:
            bool: True if successful
        """
        
        endpoint = f"update-donation/{id}"
        res = self.__requests_url__(endpoint)
        data = res.json()
        
        if data.get("success"):
            print(f"Donation {id} marked as done")
            return True
        else:
            print(f"Failed to mark donation {id} as done: {data.get('error', 'Unknown error')}")
            return False
    
    def disable_user(self, name: str, reason: str = "Disabled by bot") -> bool:
        """Disable user / bot when cookies are not valid

        Args:
            name (str): bot name
            reason (str): reason for disabling
        
        Returns:
            bool: True if successful
        """
        
        endpoint = f"disable-user/{name}"
        params = {"reason": reason}
        res = self.__requests_url__(endpoint, params=params)
        data = res.json()
        
        if data.get("success"):
            print(f"User {name} disabled: {data.get('disabled_reason', reason)}")
            return True
        else:
            print(f"Failed to disable user {name}: {data.get('error', 'Unknown error')}")
            return False  
    
        
if __name__ == "__main__":
    api = Api()
    data = api.get_donations ()
    print (data)