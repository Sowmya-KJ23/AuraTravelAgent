# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from google.adk.workflow import Workflow, START, node
from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.adk.agents.context import Context
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import FunctionTool
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types

from auratravel_agent.config import MODEL_NAME

# Load environment variables from .env
load_dotenv()

# Setup Local Authentication & Environment
if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
    if os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
else:
    # Default to Vertex AI (GCP Project Mode)
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        try:
            import google.auth

            _, project_id = google.auth.default()
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        except Exception:
            pass
    if not os.environ.get("GOOGLE_CLOUD_LOCATION"):
        os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# Initialize standard Gemini Model Client
llm = Gemini(
    model=MODEL_NAME,
    retry_options=types.HttpRetryOptions(attempts=3),
)

# -------------------------------------------------------------------------
# Pydantic Schemas for Structured I/O
# -------------------------------------------------------------------------


class PassengerDemographics(BaseModel):
    age_groups: List[str] = Field(
        description="Age groups of travelers (e.g. adults, kids, seniors)."
    )
    interests: List[str] = Field(
        description="Traveler interests (e.g. food, history, nature, adventure, relaxation)."
    )
    group_size: int = Field(description="Total number of travelers in the party.")


class ParsedTripInfo(BaseModel):
    destination: str = Field(
        description="The destination city or country (e.g. Tokyo, Paris, New York). If not specified, set to 'unknown'."
    )
    season_or_month: str = Field(
        description="The travel month or season (e.g. summer, June, December). If not specified, set to 'unknown'."
    )
    duration_days: int = Field(
        description="The length of the trip in days. If not specified, set to 0."
    )
    budget_level: str = Field(
        description="The budget level: economy, mid-range, or luxury. If not specified, set to 'unknown'."
    )
    demographics: PassengerDemographics = Field(
        description="The party group size, age groups, and interests of the travelers."
    )
    raw_query_pii_scrubbed: str = Field(
        description="The original user query, but with any Personally Identifiable Information (PII) like real names, passport numbers, email/phone details replaced with placeholders like [TRAVELER_1]."
    )
    is_complete: bool = Field(
        description="True if destination is specified and we have enough details to suggest weather and sights. Otherwise False."
    )
    clarification_message: Optional[str] = Field(
        None,
        description="If is_complete is False, a polite, helpful prompt asking the user for the missing details. Otherwise None.",
    )


class WeatherAnalysis(BaseModel):
    destination: str = Field(description="The destination city/country.")
    weather_summary: str = Field(description="Summary of the weather forecast.")
    popular_visits: List[str] = Field(
        description="Recommended seasonal attractions/visits."
    )
    travel_tips: str = Field(
        description="Demographic-aware travel tips based on weather and season."
    )


# -------------------------------------------------------------------------
# Local Python Tools
# -------------------------------------------------------------------------


def calculate_total_trip_cost(
    flight_cost: float,
    hotel_cost_per_night: float,
    duration_days: int,
    food_cost_per_day: float,
    num_passengers: int,
) -> dict:
    """Calculates the total trip cost including flights, hotel, and food estimate.

    Args:
        flight_cost: Cost of flight ticket per person.
        hotel_cost_per_night: Nightly rate for the hotel room.
        duration_days: Total number of days for the trip.
        food_cost_per_day: Estimated cost of food per person per day.
        num_passengers: Number of passengers/travelers.

    Returns:
        dict: Breakdown of trip costs and the total sum.
    """
    if flight_cost < 0:
        raise ValueError("Flight cost cannot be negative")
    if hotel_cost_per_night < 0:
        raise ValueError("Hotel cost per night cannot be negative")
    if duration_days <= 0:
        raise ValueError("Duration days must be positive")
    if food_cost_per_day < 0:
        raise ValueError("Food cost per day cannot be negative")
    if num_passengers <= 0:
        raise ValueError("Number of passengers must be positive")

    total_flights = flight_cost * num_passengers
    nights = duration_days - 1 if duration_days > 1 else 1
    total_hotel = hotel_cost_per_night * nights
    total_food = food_cost_per_day * duration_days * num_passengers
    total_cost = total_flights + total_hotel + total_food

    return {
        "flight_cost_breakdown": f"${flight_cost:.2f} x {num_passengers} = ${total_flights:.2f}",
        "hotel_cost_breakdown": f"${hotel_cost_per_night:.2f} x {nights} nights = ${total_hotel:.2f}",
        "food_cost_breakdown": f"${food_cost_per_day:.2f} x {duration_days} days x {num_passengers} travelers = ${total_food:.2f}",
        "total_cost": total_cost,
        "summary": f"Total estimated cost for {num_passengers} travelers over {duration_days} days is ${total_cost:.2f}",
    }


