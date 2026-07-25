# Weather Rendering

Use the Open-Meteo API with `&temperature_unit=fahrenheit`. The API defaults to Celsius; the parameter must be explicit.

Weather is included in **morning briefings only** — omit from evening briefings.

## WMO Weather Code → Emoji Mapping

| Code | Emoji | Description |
|------|-------|-------------|
| 0 | ☀️ | Clear sky |
| 1 | 🌤 | Mainly clear |
| 2 | ⛅ | Partly cloudy |
| 3 | ☁️ | Overcast |
| 45, 48 | 🌫 | Fog |
| 51, 53, 55 | 🌦 | Drizzle |
| 61, 63, 65 | 🌧 | Rain |
| 71, 73, 75 | 🌨 | Snow |
| 80, 81, 82 | 🌦 | Rain showers |
| 95 | ⛈ | Thunderstorm |

## Weather Line Content

Weather follows greeting as narrative prose with emoji directly before each condition word.

Include: current temp and condition, 10am commute forecast, high, 4pm commute forecast, low. Friday briefings append a weekend forecast line.

Location callout: omit when at home. When traveling, prefix with location: "Here's what Tokyo looks like today."