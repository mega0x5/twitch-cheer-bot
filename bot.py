import sys
import asyncio
import logging
from datetime import datetime
from random import randint
from typing import Optional, List, Dict

from api import Api
from browser import BrowserWrapper
from credentials import PORT, DEBUG_USERS_LIST, DEBUG_MODE, CHROME_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Bot:
    
    def __init__(self):
        """Start async tasks to send donations to twitch chat"""
         
        # variables
        self.api = Api()
        self.selectors = {
            'twitch_login_input': '#login-username',
            'comment_textarea': '[data-a-target="chat-input"]',
            'comment_send_btn': 'button[data-a-target="chat-send-button"]',
            'comment_accept_buttons': [
                'button[data-test-selector="chat-rules-ok-button"]',
                'button[data-test-selector="chat-rules-show-intro-button"]',
            ],
            'comment_warning_before': '[data-test-selector="chat-rules-ok-button"]',
            'comment_warning_after': '[data-test-selector="full-error"], [data-test-selector="inline-error"]',
        }
        self.running = False
        self.error = False
        
    async def run(self):
        """Main async entry point"""
        # Get data from api
        data = self.api.get_donations()
        donations = data["donations"]
        logger.info("Starting bot...")
        
        if not donations:
            logger.info("No donations to send")
            return None
        
        # Submit each donation as async task
        tasks = []
        for donation in donations:
            
            if DEBUG_USERS_LIST and donation["user"] not in DEBUG_USERS_LIST:
                continue
            
            # Format data
            id = donation["id"]
            user = donation["user"]
            stream_chat_link = donation["stream_chat_link"]
            time = donation["time"]
            message = donation["message"]
            amount = donation["amount"]
            
            # Get streamer name
            streamer = stream_chat_link.split("/")[4]
            
            # Show donation data       
            logger.info(f"bot: '{user}', time: {time}, streamer: '{streamer}', message: '{message}', amount: {amount} (ID: {donation['id']})")
            
            # Submit donation as async task
            task = asyncio.create_task(
                self.submit_donation(id, stream_chat_link, user, time, message, amount)
            )
            tasks.append(task)
            
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        # Raise error when end
        if self.error:
            sys.exit(1)
        
    def __show_message__(self, message: str, id: int = 0, is_error: bool = False):
        """Log message

        Args:
            id (int): id of the donation
            message (str): error text
            is_error (bool, optional): if the message is an error. Defaults to False.
        """
        
        if is_error:
            self.error = True
            logger.error(f"Donation {id}: {message}" if id != 0 else message)
        else:
            logger.info(f"Donation {id}: {message}" if id != 0 else message)
        
    async def __login__(self, id: int, user: str, scraper: BrowserWrapper) -> bool:
        """Validate login in twitch

        Args:
            id (int): donation id
            user (str): bot name
            scraper (BrowserWrapper): browser wrapper instance

        Returns:
            bool: True if the login was successful
        """
        
        logged = True
        
        # Validate login
        await scraper.set_page("https://www.twitch.tv/login")    
        login_input_visible = await scraper.count_elems(self.selectors["twitch_login_input"])
        if login_input_visible:
            
            # Show error and update status
            self.__show_message__(f"login error, bot: {user}", id, is_error=True)
            logged = False
            
            # Disable user
            response = self.api.disable_user(user)
            if response != "User disabled":
                self.__show_message__(f"bot {user} not disabled", id, is_error=True)
                                       
        return logged 
    
    async def __validate_inputs__(self, id: int, scraper: BrowserWrapper) -> bool:
        """Validate if inputs are visible and available

        Args:
            id (int): donation id
            scraper (BrowserWrapper): browser wrapper instance

        Returns:
            bool: True if inputs are visible and available
        """
        
        inputs_valid = True
        
        # Validate if controls are visible
        comment_textarea_visible = await scraper.count_elems(self.selectors["comment_textarea"])
        comment_send_btn_visible = await scraper.count_elems(self.selectors["comment_send_btn"])
        if not comment_textarea_visible or not comment_send_btn_visible:
            self.__show_message__("inputs not visible", id, is_error=True)
            inputs_valid = False
            
        # Validate error messages
        warning_text = await scraper.get_text(self.selectors["comment_warning_before"])
        if warning_text:
            self.__show_message__(f"Inputs not available: {warning_text}", id, is_error=True)
            inputs_valid = False
            
        return inputs_valid
    
    async def __validate_submit__(self, id: int, scraper: BrowserWrapper) -> bool:
        """Validate if donation was sent

        Args:
            id (int): donation id
            scraper (BrowserWrapper): browser wrapper instance
            
        Returns:
            bool: True if donation was sent
        """
        
        donation_sent = True
        
        warning_text = await scraper.get_text(self.selectors["comment_warning_after"])
        if warning_text:
            self.__show_message__(f"Donation not sent: {warning_text}", id, is_error=True)
            donation_sent = False
            
        return donation_sent
        
    async def submit_donation(self, id: int, stream_chat_link: str, user: str,
                             time_str: str, message: str, amount: int):
        """Send donation to twitch chat

        Args:
            id (int): donation id
            stream_chat_link (str): link to the chat of the stream
            user (str): bot name
            time_str (str): time text in format "hh:mm:ss"
            message (str): message to send
            amount (int): bits of the donation
        """
        
        # Wait random seconds
        await asyncio.sleep(randint(0, 15))
                
        # Donation time
        donation_time = datetime.strptime(time_str, "%H:%M:%S")
        now = datetime.now()
        donation_time = donation_time.replace(year=now.year, month=now.month, day=now.day)
        
        # Validate lost donation times
        if now > donation_time:
            self.__show_message__("time lost", id, is_error=True)
            self.running = False
            return None
                
        # Wait until donation time
        while donation_time > now:
            await asyncio.sleep(15)
            now = datetime.now()
            
        # Update status or wait until other donations are sent
        if not self.running: 
            self.running = True
        else:
            while self.running:
                await asyncio.sleep(randint(0, 5))
        
        # Show start donation status 
        self.__show_message__("starting...", id)
        
        # Connect to browser
        scraper = BrowserWrapper(
            chrome_path=CHROME_PATH,
            port=PORT
        )
        await scraper.connect()
        
        # Login in twitch and validate
        logged = await self.__login__(id, user, scraper)
        if not logged:
            self.running = False
            await scraper.close()
            return None
                    
        # Go to chat page
        await scraper.set_page(stream_chat_link)
        await asyncio.sleep(10)
        
        # Validate inputs
        inputs_valid = await self.__validate_inputs__(id, scraper)
        if not inputs_valid:
            self.running = False
            await scraper.close()
            return None
        
        # Write message
        donation_text = f"cheer{amount} {message}"
        await scraper.send_data(self.selectors["comment_textarea"], donation_text)
        await asyncio.sleep(5)
        
        # Click in accept buttons
        for selector in self.selectors["comment_accept_buttons"]:
            
            accept_elem = await scraper.count_elems(selector)
            if accept_elem:
                await scraper.click(selector)
                
                # Write message (again)
                donation_text = f"cheer{amount} {message}"
                await scraper.send_data(self.selectors["comment_textarea"], donation_text)
                
        # Submit donation
        if not DEBUG_MODE:
            await scraper.click(self.selectors["comment_send_btn"])
        
        donation_sent = await self.__validate_submit__(id, scraper)
        if donation_sent:
            self.__show_message__("sent", id)
        
        self.running = False
        await scraper.close()
        
        # Update donation status
        if not DEBUG_MODE:
            response = self.api.set_donation_done(id) 
            if response != "Donation updated":
                self.__show_message__("not updated", id, is_error=True)

if __name__ == "__main__":
    bot = Bot()
    asyncio.run(bot.run())