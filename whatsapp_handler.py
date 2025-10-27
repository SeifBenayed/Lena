import httpx
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class WhatsAppHandler:
    """Handler for WhatsApp Business API interactions."""

    def __init__(self, phone_number_id: str, access_token: str):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    async def send_message(self, to: str, message: str) -> Dict[str, Any]:
        """Send a text message to a WhatsApp user.

        Args:
            to: Recipient's phone number
            message: Text message to send

        Returns:
            API response dictionary
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Message sent successfully to {to}")
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to send message: {e}")
            raise

    async def send_location(self, to: str, latitude: float, longitude: float,
                           name: str, address: str) -> Dict[str, Any]:
        """Send a location message to a WhatsApp user.

        Args:
            to: Recipient's phone number
            latitude: Location latitude
            longitude: Location longitude
            name: Location name
            address: Location address

        Returns:
            API response dictionary
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "location",
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "name": name,
                "address": address
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Location sent successfully to {to}")
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to send location: {e}")
            raise

    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as read.

        Args:
            message_id: ID of the message to mark as read

        Returns:
            API response dictionary
        """
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to mark message as read: {e}")
            raise

    @staticmethod
    def parse_webhook_message(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse incoming webhook message data.

        Args:
            data: Webhook payload from WhatsApp

        Returns:
            Parsed message data with sender, message text, etc.
        """
        try:
            entry = data["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]

            if "messages" not in value:
                return {}

            message = value["messages"][0]
            sender = message["from"]
            message_id = message["id"]

            # Extract message text
            message_text = ""
            if message["type"] == "text":
                message_text = message["text"]["body"]

            return {
                "sender": sender,
                "message_id": message_id,
                "message_text": message_text,
                "timestamp": message.get("timestamp", "")
            }
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse webhook message: {e}")
            return {}
