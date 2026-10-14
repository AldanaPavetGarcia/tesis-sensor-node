# Mock Open-Meteo

Simulador de una fuente meteorologica externa compatible con el pipeline ambiental de la tesis.
No consulta Internet: genera localmente datos equivalentes a los que podria aportar Open-Meteo.

## Contrato MQTT

- Topico: `meteo/external/<node_id>`
- QoS: configurable, default 1
- `source`: `mock`
- `producer`: `open_meteo`
- Intervalo simulado por defecto: 900 s (15 min)

Ejemplo:

```json
{
  "node_id": "lit-cordoba-01",
  "timestamp": "2026-10-14T12:00:00Z",
  "source": "mock",
  "producer": "open_meteo",
  "schema_version": "1.0",
  "metrics": {
    "temperature_c": 20.5,
    "humidity_pct": 65.0,
    "pressure_hpa": 1011.2,
    "precipitation_mm": 0.4,
    "wind_speed_kmh": 15.2,
    "cloud_cover_pct": 78.0
  }
}
```

Los campos meteorologicos pueden ser `null` para simular una respuesta incompleta de una API externa.

## Ejecutar tests

Desde esta carpeta, con el entorno virtual activo:

```bash
pytest
```

## Ejecutar el mock

Copiar `.env.example` a `.env`, ajustar `MQTT_HOST` y ejecutar:

```bash
python -m src.main
```

Para una prueba rapida, `TIME_WARP_FACTOR=60` hace que un intervalo simulado de 15 minutos se publique cada 15 segundos reales.
