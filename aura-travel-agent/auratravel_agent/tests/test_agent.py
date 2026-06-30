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

import pytest
from auratravel_agent.agent import calculate_total_trip_cost
from auratravel_agent.mcp_server import (
    get_weather_forecast,
    get_flight_options,
    get_hotel_options,
    get_restaurant_suggestions,
)

# -------------------------------------------------------------------------
# Test Suite for calculate_total_trip_cost (Local Python Tool)
# -------------------------------------------------------------------------

def test_calculate_total_trip_cost_valid():
    """Verify cost calculation with standard valid inputs."""
    result = calculate_total_trip_cost(
        flight_cost=500.0,
        hotel_cost_per_night=150.0,
        duration_days=5,
        food_cost_per_day=50.0,
        num_passengers=2,
    )
    assert result["total_cost"] == (500.0 * 2) + (150.0 * 4) + (50.0 * 5 * 2)

def test_calculate_total_trip_cost_negative_flight():
    """Verify that negative flight cost raises a ValueError."""
    with pytest.raises(ValueError, match="Flight cost cannot be negative"):
        calculate_total_trip_cost(
            flight_cost=-500.0,
            hotel_cost_per_night=150.0,
            duration_days=5,
            food_cost_per_day=50.0,
            num_passengers=2,
        )

def test_calculate_total_trip_cost_negative_hotel():
    """Verify that negative hotel cost raises a ValueError."""
    with pytest.raises(ValueError, match="Hotel cost per night cannot be negative"):
        calculate_total_trip_cost(
            flight_cost=500.0,
            hotel_cost_per_night=-150.0,
            duration_days=5,
            food_cost_per_day=50.0,
            num_passengers=2,
        )

def test_calculate_total_trip_cost_invalid_duration():
    """Verify that zero or negative duration days raises a ValueError."""
    with pytest.raises(ValueError, match="Duration days must be positive"):
        calculate_total_trip_cost(
            flight_cost=500.0,
            hotel_cost_per_night=150.0,
            duration_days=0,
            food_cost_per_day=50.0,
            num_passengers=2,
        )

def test_calculate_total_trip_cost_negative_food():
    """Verify that negative food cost raises a ValueError."""
    with pytest.raises(ValueError, match="Food cost per day cannot be negative"):
        calculate_total_trip_cost(
            flight_cost=500.0,
            hotel_cost_per_night=150.0,
            duration_days=5,
            food_cost_per_day=-50.0,
            num_passengers=2,
        )

def test_calculate_total_trip_cost_invalid_passengers():
    """Verify that zero or negative passenger count raises a ValueError."""
    with pytest.raises(ValueError, match="Number of passengers must be positive"):
        calculate_total_trip_cost(
            flight_cost=500.0,
            hotel_cost_per_night=150.0,
            duration_days=5,
            food_cost_per_day=50.0,
            num_passengers=0,
        )


# -------------------------------------------------------------------------
# Test Suite for MCP Tools (Business Logic and Input Guardrails)
# -------------------------------------------------------------------------

def test_get_weather_forecast_validation():
    """Verify that empty destination or season/month raises a ValueError."""
    with pytest.raises(ValueError, match="Destination cannot be empty"):
        get_weather_forecast(destination="", season_or_month="spring")

    with pytest.raises(ValueError, match="Season or month cannot be empty"):
        get_weather_forecast(destination="Tokyo", season_or_month="")

def test_get_flight_options_validation():
    """Verify that empty destination raises a ValueError."""
    with pytest.raises(ValueError, match="Destination cannot be empty"):
        get_flight_options(destination="")

def test_get_hotel_options_validation():
    """Verify that empty parameters or invalid budget level raises a ValueError."""
    with pytest.raises(ValueError, match="Destination cannot be empty"):
        get_hotel_options(destination="", budget_level="mid-range")

    with pytest.raises(ValueError, match="Invalid budget level"):
        get_hotel_options(destination="Tokyo", budget_level="super-rich")

def test_get_restaurant_suggestions_validation():
    """Verify that empty destination raises a ValueError."""
    with pytest.raises(ValueError, match="Destination cannot be empty"):
        get_restaurant_suggestions(destination="")
