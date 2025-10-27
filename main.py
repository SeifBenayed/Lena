from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import PlainTextResponse
import logging
from contextlib import asynccontextmanager

from config import get_settings
from whatsapp_handler import WhatsAppHandler
from serpapi_handler import RestaurantSearchHandler
from ai_handler import AIConversationHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global handlers
whatsapp_handler: WhatsAppHandler = None
restaurant_handler: RestaurantSearchHandler = None
ai_handler: AIConversationHandler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize handlers on startup."""
    global whatsapp_handler, restaurant_handler, ai_handler

    settings = get_settings()

    # Initialize handlers
    whatsapp_handler = WhatsAppHandler(
        phone_number_id=settings.whatsapp_phone_number_id,
        access_token=settings.whatsapp_access_token
    )

    restaurant_handler = RestaurantSearchHandler(
        api_key=settings.serpapi_api_key
    )

    ai_handler = AIConversationHandler(
        api_key=settings.anthropic_api_key
    )

    logger.info("Application started successfully!")
    yield
    logger.info("Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title="WhatsApp Restaurant Assistant",
    description="AI-powered WhatsApp bot for restaurant recommendations",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "WhatsApp Restaurant Assistant",
        "version": "1.0.0"
    }


@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verify webhook for WhatsApp Business API.

    WhatsApp will send a GET request to verify the webhook URL.
    """
    settings = get_settings()

    # Extract query parameters
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    # Verify the token and mode
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("Webhook verified successfully!")
        return PlainTextResponse(content=challenge, status_code=200)
    else:
        logger.warning("Webhook verification failed!")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verification token mismatch"
        )


@app.post("/webhook")
async def handle_webhook(request: Request):
    """Handle incoming WhatsApp messages.

    This endpoint receives webhook events from WhatsApp Business API.
    """
    try:
        # Parse incoming webhook data
        data = await request.json()
        logger.info(f"Received webhook: {data}")

        # Parse the message
        parsed_message = whatsapp_handler.parse_webhook_message(data)

        if not parsed_message:
            logger.info("No message to process")
            return {"status": "ok"}

        sender = parsed_message["sender"]
        message_text = parsed_message["message_text"]
        message_id = parsed_message["message_id"]

        if not message_text:
            logger.info("Empty message text")
            return {"status": "ok"}

        # Mark message as read
        await whatsapp_handler.mark_as_read(message_id)

        # Process message with AI
        ai_result = await ai_handler.process_message(message_text, sender)

        # Check if we need to search for restaurants
        if ai_result["search_needed"]:
            search_params = ai_result["search_params"]
            query = search_params.get("query", "")
            location = search_params.get("location", "")

            # Search for restaurants
            restaurants = restaurant_handler.search_restaurants(
                query=query,
                location=location,
                max_results=5
            )

            # Format restaurant recommendations
            restaurant_message = restaurant_handler.format_restaurant_message(restaurants)

            # Combine AI response with restaurant recommendations
            final_message = ai_handler.format_response_with_restaurants(
                ai_result["response"],
                restaurant_message
            )

            # Send the message
            await whatsapp_handler.send_message(sender, final_message)

            # If we have restaurants with coordinates, send the first one as a location
            if restaurants and restaurants[0].get("latitude") and restaurants[0].get("longitude"):
                first_restaurant = restaurants[0]
                await whatsapp_handler.send_location(
                    to=sender,
                    latitude=first_restaurant["latitude"],
                    longitude=first_restaurant["longitude"],
                    name=first_restaurant["name"],
                    address=first_restaurant["address"]
                )
        else:
            # Just send the AI response
            await whatsapp_handler.send_message(sender, ai_result["response"])

        logger.info(f"Successfully processed message from {sender}")
        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
        # Return 200 to avoid WhatsApp retrying
        return {"status": "error", "message": str(e)}


@app.post("/reset-conversation/{phone_number}")
async def reset_conversation(phone_number: str):
    """Reset conversation history for a user.

    Args:
        phone_number: User's phone number

    Returns:
        Status message
    """
    try:
        ai_handler.clear_history(phone_number)
        return {
            "status": "success",
            "message": f"Conversation history cleared for {phone_number}"
        }
    except Exception as e:
        logger.error(f"Error resetting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