cost_tool = FunctionTool(
    calculate_total_trip_cost,
)


# -------------------------------------------------------------------------
# Model Context Protocol (MCP) Toolsets
# -------------------------------------------------------------------------

# Toolset for weather lookup
weather_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=["run", "python", "auratravel_agent/mcp_server.py"],
        ),
    ),
    tool_filter=["get_weather_forecast"],
)

# Toolset for booking options and suggestions
booking_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=["run", "python", "auratravel_agent/mcp_server.py"],
        ),
    ),
    tool_filter=[
        "get_flight_options",
        "get_hotel_options",
        "get_restaurant_suggestions",
    ],
)


# -------------------------------------------------------------------------
# State Initialization Callback
# -------------------------------------------------------------------------


async def init_trip_state(callback_context: CallbackContext) -> None:
    """Initializes session state keys to avoid format key errors."""
    if "trip_details" not in callback_context.state:
        callback_context.state["trip_details"] = {
            "destination": "unknown",
            "season_or_month": "unknown",
            "duration_days": 0,
            "budget_level": "unknown",
            "demographics": {"age_groups": [], "interests": [], "group_size": 1},
            "raw_query_pii_scrubbed": "",
            "is_complete": False,
        }
    if "weather_analysis" not in callback_context.state:
        callback_context.state["weather_analysis"] = {
            "destination": "unknown",
            "weather_summary": "unknown weather",
            "popular_visits": [],
            "travel_tips": "",
        }


# -------------------------------------------------------------------------
# Workflow Node Definitions
# -------------------------------------------------------------------------

# Node 1: Parse Input (LlmAgent)
# Node 1: Parse Input (LlmAgent)
parse_input = LlmAgent(
    name="parse_input",
    model=llm,
    static_instruction="""You are a security-conscious, privacy-focused travel input parser.
    Your task is to parse raw user queries and extract details needed for travel planning.

    1. EXCLUSIVELY output a JSON object adhering to the schema.
    2. PRIVACY/SECURITY RULE: Scrub any Personally Identifiable Information (PII) like real names, passport numbers, email addresses, phone numbers, or physical addresses. Replace them with generic placeholders like [TRAVELER_1].
    3. If the user's query is a follow-up (e.g. asking for hotel bookings, flights, cost calculations, or restaurant suggestions) and destination/dates are not mentioned, refer to the existing trip details in the state and fill in the missing details from there.
    4. Determine if the information is complete enough to proceed. You need at least a destination and a travel season/month to suggest weather and destinations. If complete, set is_complete=True.
    5. If is_complete is False, generate a polite clarification message in clarification_message asking for the missing details.
    """,
    instruction="Existing trip details in state: {trip_details}",
    output_schema=ParsedTripInfo,
    output_key="parsed_trip_info",
    before_agent_callback=init_trip_state,
)


# Programmatic Wrapper Node 1: Parse Input (Executed Silently)
async def parse_input_node(ctx: Context) -> Event:
    """Runs the parse_input agent internally without streaming output to the user."""
    await init_trip_state(ctx)

    parsed_info = None
    async for event in parse_input.run(ctx=ctx, node_input=None):
        if event.output is not None:
            parsed_info = event.output

    if parsed_info is None:
        parsed_info = ctx.state.get("trip_details") or {
            "destination": "unknown",
            "season_or_month": "unknown",
            "duration_days": 0,
            "budget_level": "unknown",
            "demographics": {"age_groups": [], "interests": [], "group_size": 1},
            "raw_query_pii_scrubbed": "",
            "is_complete": False,
        }

    return Event(output=parsed_info)


# Node 2: Check completeness & router (FunctionNode)
def check_trip_completeness(ctx: Context, node_input: dict) -> Event:
    """Checks if the parsed trip info is complete and routes accordingly."""
    is_complete = node_input.get("is_complete", False)

    if not is_complete:
        clarification = (
            node_input.get("clarification_message")
            or "Could you please specify your destination and when you plan to travel?"
        )
        return Event(output=clarification, actions={"route": "clarify"})

    # Check if we already have weather analysis for this destination to avoid duplicate API calls
    prev_details = ctx.state.get("trip_details", {})
    prev_dest = prev_details.get("destination", "").lower().strip()
    new_dest = node_input.get("destination", "").lower().strip()

    has_weather = (
        ctx.state.get("weather_analysis", {}).get("destination", "unknown") != "unknown"
    )

    # Save the new details to state
    ctx.state["trip_details"] = node_input

    if has_weather and prev_dest == new_dest:
        return Event(
            output=ctx.state["weather_analysis"],
            actions={"route": "skip_weather"},
        )
    else:
        return Event(output=node_input, actions={"route": "ready"})


