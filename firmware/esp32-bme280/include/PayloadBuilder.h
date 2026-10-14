#pragma once

#include <Arduino.h>

#include "SensorReading.h"

namespace PayloadBuilder {

String buildMeasurement(const SensorReading& reading,
                        const String& timestampIso8601);

String buildStatus(const char* status);

}  // namespace PayloadBuilder
