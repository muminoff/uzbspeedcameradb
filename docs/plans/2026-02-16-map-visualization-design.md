# Camera Map Visualization Design

## Summary

A Python script that reads `data/cameras.json` and generates an interactive HTML map of all 576 speed and traffic cameras in Uzbekistan using Folium (Leaflet.js wrapper).

## Approach

**Folium** — generates a standalone `map.html` with an interactive Leaflet map. No server, no frontend framework.

Alternatives considered:
- FastAPI + Vanilla Leaflet.js — overkill for "just pins"
- FastAPI + SPA (React/Vue/Svelte) — way overkill

## Behavior

- Map centered on Uzbekistan (~41.3, 64.5), zoom level 6
- Each camera = one circle marker
- Color-coded by camera type:
  - Red: `speed_camera`
  - Blue: `alpr`
  - Orange: `traffic_camera`
- Click popup shows: speed limit, camera type, direction, road name
- MarkerCluster groups nearby pins at low zoom levels

## Files

| File | Purpose |
|------|---------|
| `generate_map.py` | Script to generate the map |
| `map.html` | Generated output (gitignored) |

## Dependencies

- `folium` (includes leaflet + markercluster plugin)

## How to Run

```bash
uv run generate_map.py
open map.html
```
