from typing import TypedDict, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field


class WeatherAPIError(Exception):
    pass

@dataclass
class WeatherData:
    temperature: float      # Celsius
    humidity: float         # %
    condition: str          # e.g. "clear sky"
    wind_speed: float       # m/s