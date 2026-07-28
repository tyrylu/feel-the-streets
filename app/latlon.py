from dataclasses import dataclass


@dataclass
class LatLon:
    """Lightweight position container holding a latitude and longitude in decimal degrees."""
    lat: float
    lon: float
