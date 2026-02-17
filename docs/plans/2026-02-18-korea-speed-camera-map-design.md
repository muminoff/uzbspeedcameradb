# Korea Speed Camera Map Visualization — Design

**Date:** 2026-02-18
**Status:** Approved

## Goal

Add an interactive Folium map visualization of South Korea's 41,914 speed/traffic enforcement cameras to this repo, deployed alongside the existing Uzbekistan map on GitHub Pages.

## Data Source

- **File:** `전국무인교통단속카메라표준데이터.csv` (Korean government open data)
- **Encoding:** EUC-KR → converted to UTF-8 for the repo
- **Records:** 41,914 cameras across 17 regions
- **Coordinate coverage:** 99.98% valid
- **Installation years:** 2002–2025

### Key columns (kept in original Korean)

| Column | Meaning |
|--------|---------|
| 무인교통단속카메라관리번호 | Camera ID |
| 시도명 | Province/City |
| 시군구명 | District |
| 도로종류 | Road type |
| 소재지도로명주소 | Street address |
| 위도 / 경도 | Latitude / Longitude |
| 단속구분 | Enforcement type (coded) |
| 제한속도 | Speed limit (km/h) |
| 보호구역구분 | Protected zone type (coded) |
| 설치연도 | Installation year |

### Enforcement type codes (단속구분)

| Code | Meaning | Color |
|------|---------|-------|
| 1 | Speed (속도위반) | red |
| 2 | Signal (신호위반) | blue |
| 3 | Bus lane (버스전용차로) | green |
| 4 | School zone (보호구역) | orange |
| Other/99 | Other | gray |

## Approach

Direct port of the Uzbekistan Folium pattern with `FastMarkerCluster` for 41K-point performance.

### Why FastMarkerCluster

Standard `MarkerCluster` creates individual DOM elements per marker — unusable at 41K. `FastMarkerCluster` renders via canvas, handling large datasets efficiently with clustering at zoom-out.

## Architecture

### New files

```
data/korea_cameras.csv          # UTF-8 dataset (committed)
generate_korea_map.py           # Standalone map generator
korea.html                      # Generated output (GitHub Pages)
```

### No changes to existing files

`generate_map.py`, `main.py`, `index.html` remain untouched.

### Script structure (generate_korea_map.py)

```python
DATA_PATH = Path("data/korea_cameras.csv")
OUTPUT_PATH = Path("korea.html")

ENFORCEMENT_COLORS = { "1": "red", "2": "blue", "3": "green", "4": "orange", default: "gray" }

def load_cameras() -> list[dict]     # Read CSV, filter invalid coords
def build_popup(cam: dict) -> str    # Format popup HTML
def generate_map() -> None           # Build Folium map with FastMarkerCluster
```

### Map configuration

- Center: `[36.5, 127.5]` (geographic center of South Korea)
- Zoom: `7` (full country view)
- Markers: `CircleMarker`, radius 5, colored by enforcement type
- Popup: address, speed limit, enforcement type, installation year, protected zone

## Deployment

Both `index.html` (Uzbekistan) and `korea.html` (Korea) served from the same GitHub Pages site.

```bash
uv run python generate_korea_map.py   # Generate korea.html
```
