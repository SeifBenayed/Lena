from serpapi import Client
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RestaurantSearchHandler:
    """Handler for restaurant search using SerpAPI Google Places."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = Client(api_key=api_key)

    def search_restaurants(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for restaurants using Google Places via SerpAPI.

        Args:
            query: Search query (e.g., "italian restaurant", "sushi near me")
            location: Location string (e.g., "New York, NY")
            max_results: Maximum number of results to return

        Returns:
            List of restaurant dictionaries with parsed information
        """
        try:
            # Build search parameters
            search_params = {
                "engine": "google_maps",
                "q": query,
                "type": "search"
            }

            if location:
                search_params["ll"] = f"@{location}"

            # Execute search using the new Client API
            results = self.client.search(search_params)

            # Parse and format results
            restaurants = []
            local_results = results.get("local_results", [])

            for result in local_results[:max_results]:
                restaurant = self._parse_restaurant(result)
                if restaurant:
                    restaurants.append(restaurant)

            logger.info(f"Found {len(restaurants)} restaurants for query: {query}")
            return restaurants

        except Exception as e:
            logger.error(f"Error searching restaurants: {e}")
            return []

    def _parse_restaurant(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a single restaurant result from SerpAPI.

        Args:
            result: Raw result from SerpAPI

        Returns:
            Parsed restaurant dictionary or None if parsing fails
        """
        try:
            restaurant = {
                "name": result.get("title", "Unknown"),
                "address": result.get("address", "Address not available"),
                "rating": result.get("rating", "N/A"),
                "reviews": result.get("reviews", 0),
                "type": result.get("type", "Restaurant"),
                "phone": result.get("phone", "N/A"),
                "hours": result.get("hours", "Hours not available"),
                "price": result.get("price", "N/A"),
            }

            # Extract coordinates if available
            gps_coordinates = result.get("gps_coordinates", {})
            if gps_coordinates:
                restaurant["latitude"] = gps_coordinates.get("latitude")
                restaurant["longitude"] = gps_coordinates.get("longitude")

            # Extract additional information
            if "description" in result:
                restaurant["description"] = result["description"]

            return restaurant

        except Exception as e:
            logger.error(f"Error parsing restaurant result: {e}")
            return None

    def format_restaurant_message(self, restaurants: List[Dict[str, Any]]) -> str:
        """Format restaurant list into a user-friendly message.

        Args:
            restaurants: List of restaurant dictionaries

        Returns:
            Formatted message string
        """
        if not restaurants:
            return "I couldn't find any restaurants matching your criteria. Try adjusting your search!"

        message_parts = ["Here are some great restaurant recommendations:\n"]

        for idx, restaurant in enumerate(restaurants, 1):
            message_parts.append(f"\n{idx}. *{restaurant['name']}*")

            if restaurant['rating'] != "N/A":
                message_parts.append(f"   ⭐ {restaurant['rating']} ({restaurant['reviews']} reviews)")

            if restaurant['type']:
                message_parts.append(f"   📍 {restaurant['type']}")

            if restaurant['price'] != "N/A":
                message_parts.append(f"   💰 {restaurant['price']}")

            if restaurant['address']:
                message_parts.append(f"   📌 {restaurant['address']}")

            if restaurant['phone'] != "N/A":
                message_parts.append(f"   📞 {restaurant['phone']}")

            if restaurant.get('description'):
                message_parts.append(f"   ℹ️ {restaurant['description']}")

        return "\n".join(message_parts)
