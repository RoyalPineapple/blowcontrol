# Dyson MQTT Message Analysis

Based on the Dyson Purifier Cool PC1 manual and captured MQTT messages, this document provides a comprehensive breakdown of all status and environmental messages.

## Test Device Information
- **Model**: TP11 (Dyson Purifier Cool PC1)
- **Type**: 438 (Purifier Cool)
- **Serial**: XXX-XX-XXXXXXXX
- **Product Category**: ec (Environmental Control)
- **Connection**: lecAndWifi (Local & WiFi)

## Message Types

### 1. Command Messages (Sent TO device)
- `REQUEST-CURRENT-STATE` - Request current device state
- `REQUEST-CURRENT-FAULTS` - Request current fault status
- `STATE-SET` - Set device state parameters
- `LOCATE` - Request device location/position

### 2. Status Messages (Received FROM device)
- `CURRENT-STATE` - Complete device state snapshot
- `STATE-CHANGE` - State change notification (shows before/after values)
- `ENVIRONMENTAL-CURRENT-SENSOR-DATA` - Air quality sensor readings
- `LOCATION` - Device position response (for oscillation)

## Product State Parameters

### Power & Operation
| Parameter | Description | Values | Notes |
|-----------|-------------|--------|-------|
| `fpwr` | Fan Power | `ON`, `OFF` | Main power state |
| `fnst` | Fan Status | `OFF`, `FAN` | Current fan operation |
| `fnsp` | Fan Speed | `0001`-`0010`, `AUTO` | Speed level (1-10) or auto |
| `auto` | Auto Mode | `ON`, `OFF` | Automatic air quality response |

### Air Quality & Modes
| Parameter | Description | Values | Notes |
|-----------|-------------|--------|-------|
| `nmod` | Night Mode | `ON`, `OFF` | Quiet operation mode |
| `sltm` | Sleep Timer | `OFF`, `0015`-`0540` | Timer in minutes (15-540) |
| `rhtm` | Real-time Monitoring | `ON`, `OFF` | Continuous air quality monitoring |

### Oscillation & Direction
| Parameter | Description | Values | Notes |
|-----------|-------------|--------|-------|
| `oscs` | Oscillation Status | `ON`, `OFF` | Whether oscillating |
| `oson` | Oscillation On | `ON`, `OFF` | Oscillation enabled |
| `osal` | Oscillation Angle Lower | `0005`-`0355` | Start angle (degrees) |
| `osau` | Oscillation Angle Upper | `0005`-`0355` | End angle (degrees) |
| `ancp` | Angle Control Point | `0090`, `CUST` | Fixed 90° or custom range |
| `apos` | Actual Position | `0005`-`0355` | Current fan position (from LOCATION) |

### Display & Interface
| Parameter | Description | Values | Notes |
|-----------|-------------|--------|-------|
| `bril` | Brightness | `0001`-`0010` | LCD screen brightness |
| `wacd` | WiFi Access Code Display | `NONE` | WiFi setup display |

### Device Information
| Parameter | Description | Values | Notes |
|-----------|-------------|--------|-------|
| `nmdv` | Network Mode Device | `0004` | Network configuration |
| `rssi` | WiFi Signal Strength | `-30` to `-50` | Signal strength in dBm |
| `channel` | WiFi Channel | `1`-`11` | Current WiFi channel |

### Filter Status
| Parameter | Description | Values | Notes |
|-----------|-------------|--------|-------|
| `cflr` | Carbon Filter Remaining | `INV` | Carbon filter life remaining |
| `hflr` | HEPA Filter Remaining | `0100` | HEPA filter life (percentage) |
| `cflt` | Carbon Filter Type | `NONE` | Carbon filter type |
| `hflt` | HEPA Filter Type | `GCOM` | HEPA+Carbon combined filter |
| `fqhp` | Filter Quality HP | `0` | Filter quality indicator |
| `fghp` | Filter Grade HP | `0` | Filter grade indicator |

