from dataclasses import dataclass

import requests

TRIPS_URL = "https://helium-prod.mylirr.org/v1/subway/trips"
TIMEOUT = 10


@dataclass(frozen=True)
class Train:
    id: str
    route: str
    lat: float
    lon: float


def fetch_trains() -> list[Train]:
    """Trains with a known position; trips that haven't left yet have none."""
    response = requests.get(TRIPS_URL, timeout=TIMEOUT)
    response.raise_for_status()
    return [
        Train(id=trip["tripId"], route=trip["routeId"], lat=trip["estimatedLatitude"], lon=trip["estimatedLongitude"])
        for trip in response.json()["trips"]
        if trip.get("estimatedLatitude") is not None and trip.get("estimatedLongitude") is not None
    ]
