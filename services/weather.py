from urllib.parse import urlencode
from dataclasses import dataclass
from datetime import datetime
import requests


@dataclass(frozen=True)
class WeatherData:
    currentTempF: int
    maxTempF: int
    minTempF: int


TIMEOUT = 5
WEATHER_API_BASE_URL = "https://api.open-meteo.com/v1/forecast"
PARAMETERS = {
    "latitude": 40.665029432165504,
    "longitude": -73.95377924895932,
    "hourly": ",".join(
        [
            "temperature_2m",
            "wind_speed_10m",
            "wind_direction_10m",
            "precipitation_probability",
            "wind_gusts_10m",
            "cloud_cover",
            "snowfall",
            "rain",
            "showers",
        ]
    ),
    "daily": ",".join(["temperature_2m_max", "temperature_2m_min"]),
    "current": ",".join(["temperature_2m"]),
    "timezone": "auto",
    "forecast_days": 1,
    "wind_speed_unit": "mph",
    "temperature_unit": "fahrenheit",
    "precipitation_unit": "inch",
}

WEATHER_API_ENDPOINT = f"{WEATHER_API_BASE_URL}?{urlencode(PARAMETERS)}"


def fetch_weather() -> WeatherData:
    response = requests.get(WEATHER_API_ENDPOINT, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    daily = data.get("daily", {})
    max_temp = int(daily["temperature_2m_max"][0])
    min_temp = int(daily["temperature_2m_min"][0])
    current = data["current"]
    current_temp = int(current["temperature_2m"])
    return WeatherData(currentTempF=current_temp, maxTempF=max_temp, minTempF=min_temp)


if __name__ == "__main__":
    print(fetch_weather())