### Scheduler
| Parameter | Description | Values | Notes |
|-----------|-------------|--------|-------|
| `srsc` | Schedule | `0000000000000000` | Weekly schedule bitmap |
| `dstv` | Daylight Saving Time | `0001` | DST setting |
| `tzid` | Timezone ID | `0001` | Timezone identifier |

## Environmental Sensor Data

### Air Quality Measurements
| Parameter | Description | Range | Units | Notes |
|-----------|-------------|-------|-------|-------|
| `pm25` | PM2.5 Particles | `0000`-`9999` | μg/m³ | Particles ≤ 2.5 microns |
| `pm10` | PM10 Particles | `0000`-`9999` | μg/m³ | Particles ≤ 10 microns |
| `p25r` | PM2.5 Running Average | `0000`-`9999` | μg/m³ | 24-hour average |
| `p10r` | PM10 Running Average | `0000`-`9999` | μg/m³ | 24-hour average |
| `sltm` | Sleep Timer Remaining | `OFF`, `0001`-`0540` | minutes | Time left on sleep timer |

### Air Quality Levels (from Manual)
According to the Dyson manual, the device monitors:
- **PM2.5**: Microscopic particles up to 2.5 microns (smoke, allergens)
- **PM10**: Larger particles up to 10 microns (dust, pollen)
- **Real-time monitoring**: Shows last 12 seconds of air quality data
- **Filter life**: Displayed on LCD and indicates when replacement needed

## Message Examples

### Power On/Off
```json
// Turn on
{"data":{"fpwr":"ON"},"msg":"STATE-SET","time":"2025-07-21T18:58:52Z","mode-reason":"RAPP"}

// Response
{"msg":"STATE-CHANGE","product-state":{"fpwr":["OFF","ON"],"fnst":["OFF","FAN"]}}
```

### Fan Speed Control
```json
// Set speed to 5
{"data":{"fnsp":"0005"},"msg":"STATE-SET","time":"2025-07-21T18:59:27Z","mode-reason":"RAPP"}

// Set to auto mode
{"data":{"auto":"ON"},"msg":"STATE-SET","time":"2025-07-21T18:59:09Z","mode-reason":"RAPP"}
```

### Oscillation Control
```json
// Set custom oscillation range (90° to 270°)
{"data":{"osal":"0090","osau":"0270","ancp":"CUST","oson":"ON"},"msg":"STATE-SET"}

// Fixed direction (point to 195°)
{"data":{"osal":"0195","osau":"0195","ancp":"CUST","oson":"ON"},"msg":"STATE-SET"}
```

### Sleep Timer
```json
// Set 45 minute timer
{"data":{"sltm":"0045"},"msg":"STATE-SET","time":"2025-07-21T19:00:29Z","mode-reason":"RAPP"}

// Clear timer
{"data":{"sltm":"OFF"},"msg":"STATE-SET","time":"2025-07-21T19:01:26Z","mode-reason":"RAPP"}
```

### Night Mode
```json
// Enable night mode
{"data":{"nmod":"ON"},"msg":"STATE-SET","time":"2025-07-21T19:00:51Z","mode-reason":"RAPP"}
```

## State Change Format
State changes show before/after values in arrays:
```json
"product-state": {
  "fpwr": ["OFF", "ON"],    // [previous, new]
  "fnst": ["OFF", "FAN"],
  "oscs": ["OFF", "ON"]
}
```

## Error Handling
- Device sends `REQUEST-CURRENT-FAULTS` periodically
- Manual mentions error codes displayed on LCD
- Error recovery: "try turning it off and then on again"

## Network Information
- **MQTT Root Topic**: `438M`
- **Device Topic Pattern**: `438M/{SERIAL}/status/#` and `438M/{SERIAL}/command`
- **WiFi Status**: Shown in device state
- **Signal Strength**: Included in CURRENT-STATE messages

## Filter Management
- **HEPA+Carbon Combined Filter**: Single replaceable filter
- **Filter Life**: Percentage remaining shown in `hflr`
- **Reset Required**: After filter replacement using Night mode button hold
- **Types**: `GCOM` = HEPA+Carbon combined, `INV` = Invalid/needs replacement
