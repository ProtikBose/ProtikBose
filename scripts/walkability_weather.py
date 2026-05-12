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

# Split past vs future on the current hour
now_hour = updated_at[:13]  # "YYYY-MM-DDTHH"
past_mask = [t[:13] <= now_hour for t in times_raw]

past_times  = [t for t, p in zip(times, past_mask) if p]
past_feels  = [v for v, p in zip(feels, past_mask) if p]
future_times = [t for t, p in zip(times, past_mask) if not p]
future_feels = [v for v, p in zip(feels, past_mask) if not p]


def walking_risk(value_c):
    if value_c is None:
        return "Unknown"
    if value_c >= 43:
        return "Extreme"
    if value_c >= 38:
        return "High"
    if value_c >= 32:
        return "Moderate"
    return "Low"


risk = walking_risk(feels_like)
uncomfortable_hours = sum(1 for v in future_feels if v is not None and v >= 32)
high_risk_hours    = sum(1 for v in future_feels if v is not None and v >= 38)
extreme_hours      = sum(1 for v in future_feels if v is not None and v >= 43)

# ---- Plot ----
fig, ax = plt.subplots(figsize=(11, 4.5))

ax.plot(past_times, past_feels,
        linewidth=2.5, color="#1f77b4",
        label="Past apparent temperature")
ax.plot(future_times, future_feels,
        linewidth=2.2, linestyle="--", color="#ff7f0e",
        label="Forecast apparent temperature")

if past_times:
    ax.axvline(x=past_times[-1], linestyle=":", linewidth=1.2,
               color="black", label="Now")

ax.axhspan(32, 38, alpha=0.08, color="orange")
ax.axhspan(38, 43, alpha=0.10, color="red")
ax.axhspan(43, 60, alpha=0.15, color="darkred")

ax.axhline(32, linestyle="--", linewidth=1, color="orange")
ax.axhline(38, linestyle="--", linewidth=1, color="red")
ax.axhline(43, linestyle="--", linewidth=1, color="darkred")

ax.text(0.005, 32, " Moderate (32°C)", va="bottom", ha="left",
        transform=ax.get_yaxis_transform(), fontsize=8, color="darkorange")
ax.text(0.005, 38, " High (38°C)", va="bottom", ha="left",
        transform=ax.get_yaxis_transform(), fontsize=8, color="red")
ax.text(0.005, 43, " Extreme (43°C)", va="bottom", ha="left",
        transform=ax.get_yaxis_transform(), fontsize=8, color="darkred")

ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
plt.xticks(rotation=45)

ax.set_title("Phoenix Walkability Weather Risk — Past 6h + Next 18h",
             fontsize=13, pad=10)
ax.set_ylabel("Apparent temperature / feels-like (°C)")
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.legend(loc="upper right", fontsize=8)

plt.tight_layout()
plt.savefig("walkability_weather.png", dpi=150)
plt.close()

# ---- Markdown report ----
updated_fmt = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M").strftime(
    "%b %d, %Y at %H:%M"
)

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
| Extreme-risk walking hours in next 18h | {extreme_hours} hours |

## Why apparent temperature, not air temperature?

A thermometer reading alone does not predict how a body experiences heat outdoors. Two days at 38°C can feel completely different depending on humidity, sun exposure, and wind:

- **Humidity** suppresses sweat evaporation, so the body cannot shed heat efficiently. 38°C at 50% humidity is physiologically harsher than 38°C at 10%.
- **Solar radiation** adds direct radiative load on skin and clothing — the difference between standing in shade and in direct sun can be several degrees of perceived heat.
- **Wind** accelerates convective cooling when air is cooler than skin, and accelerates heating when air is hotter than skin.

Open-Meteo's `apparent_temperature` combines these inputs (air temperature, humidity, wind, and shortwave radiation) into a single number that better reflects what a pedestrian actually experiences on a sidewalk. For a walkability indicator, that is the relevant signal — not the raw air temperature.

## How the walking-risk thresholds were chosen

The thresholds are drawn from established heat-stress guidance for outdoor exposure, simplified into four bands:

| Risk level | Feels-like temperature | Rationale |
|---|---|---|
| Low | < 32°C | Most healthy adults can walk comfortably. |
| Moderate | 32–37.9°C | Sustained walking causes meaningful sweat loss; vulnerable groups (children, older adults, people with cardiovascular conditions) should limit exposure. Aligns with the lower bound of the US National Weather Service "Caution" heat index range. |
| High | 38–42.9°C | Heat exhaustion becomes likely with prolonged exposure. Corresponds to the NWS "Extreme Caution" and "Danger" range. Outdoor activity should be shortened and shaded. |
| Extreme | ≥ 43°C | Heat stroke is a real risk even with short exposure. NWS "Extreme Danger". Walking trips should be deferred or moved indoors. |

These are pedestrian-oriented thresholds. They are stricter than thresholds used for, say, marathon runners (who self-select for fitness) but looser than those used for clinical heat-vulnerability assessments — they target a typical person making a short utilitarian trip on foot.

The counters in the table above use the same bands:
- *Uncomfortable hours* counts any forecast hour with feels-like ≥ 32°C.
- *High-risk hours* counts hours at ≥ 38°C.
- *Extreme-risk hours* counts hours at ≥ 43°C.

---

_This live snapshot connects weather conditions with pedestrian infrastructure usability. A sidewalk may exist physically, but extreme heat can reduce whether people can safely and comfortably use it._

_Auto-updated every 3 hours via GitHub Actions._
"""

with open("walkability_weather.md", "w", encoding="utf-8") as f:
    f.write(summary)

print(summary)