# Node 3: Ask Clarification (FunctionNode)
def ask_clarification(node_input: str):
    """Returns the clarification prompt to the user and displays it in the chat UI."""
    yield Event(
        content=types.Content(
            role="model", parts=[types.Part.from_text(text=node_input)]
        )
    )
    yield Event(output=node_input)


# Node 4: Analyze Weather & Seasonal popularity (LlmAgent)
weather_season_analyzer = LlmAgent(
    name="weather_season_analyzer",
    model=llm,
    static_instruction="""You are a weather and seasonal travel analyst.
    Your task is to check the weather forecast and popular activities for the destination.
    Look up the weather using the get_weather_forecast tool for the destination and season/month.
    Then, analyze how this weather affects the traveler demographics.
    Provide structural recommendations in the output schema.
    """,
    instruction="Trip parameters in state: {trip_details}",
    tools=[weather_toolset],
    output_schema=WeatherAnalysis,
    output_key="weather_analysis",
)


# Programmatic Wrapper Node 4: Weather Season Analyzer (Executed Silently)
async def weather_season_analyzer_node(ctx: Context, node_input: dict) -> Event:
    """Runs the weather_season_analyzer agent internally without streaming output."""
    weather_info = None
    async for event in weather_season_analyzer.run(ctx=ctx, node_input=node_input):
        if event.output is not None:
            weather_info = event.output

    # Save the weather analysis to state
    ctx.state["weather_analysis"] = weather_info

    return Event(output=weather_info)


# Node 5: Generate Itinerary (LlmAgent)
itinerary_generator = LlmAgent(
    name="itinerary_generator",
    model=llm,
    static_instruction="""You are a personalized, creative AI travel assistant.
    Your task is to generate a comprehensive, day-by-day travel itinerary and assist the user with specific bookings and suggestions.

    Role & Instructions:
    1. Generate a demographic-aware day-by-day itinerary tailored to the traveler's interests, age group, and budget.
    2. The itinerary MUST include:
       - Day passes: Suggest practical local transit passes (e.g. Navigo, Metro pass), city tourist cards, museum passes, or skip-the-line bundle passes.
       - Local activities that are happening: Mention seasonal festivals, local tours, public events, street markets, or seasonal happenings relevant to their travel time.
       - Monuments details & famous places: Include historical context, cultural/architectural significance, opening hours, or ticketing tips for the sights in the itinerary.
       - Local Spas & Wellness: Recommend local spas, wellness retreats, traditional public baths (such as Onsens in Tokyo, traditional baths in Paris, or wellness spas in New York) for relaxation.
       - Tourist Scams & Safety Alerts: Highlight common scams, tourist traps, or safety tips for the locations (e.g., petition scams, pickpocket hotspots, fake ticket sellers) so they travel safely.
    3. ON-DEMAND TOOL CALLING RULE: Only invoke the booking tools (`get_flight_options`, `get_hotel_options`, `get_restaurant_suggestions`) on-demand when the user explicitly requests that type of information in their input (e.g. by using keywords like 'flight', 'ticket', 'hotel', 'stay', 'accommodation', 'restaurant', 'eat', 'food', 'dining', etc. in their query).
       - Do NOT call these tools on the initial itinerary request unless the user's initial query explicitly asks for them.
       - Inform the user that they can request flight options, hotel suggestions, restaurant recommendations, or total trip cost calculations.
    4. If the user wants to calculate the total cost of the trip, invoke the calculate_total_trip_cost tool using values retrieved from the other tools or based on user input.
    5. Always be polite, creative, and structured.
    """,
    instruction="Weather analysis: {weather_analysis}\nTrip details in state: {trip_details}",
    tools=[booking_toolset, cost_tool],
    output_key="itinerary",
)

# -------------------------------------------------------------------------
# Workflow Configuration & Registration
# -------------------------------------------------------------------------

# Define graph workflow edges
edges = [
    (START, parse_input_node),
    (parse_input_node, check_trip_completeness),
    (
        check_trip_completeness,
        {
            "clarify": ask_clarification,
            "ready": weather_season_analyzer_node,
            "skip_weather": itinerary_generator,
        },
    ),
    (weather_season_analyzer_node, itinerary_generator),
]

root_agent = Workflow(
    name="root_agent",
    edges=edges,
    description="A modular, privacy-focused travel planning assistant.",
)

app = App(
    root_agent=root_agent,
    name="auratravel_agent",
)
