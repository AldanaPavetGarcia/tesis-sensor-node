# Mock BME280 - guía rápida de ejecución

## 1. Qué simula

Este programa reemplaza temporalmente al conjunto físico **BME280 + ESP32**.
No utiliza I2C: genera mediciones en Python y las publica directamente en
Mosquitto mediante MQTT.

```text
Mock Python ── MQTT ──> Mosquitto ──> consumer/suscriptor
```

En el sistema real, el recorrido será:

```text
BME280 ── I2C ──> ESP32 ── Wi-Fi + MQTT ──> Mosquitto ──> consumer
```

El mock reproduce el contrato JSON que deberá utilizar también el firmware
real. El campo `source` indica si el dato es real o simulado (`real` o `mock`),
mientras que `producer` identifica quién produce la medición, por ejemplo
`bme280`.

> No ejecutar el mock y el ESP32 real con el mismo `NODE_ID` durante una prueba
> simple, salvo que se quiera recibir ambas fuentes simultáneamente.

## 2. Preparación inicial, una sola vez

Desde la raíz del repositorio:

```bash
cd mocks/bme280
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp -n .env.example .env
```

El entorno virtual instala únicamente las dependencias Python del mock:
`paho-mqtt`, `python-dotenv` y `pytest`.

## 3. Configuración

El archivo local `mocks/bme280/.env` define el broker, el nodo y la velocidad de
simulación. Para la demostración local puede conservarse:

```env
MQTT_HOST=localhost
MQTT_PORT=1883
NODE_ID=lit-cordoba-01
PUBLISH_INTERVAL_SECONDS=60
TIME_WARP_FACTOR=60
CHAOS_ENABLED=false
```

Con intervalo 60 y factor 60, el reloj simulado avanza un minuto por cada
segundo real.

## 4. Pruebas unitarias

Con `.venv` activado:

```bash
cd mocks/bme280
source .venv/bin/activate
python -m pytest -q
```

Resultado esperado:

```text
.... [100%]
5 passed
```

## 5. Demostración en tres terminales

### Terminal 1 - levantar Mosquitto

Desde la raíz:

```bash
cd infrastructure/mosquitto
docker compose up -d
docker compose ps
```

El contenedor esperado es `tesis-mosquitto`, en estado `Up`, con el puerto
`1883` publicado.

### Terminal 2 - recibir la información

Opción rápida, mostrando el mensaje MQTT sin procesarlo:

```bash
cd <RAIZ_DEL_REPOSITORIO>
./scripts/mqtt-subscribe.sh
```

Opción demostrativa, usando un pequeño consumer de consola que valida el JSON:

```bash
cd mocks/bme280
source .venv/bin/activate
python ../../tools/console_consumer.py
```

Este consumer es sólo una herramienta de demostración. El consumer conjunto
definitivo deberá además validar el contrato completo y persistir en la base de
datos.

### Terminal 3 - ejecutar el mock

```bash
cd mocks/bme280
source .venv/bin/activate
python -m src.main
```

Se publican:

- Mediciones: `meteo/sensor/<node_id>`.
- Estado/LWT: `meteo/status/<node_id>`.

Para detener el mock:

```text
Ctrl + C
```

## 6. Payload esperado

```json
{
  "node_id": "lit-cordoba-01",
  "timestamp": "2026-08-06T13:20:00Z",
  "source": "mock",
  "producer": "bme280",
  "schema_version": "1.0",
  "metrics": {
    "temperature_c": 22.5,
    "humidity_pct": 60.0,
    "pressure_hpa": 1012.0,
    "sensor_uid": "bme280-mock-01"
  }
}
```

El contrato ambiental utiliza `source` para distinguir datos reales de
simulados y `producer` para identificar quién produce la medición.
`src/payload_builder.py` concentra el formato del payload para mantener esta
convención centralizada.

## 7. Qué demuestra esta ejecución

La prueba confirma:

```text
Generador ambiental
  -> construcción del JSON
  -> publicación MQTT con QoS 1
  -> recepción en Mosquitto
  -> lectura por un suscriptor/consumer
```

No demuestra todavía I2C ni el funcionamiento del BME280 físico. Eso se valida
con el firmware del ESP32.

## 8. Detener la infraestructura

```bash
cd infrastructure/mosquitto
docker compose down
```