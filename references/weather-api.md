# Weather API Reference

## Working Method: Open-Meteo Direct

The RapidAPI `weather` endpoint is unreliable for Vesper's morning briefings (the `current-weather` action returns "tool not found"). Use `curl` directly to Open-Meteo.

### San Francisco Morning Weather Query

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=37.7749&longitude=-122.4194&current=temperature_2m,weather_code&hourly=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min,weather_code&temperature_unit=fahrenheit&timezone=America%2FLos_Angeles&forecast_days=2"
```

### Parse with Python

```python
import json, sys
d = json.load(sys.stdin)
c = d['current']
print(f"Current: {c['temperature_2m']}°F, code {c['weather_code']}")
h = d['hourly']
for i, t in enumerate(h['time']):
    if 'T10:00' in t: print(f"10am: {h['temperature_2m'][i]}°F, code {h['weather_code'][i]}")
    if 'T16:00' in t: print(f"4pm: {h['temperature_2m'][i]}°F, code {h['weather_code'][i]}")
for i, day in enumerate(d['daily']['time']):
    print(f"Day {day}: high {d['daily']['temperature_2m_max'][i]}°F, low {d['daily']['temperature_2m_min'][i]}°F, code {d['daily']['weather_code'][i]}")
```

### Key Parameters

| Parameter | Value | Notes |
|---|---|---|
| `latitude` | 37.7749 | San Francisco |
| `longitude` | -122.4194 | San Francisco |
| `current` | `temperature_2m,weather_code` | Separate params, comma-separated in query string |
| `hourly` | `temperature_2m,weather_code` | Same |
| `daily` | `temperature_2m_max,temperature_2m_min,weather_code` | Same |
| `temperature_unit` | `fahrenheit` | Default is Celsius — must be explicit |
| `timezone` | `America%2FLos_Angeles` | URL-encoded slash |
| `forecast_days` | 2 | Today + tomorrow |

### Common Mistake

Do NOT use `temperature_weather_code` as a single parameter — it's not valid. The API returns a confusing error about "SurfacePressureAndHeightVariable". Use `temperature_2m` and `weather_code` as separate comma-separated values in the query string.

### WMO Weather Code Mapping

See `weather-codes.md` for the full emoji mapping. Key ones for SF:
- 0 → ☀️ clear sky
- 1 → 🌤 mainly clear
- 3 → ☁️ overcast
- 45, 48 → 🌫 fog
- 61, 63, 65 → 🌧 rain
