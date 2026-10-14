from dataclasses import dataclass
import os

from dotenv import load_dotenv


def _int(name: str, default: int, minimum: int | None = None) -> int:
    value = int(os.getenv(name, str(default)))
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} debe ser >= {minimum}.")
    return value


def _float(
    name: str,
    default: float,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    value = float(os.getenv(name, str(default)))
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} debe ser >= {minimum}.")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} debe ser <= {maximum}.")
    return value


@dataclass(frozen=True)
class Settings:
    mqtt_host: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str
    mqtt_qos: int
    mqtt_keepalive_seconds: int
    mqtt_connect_timeout_seconds: int
    node_id: str
    schema_version: str
    publish_interval_seconds: float
    time_warp_factor: float
    random_seed: int
    missing_field_probability: float

    @property
    def measurement_topic(self) -> str:
        return f"meteo/external/{self.node_id}"

    @property
    def real_wait_seconds(self) -> float:
        return self.publish_interval_seconds / self.time_warp_factor


def load_settings() -> Settings:
    load_dotenv()
    qos = _int("MQTT_QOS", 1, 0)
    if qos not in {0, 1, 2}:
        raise ValueError("MQTT_QOS debe ser 0, 1 o 2.")

    return Settings(
        mqtt_host=os.getenv("MQTT_HOST", "localhost"),
        mqtt_port=_int("MQTT_PORT", 1883, 1),
        mqtt_username=os.getenv("MQTT_USERNAME", ""),
        mqtt_password=os.getenv("MQTT_PASSWORD", ""),
        mqtt_qos=qos,
        mqtt_keepalive_seconds=_int("MQTT_KEEPALIVE_SECONDS", 60, 1),
        mqtt_connect_timeout_seconds=_int("MQTT_CONNECT_TIMEOUT_SECONDS", 10, 1),
        node_id=os.getenv("NODE_ID", "lit-cordoba-01"),
        schema_version=os.getenv("SCHEMA_VERSION", "1.0"),
        publish_interval_seconds=_float("PUBLISH_INTERVAL_SECONDS", 900.0, 0.1),
        time_warp_factor=_float("TIME_WARP_FACTOR", 1.0, 0.01),
        random_seed=_int("RANDOM_SEED", 84),
        missing_field_probability=_float(
            "MISSING_FIELD_PROBABILITY", 0.05, 0.0, 1.0
        ),
    )
