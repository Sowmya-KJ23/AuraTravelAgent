from mcp.server.fastmcp import FastMCP

# Create FastMCP server
mcp = FastMCP("AuraTravelMockAPI")

# Simulated database of seasonal recommendations and weather
WEATHER_DATA = {
    "tokyo": {
        "spring": "Mild and pleasant, 15-20°C. Famous for cherry blossoms (Sakura) in late March/April.",
        "summer": "Hot and humid, 26-32°C. Frequent summer festivals and fireworks displays.",
        "autumn": "Cool and comfortable, 15-21°C. Stunning autumn foliage (Momiji) in November.",
        "winter": "Cold and clear, 2-10°C. Great for winter illuminations and nearby skiing.",
    },
    "paris": {
        "spring": "Fresh and mild, 11-20°C. Beautiful city walks, moderate crowds.",
        "summer": "Warm and sunny, 16-25°C. High tourist season, long daylight hours.",
        "autumn": "Cool and colorful, 10-16°C. Excellent museum weather, fewer crowds.",
        "winter": "Cold and damp, 3-8°C. Festive Christmas markets, low season rates.",
    },
    "new york": {
        "spring": "Crisp and changing, 5-18°C. Central Park is in full bloom.",
        "summer": "Hot and humid, 20-29°C. Outdoor concerts, rooftop bars active.",
        "autumn": "Cool and breezy, 10-18°C. Perfect for walking, beautiful fall colors.",
        "winter": "Cold and snowy, -3 to 6°C. Famous holiday decorations and ice skating.",
    },
}

DEFAULT_WEATHER = "Mild and variable, 15-22°C. Good time to explore local sights."

POPULAR_VISITS = {
    "tokyo": ["Senso-ji Temple", "Shibuya Crossing", "Meiji Shrine", "Tokyo Skytree"],
    "paris": [
        "Eiffel Tower",
        "Louvre Museum",
        "Notre-Dame Cathedral",
        "Seine River Cruise",
    ],
    "new york": [
        "Statue of Liberty",
        "Central Park",
        "Empire State Building",
        "Times Square",
    ],
}

DEFAULT_VISITS = [
    "Local City Center",
    "Historical Museum",
    "Public Parks",
    "Scenic Viewpoint",
]

FLIGHT_DATABASE = {
    "tokyo": [
        {
            "flight": "AuraAir 201",
            "class": "Economy",
            "price": 850.00,
            "duration": "14h 30m",
        },
        {
            "flight": "AuraAir 202",
            "class": "Business",
            "price": 2450.00,
            "duration": "14h 30m",
        },
    ],
    "paris": [
        {
            "flight": "AuraAir 101",
            "class": "Economy",
            "price": 600.00,
            "duration": "8h 15m",
        },
        {
            "flight": "AuraAir 102",
            "class": "Business",
            "price": 1800.00,
            "duration": "8h 15m",
        },
    ],
    "new york": [
        {
            "flight": "AuraAir 301",
            "class": "Economy",
            "price": 350.00,
            "duration": "5h 45m",
        },
        {
            "flight": "AuraAir 302",
            "class": "Business",
            "price": 950.00,
            "duration": "5h 45m",
        },
    ],
}

HOTEL_DATABASE = {
    "tokyo": {
        "economy": {
            "name": "Shinjuku Capsule & Inn",
            "price_per_night": 45.00,
            "rating": "4.2/5",
        },
        "mid-range": {
            "name": "Shibuya Stream Hotel",
            "price_per_night": 180.00,
            "rating": "4.5/5",
        },
        "luxury": {"name": "Aman Tokyo", "price_per_night": 950.00, "rating": "4.9/5"},
    },
    "paris": {
        "economy": {
            "name": "Hotel de la Gare",
            "price_per_night": 75.00,
            "rating": "4.0/5",
        },
        "mid-range": {
            "name": "Hotel Marais Bastille",
            "price_per_night": 210.00,
            "rating": "4.4/5",
        },
        "luxury": {
            "name": "The Ritz Paris",
            "price_per_night": 1200.00,
            "rating": "4.9/5",
        },
    },
    "new york": {
        "economy": {
            "name": "The Pod Hotel 39",
            "price_per_night": 90.00,
            "rating": "4.1/5",
        },
        "mid-range": {
            "name": "Arlo NoMad",
            "price_per_night": 240.00,
            "rating": "4.5/5",
        },
        "luxury": {
            "name": "The Plaza Hotel",
            "price_per_night": 1100.00,
            "rating": "4.8/5",
        },
    },
}

