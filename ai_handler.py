from anthropic import Anthropic
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class AIConversationHandler:
    """Handler for AI-powered natural conversations using Claude."""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Latest stable model
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}

    def get_conversation_history(self, user_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a specific user.

        Args:
            user_id: User's phone number or identifier

        Returns:
            List of conversation messages
        """
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        return self.conversation_history[user_id]

    def add_to_history(self, user_id: str, role: str, content: str):
        """Add a message to the conversation history.

        Args:
            user_id: User's phone number or identifier
            role: Message role ("user" or "assistant")
            content: Message content
        """
        history = self.get_conversation_history(user_id)
        history.append({"role": role, "content": content})

        # Keep only last 20 messages to avoid token limits
        if len(history) > 20:
            self.conversation_history[user_id] = history[-20:]

    def clear_history(self, user_id: str):
        """Clear conversation history for a user.

        Args:
            user_id: User's phone number or identifier
        """
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]

    async def process_message(
        self,
        user_message: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Process a user message and generate AI response with search intent.

        Args:
            user_message: User's message text
            user_id: User's phone number or identifier

        Returns:
            Dictionary with AI response and search parameters if applicable
        """
        try:
            # Add user message to history
            self.add_to_history(user_id, "user", user_message)

            # Build the system prompt
            system_prompt = self._build_system_prompt()

            # Get conversation history
            history = self.get_conversation_history(user_id)

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=history
            )

            # Extract response
            assistant_message = response.content[0].text

            # Add assistant response to history
            self.add_to_history(user_id, "assistant", assistant_message)

            # Parse the response to extract search intent
            result = self._parse_ai_response(assistant_message)

            logger.info(f"AI processed message from {user_id}")
            return result

        except Exception as e:
            logger.error(f"Error processing AI message: {e}")
            return {
                "response": "I'm having trouble processing your request right now. Please try again!",
                "search_needed": False
            }

    def _build_system_prompt(self) -> str:
        """Build the system prompt for Claude.

        Returns:
            System prompt string
        """
        return """You are a helpful WhatsApp assistant that helps users find great restaurants.
You have access to a restaurant search function that uses Google Places data.

Your role is to:
1. Have natural, friendly conversations with users
2. Understand their restaurant preferences (cuisine type, location, price range, etc.)
3. When you have enough information, indicate that a search should be performed
4. Present restaurant recommendations in a helpful, engaging way

When the user asks about restaurants or you have enough information to search, respond with your message followed by a special marker:

SEARCH_PARAMS: {"query": "cuisine/restaurant type", "location": "city or area if provided"}

For example:
- User: "I want Italian food in Manhattan"
  You: "Great choice! Let me find some excellent Italian restaurants in Manhattan for you!"
  SEARCH_PARAMS: {"query": "Italian restaurant Manhattan", "location": "Manhattan, NY"}

- User: "Any good sushi places nearby?"
  You: "I'd love to help you find great sushi! Could you tell me what area or city you're in?"

- User: "I'm in Brooklyn"
  You: "Perfect! Let me search for the best sushi spots in Brooklyn for you!"
  SEARCH_PARAMS: {"query": "sushi restaurant Brooklyn", "location": "Brooklyn, NY"}

Keep your responses conversational, warm, and helpful. If you need more information (like location), ask naturally.
Don't include the SEARCH_PARAMS marker unless you have enough information to perform a meaningful search."""

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response to extract search parameters.

        Args:
            response: Raw AI response text

        Returns:
            Dictionary with parsed response and search parameters
        """
        result = {
            "response": response,
            "search_needed": False,
            "search_params": {}
        }

        # Check if response contains search parameters
        if "SEARCH_PARAMS:" in response:
            parts = response.split("SEARCH_PARAMS:")
            result["response"] = parts[0].strip()

            try:
                # Extract JSON from the search params
                json_str = parts[1].strip()
                search_params = json.loads(json_str)
                result["search_needed"] = True
                result["search_params"] = search_params
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse search parameters: {e}")

        return result

    def format_response_with_restaurants(
        self,
        initial_response: str,
        restaurant_message: str
    ) -> str:
        """Combine AI response with restaurant recommendations.

        Args:
            initial_response: Initial AI response
            restaurant_message: Formatted restaurant recommendations

        Returns:
            Combined message
        """
        return f"{initial_response}\n\n{restaurant_message}"
