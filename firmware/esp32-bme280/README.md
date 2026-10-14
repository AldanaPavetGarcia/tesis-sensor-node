# Firmware ESP32 + BME280

Firmware del nodo ambiental real.

## Flujo

`BME280 -> I2C -> ESP32 -> Wi-Fi/MQTT -> Mosquitto`

## Contrato MQTT

Mediciones:

- Topico: `meteo/sensor/<node_id>`
- QoS: 1
- `source`: `real`
- `producer`: `bme280`

Estado/LWT:

- Topico: `meteo/status/<node_id>`
- Retained: si
- `source`: `real`
- `producer`: `bme280`
- `status`: `online` u `offline`

El mock BME280 utiliza el mismo esquema de mediciones, cambiando solamente
`source` de `real` a `mock`.

## Hardware esperado

- ESP32 / ESP-32S
- BME280 por I2C
- SDA: GPIO 21
- SCL: GPIO 22
- Direccion BME280: `0x76` o `0x77`

Los pines deben confirmarse contra la placa fisica antes de cablear.

## Configuracion

Copiar `include/Secrets.example.h` como `include/Secrets.h` y completar las
credenciales Wi-Fi/MQTT locales.

El broker se configura en `include/AppConfig.h`. Durante desarrollo debe ser
la IP LAN de la PC que ejecuta Mosquitto, nunca `localhost`.

## Compilacion

Desde la raiz del repositorio:

```bash
python -m platformio run -d firmware/esp32-bme280
```

La prueba con hardware se realizara cuando el BME280 fisico este disponible.
Hasta entonces, el objetivo es mantener el firmware compilable y alineado con
el contrato del mock.