RESTAURANTS_DATABASE = {
    "tokyo": [
        {
            "name": "Ichiran Ramen",
            "type": "Casual",
            "cuisine": "Japanese (Ramen)",
            "avg_cost_person": 15.00,
        },
        {
            "name": "Sushi Dai",
            "type": "Mid-range",
            "cuisine": "Japanese (Sushi)",
            "avg_cost_person": 50.00,
        },
        {
            "name": "Ryugin",
            "type": "Fine Dining",
            "cuisine": "Japanese (Kaiseki)",
            "avg_cost_person": 300.00,
        },
    ],
    "paris": [
        {
            "name": "L'As du Fallafel",
            "type": "Casual",
            "cuisine": "Middle Eastern",
            "avg_cost_person": 12.00,
        },
        {
            "name": "Le Bistro Paul Bert",
            "type": "Mid-range",
            "cuisine": "French Bistro",
            "avg_cost_person": 45.00,
        },
        {
            "name": "L'Ambroisie",
            "type": "Fine Dining",
            "cuisine": "French Haute Cuisine",
            "avg_cost_person": 350.00,
        },
    ],
    "new york": [
        {
            "name": "Joe's Pizza",
            "type": "Casual",
            "cuisine": "Pizza",
            "avg_cost_person": 8.00,
        },
        {
            "name": "Balthazar",
            "type": "Mid-range",
            "cuisine": "French Bistro",
            "avg_cost_person": 60.00,
        },
        {
            "name": "Eleven Madison Park",
            "type": "Fine Dining",
            "cuisine": "Plant-based Fine Dining",
            "avg_cost_person": 400.00,
        },
    ],
}


@mcp.tool()
def get_weather_forecast(destination: str, season_or_month: str) -> dict:
    """Retrieves the weather forecast and popular activities for a destination during a specific season or month.

    Args:
        destination: The destination city.
        season_or_month: The season (spring, summer, autumn, winter) or month (January-December).

    Returns:
        dict: Weather report and recommended local spots.
    """
    if not destination or not destination.strip():
        raise ValueError("Destination cannot be empty")
    if not season_or_month or not season_or_month.strip():
        raise ValueError("Season or month cannot be empty")

    dest = destination.lower().strip()
    season = season_or_month.lower().strip()

    # Map month to season
    month_to_season = {
        "january": "winter",
        "february": "winter",
        "december": "winter",
        "march": "spring",
        "april": "spring",
        "may": "spring",
        "june": "summer",
        "july": "summer",
        "august": "summer",
        "september": "autumn",
        "october": "autumn",
        "november": "autumn",
    }

    if season in month_to_season:
        season = month_to_season[season]

    weather = DEFAULT_WEATHER
    visits = DEFAULT_VISITS

    if dest in WEATHER_DATA:
        weather = WEATHER_DATA[dest].get(season, DEFAULT_WEATHER)
        visits = POPULAR_VISITS.get(dest, DEFAULT_VISITS)

    return {
        "destination": destination,
        "season_determined": season,
        "weather_summary": weather,
        "popular_visits": visits,
    }


@mcp.tool()
def get_flight_options(destination: str) -> dict:
    """Retrieves list of flight options to a destination.

    Args:
        destination: The destination city.

    Returns:
        dict: Flight options with flight numbers, classes, and prices.
    """
    if not destination or not destination.strip():
        raise ValueError("Destination cannot be empty")
    dest = destination.lower().strip()
    flights = FLIGHT_DATABASE.get(
        dest,
        [
            {
                "flight": "AuraAir 901",
                "class": "Economy",
                "price": 700.00,
                "duration": "10h 00m",
            }
        ],
    )
    return {"destination": destination, "flights": flights}


@mcp.tool()
def get_hotel_options(destination: str, budget_level: str) -> dict:
    """Retrieves hotel suggestions based on destination and budget level.

    Args:
        destination: The destination city.
        budget_level: Budget level (economy, mid-range, luxury).

    Returns:
        dict: Recommended hotel name, price per night, and rating.
    """
    if not destination or not destination.strip():
        raise ValueError("Destination cannot be empty")
    if not budget_level or budget_level.lower().strip() not in ["economy", "mid-range", "luxury"]:
        raise ValueError("Invalid budget level")
    dest = destination.lower().strip()
    budget = budget_level.lower().strip()

    if dest in HOTEL_DATABASE:
        hotel = HOTEL_DATABASE[dest].get(budget, HOTEL_DATABASE[dest]["mid-range"])
    else:
        hotel = {"name": "Aura Cozy Stay", "price_per_night": 120.00, "rating": "4.3/5"}

    return {"destination": destination, "budget_level": budget_level, "hotel": hotel}


@mcp.tool()
def get_restaurant_suggestions(destination: str) -> dict:
    """Retrieves top restaurant suggestions for a destination.

    Args:
        destination: The destination city.

    Returns:
        dict: List of restaurants with cuisines and average cost.
    """
    if not destination or not destination.strip():
        raise ValueError("Destination cannot be empty")
    dest = destination.lower().strip()
    restaurants = RESTAURANTS_DATABASE.get(
        dest,
        [
            {
                "name": "Local Dining Hall",
                "type": "Casual",
                "cuisine": "International",
                "avg_cost_person": 25.00,
            }
        ],
    )
    return {"destination": destination, "restaurants": restaurants}


if __name__ == "__main__":
    # Start the fastmcp stdio server
    mcp.run()
