#include "PayloadBuilder.h"

#include <ArduinoJson.h>

#include "AppConfig.h"

namespace PayloadBuilder {

String buildMeasurement(const SensorReading& reading,
                        const String& timestampIso8601) {
  JsonDocument doc;

  doc["node_id"] = AppConfig::NODE_ID;
  doc["timestamp"] = timestampIso8601;
  doc["source"] = "real";
  doc["producer"] = "bme280";
  doc["schema_version"] = "1.0";

  JsonObject metrics = doc["metrics"].to<JsonObject>();
  metrics["temperature_c"] = reading.temperatureC;
  metrics["humidity_pct"] = reading.humidityPct;
  metrics["pressure_hpa"] = reading.pressureHpa;
  metrics["sensor_uid"] = AppConfig::SENSOR_UID;

  String payload;
  serializeJson(doc, payload);
  return payload;
}

String buildStatus(const char* status) {
  JsonDocument doc;
  doc["node_id"] = AppConfig::NODE_ID;
  doc["source"] = "real";
  doc["producer"] = "bme280";
  doc["status"] = status;

  String payload;
  serializeJson(doc, payload);
  return payload;
}

}  // namespace PayloadBuilder
