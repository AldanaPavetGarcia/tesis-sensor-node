from dataclasses import dataclass


@dataclass(frozen=True)
class ExternalWeatherReading:
    temperature_c: float | None
    humidity_pct: float | None
    pressure_hpa: float | None
    precipitation_mm: float | None
    wind_speed_kmh: float | None
    cloud_cover_pct: float | None
