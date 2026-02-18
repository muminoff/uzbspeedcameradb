# NEOLINE X-COP 7500s Speed Camera Map

## Overview

Add a new interactive map page visualizing 91,437 speed camera/POI locations from a NEOLINE X-COP 7500s radar detector database. The data covers Eastern Europe through Far East Russia (lat 46-69N, lon 16-178E).

## Data Source

- **File:** `data/X-COP_7500s_Baza_GPS_decoded.csv` (copied from `/Users/sardor/Projects/neonline/`)
- **Records:** 91,437
- **Columns:** id, latitude, longitude, poi_type, direction, category, byte10, byte21, byte22, byte23, raw_hex
- **Origin:** Reverse-engineered from proprietary BRMSC binary format

## Approach

FastMarkerCluster via Folium — same pattern as `generate_korea_map.py`. Proven at scale (41K Korea cameras), handles 91K comfortably.

### Alternatives considered

| Approach | Why not |
|----------|---------|
| CircleMarker + MarkerCluster | Too slow at 91K points |
| Heatmap + click layer | Loses individual point detail |

## Architecture

- **New file:** `generate_neoline_map.py`
- **Output:** `neoline.html`
- **Data:** `data/X-COP_7500s_Baza_GPS_decoded.csv`
- **Pattern:** Mirrors `generate_korea_map.py` structure exactly

## Visual Encoding

### POI Type Colors (top 8 by frequency)

| Code | Count | Color |
|------|-------|-------|
| 0xA5 | 22,875 | red |
| 0xE0 | 9,482 | blue |
| 0xE7 | 7,788 | green |
| 0xE8 | 7,011 | orange |
| 0x97 | 6,274 | purple |
| 0xA8 | 5,291 | cyan |
| 0xE6 | 4,855 | brown |
| 0xE9 | 2,947 | pink |
| Others | ~24,914 | gray |

### Direction Markers

- `direction=0` (forward/both): circle marker
- `direction=1` (reverse): triangle marker pointing down

## Popup Content

All decoded fields displayed:

- POI Type (hex)
- Direction (Forward/Reverse)
- Category (hex)
- Byte10, Byte21, Byte22, Byte23
- Raw hex
- Coordinates (lat, lon)

## Map Defaults

- **Center:** [55.0, 60.0] (central Russia)
- **Zoom:** 4 (shows full geographic extent)
