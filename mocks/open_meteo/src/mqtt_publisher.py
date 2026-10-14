import json
import time
from threading import Event
from typing import Any

import paho.mqtt.client as mqtt

from .config import Settings


class MqttPublisher:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._connected = Event()
        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"mock-open-meteo-{settings.node_id}",
            protocol=mqtt.MQTTv311,
        )

        if settings.mqtt_username:
            self._client.username_pw_set(settings.mqtt_username, settings.mqtt_password)

        self._client.reconnect_delay_set(min_delay=1, max_delay=30)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, connect_flags, reason_code, properties) -> None:
        del client, userdata, connect_flags, properties
        if reason_code.is_failure:
            print(f"[MQTT] Conexion rechazada: {reason_code}")
            self._connected.clear()
            return
        print("[MQTT] Conectado al broker.")
        self._connected.set()

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties) -> None:
        del client, userdata, disconnect_flags, properties
        self._connected.clear()
        if reason_code.is_failure:
            print(f"[MQTT] Conexion perdida; se reintentara: {reason_code}")
        else:
            print("[MQTT] Desconectado correctamente.")

    def connect(self) -> None:
        print(f"[MQTT] Conectando a {self._settings.mqtt_host}:{self._settings.mqtt_port}...")
        self._client.connect(
            self._settings.mqtt_host,
            self._settings.mqtt_port,
            keepalive=self._settings.mqtt_keepalive_seconds,
        )
        self._client.loop_start()
        if not self._connected.wait(self._settings.mqtt_connect_timeout_seconds):
            self._client.loop_stop()
            raise TimeoutError("No se pudo conectar al broker MQTT.")

    def publish_measurement(self, payload: dict[str, Any]) -> None:
        if not self._connected.is_set():
            deadline = time.monotonic() + self._settings.mqtt_connect_timeout_seconds
            while not self._connected.is_set() and time.monotonic() < deadline:
                time.sleep(0.1)
        if not self._connected.is_set():
            raise ConnectionError("El cliente MQTT no esta conectado.")

        serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        result = self._client.publish(
            self._settings.measurement_topic,
            payload=serialized,
            qos=self._settings.mqtt_qos,
            retain=False,
        )
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(
                f"Error MQTT {result.rc} al publicar en {self._settings.measurement_topic}."
            )
        result.wait_for_publish(timeout=10.0)

    def disconnect(self) -> None:
        self._client.disconnect()
        self._client.loop_stop()
