# Módulo de Sensores Ambientales — Documentación de la parte individual

## 1. Objetivo

El módulo de sensores ambientales incorpora mediciones meteorológicas al testbed LEO/Starlink para que luego puedan almacenarse, visualizarse y compararse con las métricas de red.

La responsabilidad individual de este módulo cubre la generación de datos ambientales de prueba, la definición del contrato MQTT y el firmware básico del nodo físico basado en ESP32 + BME280.

## 2. Arquitectura general

### Camino con sensor físico

```text
BME280
  │ I2C
  ▼
ESP32
  │ Wi-Fi / MQTT
  ▼
Mosquitto
  │
  ▼
Consumer / Router
  │
  ▼
TimescaleDB
  │
  ▼
Grafana / API
```

### Camino con mock BME280

```text
Mock BME280 (Python)
  │ MQTT
  ▼
Mosquitto
  │
  ▼
Consumer / Router
  │
  ▼
TimescaleDB
```

El mock reemplaza temporalmente al conjunto BME280 + ESP32. No simula I2C: publica directamente por MQTT.

## 3. Identidad del dato: `source` y `producer`

Se adoptó la siguiente semántica:

- `source`: indica si el dato es real o simulado.
  - `real`
  - `mock`
- `producer`: indica quién genera u origina el dato.
  - `bme280`
  - `open_meteo`
  - otros productores futuros

Ejemplos:

```json
{
  "source": "mock",
  "producer": "bme280"
}
```

```json
{
  "source": "real",
  "producer": "bme280"
}
```

```json
{
  "source": "mock",
  "producer": "open_meteo"
}
```

Esta separación permite mantener el mismo esquema lógico cuando se reemplaza un simulador por una fuente real.

## 4. Tópicos MQTT

### BME280

Mediciones:

```text
meteo/sensor/<node_id>
```

Ejemplo:

```text
meteo/sensor/lit-cordoba-01
```

Estado / heartbeat / LWT:

```text
meteo/status/<node_id>
```

La separación del tópico de estado ambiental evita colisiones con otros dominios, por ejemplo Starlink.

### Fuente meteorológica externa

```text
meteo/external/<node_id>
```

Ejemplo:

```text
meteo/external/lit-cordoba-01
```

## 5. Mock BME280

El mock BME280 está implementado en Python y permite probar el pipeline sin disponer del sensor físico.

Responsabilidades principales:

- generar temperatura, humedad y presión;
- producir variaciones temporales controladas;
- publicar periódicamente por MQTT;
- soportar aceleración temporal mediante `TIME_WARP_FACTOR`;
- publicar con el mismo contrato utilizado por el firmware físico;
- utilizar `source = "mock"` y `producer = "bme280"`.

El mock permite desacoplar el desarrollo de la infraestructura del momento en que esté disponible el hardware real.

## 6. Mock Open-Meteo

Se incorporó un segundo generador que representa una fuente meteorológica externa.

Publica en:

```text
meteo/external/<node_id>
```

y agrega variables como:

- precipitación;
- velocidad del viento;
- cobertura nubosa;
- temperatura;
- humedad;
- presión.

En este caso:

```text
source = mock
producer = open_meteo
```

También contempla campos `null` para representar datos que una API externa podría no entregar.

## 7. Firmware ESP32 + BME280

El firmware físico está desarrollado para ESP32 utilizando PlatformIO y Arduino framework.

Su camino de datos es:

```text
BME280 --I2C--> ESP32 --Wi-Fi/MQTT--> broker
```

Responsabilidades principales:

- inicializar el BME280 por I2C;
- conectarse a Wi-Fi;
- sincronizar hora;
- conectarse al broker MQTT;
- publicar las mediciones ambientales;
- publicar heartbeat;
- utilizar LWT para indicar una desconexión inesperada;
- aplicar reconexión con backoff.

El contrato del firmware quedó alineado con el mock:

```text
source = real
producer = bme280
```

Mediciones:

```text
meteo/sensor/<node_id>
```

Estado:

```text
meteo/status/<node_id>
```

El firmware fue compilado correctamente con PlatformIO para `esp32dev`.

## 8. Por qué existen mocks y versión real

Los mocks no son el producto final. Son herramientas de desacoplamiento.

Permiten desarrollar y verificar:

```text
MQTT -> Consumer -> Base de datos -> Visualización
```

sin depender de que el sensor, la ESP32 o la estación real estén físicamente disponibles.

Cuando se conecta el hardware real, el resto del sistema no debería necesitar rediseñarse. La diferencia principal es:

```text
Mock:
source = mock

Hardware:
source = real
```

El productor continúa siendo:

```text
producer = bme280
```

## 9. Estado de la parte individual

Quedaron implementados:

- contrato ambiental MQTT;
- mock BME280;
- pruebas unitarias del mock BME280;
- Dockerfile y configuración del mock;
- mock de fuente Open-Meteo;
- pruebas del mock Open-Meteo;
- firmware ESP32 + BME280;
- alineación del firmware con el contrato actual;
- compilación exitosa del firmware;
- documentación del módulo.

## 10. Qué no pertenece al cierre individual

La conexión física completa del BME280 y las pruebas extremo a extremo forman parte de la etapa de integración.

Entre las tareas posteriores se encuentran:

```text
ESP32 + BME280 físico
        │
        ▼
Mosquitto compartido
        │
        ▼
Consumer
        │
        ▼
TimescaleDB
        │
        ▼
Grafana
```

También quedan para integración:

- persistencia de datos ambientales;
- pruebas E2E;
- despliegue en Raspberry Pi 5;
- operación con Starlink real;
- campaña de medición;
- análisis y correlación de datos.

## 11. Cómo explicar este módulo oralmente

Una explicación corta puede ser:

> Mi parte fue desarrollar la fuente de datos ambientales del sistema. Primero definimos un contrato MQTT común para desacoplar la fuente de la infraestructura. Implementé un mock del BME280 para que el pipeline pudiera desarrollarse sin hardware, y un mock de una fuente meteorológica externa. Después alineé el firmware de la ESP32 con el mismo contrato. De esa forma, cambiar del mock al sensor físico no obliga a modificar el consumer ni la arquitectura: ambos publican el mismo tipo de dato y se distinguen mediante `source`, mientras `producer` identifica el origen.

Si preguntan por qué se usa MQTT:

> Porque desacopla productores y consumidores. El ESP32 o los mocks solamente publican; no necesitan conocer la base de datos ni Grafana.

Si preguntan por qué existen `source` y `producer`:

> `source` distingue datos reales de simulados y `producer` identifica qué componente los originó. Esto permite comparar mock y hardware sin cambiar el contrato.

Si preguntan qué falta para tener datos reales:

> Conectar físicamente el BME280 al ESP32, cargar credenciales y dirección del broker, flashear el firmware y verificar que las publicaciones reales lleguen al pipeline compartido.
