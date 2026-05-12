import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Phoenix, AZ
LAT, LON = 33.4484, -112.0740
TIMEZONE = "America%2FPhoenix"

url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}"
    "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
    "wind_speed_10m,uv_index"
    "&hourly=apparent_temperature,temperature_2m"
    "&past_hours=6"
    "&forecast_hours=18"
    f"&timezone={TIMEZONE}"
)

response = requests.get(url, timeout=30)
response.raise_for_status()
data = response.json()

current = data["current"]
now_temp = current["temperature_2m"]
feels_like = current["apparent_temperature"]
humidity = current["relative_humidity_2m"]
wind_speed = current["wind_speed_10m"]
uv_index = current.get("uv_index", "N/A")
updated_at = current["time"]

times_raw = data["hourly"]["time"]
temps = data["hourly"]["temperature_2m"]
feels = data["hourly"]["apparent_temperature"]
times = [datetime.strptime(t, "%Y-%m-%dT%H:%M") for t in times_raw]

now_hour = updated_at[:13]
past_mask = [t[:13] <= now_hour for t in times_raw]

past_times = [t for t, is_past in zip(times, past_mask) if is_past]
past_feels = [v for v, is_past in zip(feels, past_mask) if is_past]

future_times = [t for t, is_past in zip(times, past_mask) if not is_past]
future_feels = [v for v, is_past in zip(feels, past_mask) if not is_past]


def walking_risk(value_c):
    if value_c >= 43:
        return "Extreme"
    if value_c >= 38:
        return "High"
    if value_c >= 32:
        return "Moderate"
    return "Low"


risk = walking_risk(feels_like)
uncomfortable_hours = sum(1 for v in future_feels if v is not None and v >= 32)
high_risk_hours = sum(1 for v in future_feels if v is not None and v >= 38)

# Plot
fig, ax = plt.subplots(figsize=(11, 4))

ax.plot(past_times, past_feels, linewidth=2.5, label="Past apparent temperature")
ax.plot(future_times, future_feels, linewidth=2.2, linestyle="--", label="Forecast apparent temperature")

if past_times:
    ax.axvline(x=past_times[-1], linestyle=":", linewidth=1.2, label="Now")

ax.axhline(32, linestyle="--", linewidth=1, label="Moderate walking risk")
ax.axhline(38, linestyle="--", linewidth=1, label="High walking risk")

ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))

plt.xticks(rotation=45)
ax.set_title("Phoenix Walkability Weather Risk — Past 6h + Next 18h", fontsize=13, pad=10)
ax.set_ylabel("Apparent temperature / feels-like (°C)")
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.legend(loc="upper right", fontsize=8)

plt.tight_layout()
plt.savefig("walkability_weather.png", dpi=150)
plt.close()

updated_fmt = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M").strftime("%b %d, %Y at %H:%M")

summary = f"""# 🚶 Phoenix Walkability Weather Risk — Live

Updated: **{updated_fmt} Phoenix time**

| Metric | Value |
|---|---:|
| Air temperature | {now_temp}°C |
| Feels-like temperature | {feels_like}°C |
| Relative humidity | {humidity}% |
| Wind speed | {wind_speed} km/h |
| UV index | {uv_index} |
| Current walking risk | **{risk}** |
| Uncomfortable walking hours in next 18h | {uncomfortable_hours} hours |
| High-risk walking hours in next 18h | {high_risk_hours} hours |

## Risk interpretation

| Risk level | Feels-like temperature |
|---|---|
| Low | < 32°C |
| Moderate | 32–37.9°C |
| High | 38–42.9°C |
| Extreme | ≥ 43°C |

_This live snapshot connects weather conditions with pedestrian infrastructure usability. A sidewalk may exist physically, but extreme heat can reduce whether people can safely and comfortably use it._

_Auto-updated every 2 hours via GitHub Actions._
"""

with open("walkability_weather.md", "w", encoding="utf-8") as f:
    f.write(summary)

print(summary)
