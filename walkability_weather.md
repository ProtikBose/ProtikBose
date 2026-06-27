# 🚶 Phoenix Walkability Weather Risk — Live

Updated: **Jun 27, 2026 at 12:30 Phoenix time**

| Metric | Value |
|---|---:|
| Air temperature | 39.7°C |
| Feels-like temperature | 37.8°C |
| Relative humidity | 10% |
| Wind speed | 18.2 km/h |
| UV index | 8.75 |
| Current walking risk | **Moderate** |
| Uncomfortable walking hours in next 18h | 7 hours |
| High-risk walking hours in next 18h | 0 hours |
| Extreme-risk walking hours in next 18h | 0 hours |

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
