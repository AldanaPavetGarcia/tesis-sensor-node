import json
import signal
import sys
from datetime import datetime, timedelta, timezone
from threading import Event

from .config import load_settings
from .generator import OpenMeteoGenerator
from .mqtt_publisher import MqttPublisher
from .payload_builder import build_measurement_payload


stop_event = Event()


def _request_stop(signum: int, frame: object) -> None:
    del frame
    print(f"\n[APP] Senal {signum} recibida. Finalizando...")
    stop_event.set()


def run() -> int:
    settings = load_settings()
    print("=== Mock Open-Meteo ===")
    print(f"[CONFIG] Broker: {settings.mqtt_host}:{settings.mqtt_port}")
    print(f"[CONFIG] Topico: {settings.measurement_topic}")
    print(f"[CONFIG] Intervalo simulado: {settings.publish_interval_seconds}s")
    print(f"[CONFIG] TIME_WARP_FACTOR: {settings.time_warp_factor}")
    print(f"[CONFIG] Espera real: {settings.real_wait_seconds:.3f}s")

    generator = OpenMeteoGenerator(
        settings.random_seed,
        settings.missing_field_probability,
    )
    publisher = MqttPublisher(settings)
    simulated_at = datetime.now(timezone.utc)
    publisher.connect()

    try:
        while not stop_event.is_set():
            reading = generator.generate(simulated_at)
            payload = build_measurement_payload(
                node_id=settings.node_id,
                schema_version=settings.schema_version,
                measured_at=simulated_at,
                reading=reading,
            )
            publisher.publish_measurement(payload)
            print(
                f"[MQTT] Publicado en {settings.measurement_topic}: "
                f"{json.dumps(payload, ensure_ascii=False)}"
            )

            simulated_at += timedelta(seconds=settings.publish_interval_seconds)
            stop_event.wait(settings.real_wait_seconds)
    finally:
        publisher.disconnect()

    return 0


def main() -> None:
    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)
    try:
        code = run()
    except (ValueError, OSError, ConnectionError, TimeoutError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        code = 1
    raise SystemExit(code)


if __name__ == "__main__":
    main()
