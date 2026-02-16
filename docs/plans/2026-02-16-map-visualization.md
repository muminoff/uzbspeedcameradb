# Map Visualization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate an interactive HTML map showing all 576 speed/traffic cameras in Uzbekistan using Folium.

**Architecture:** A single Python script reads `data/cameras.json`, creates a Folium map with color-coded clustered markers and click popups, and writes `map.html`.

**Tech Stack:** Python 3.14, Folium, uv

---

### Task 1: Add folium dependency

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add folium via uv**

Run: `uv add folium`

**Step 2: Verify installation**

Run: `uv run python -c "import folium; print(folium.__version__)"`
Expected: Version number printed without error.

**Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "Add folium dependency"
```

---

### Task 2: Add map.html to .gitignore

**Files:**
- Modify: `.gitignore`

**Step 1: Add map.html to gitignore**

Append `map.html` to `.gitignore`.

**Step 2: Commit**

```bash
git add .gitignore
git commit -m "Add map.html to gitignore"
```

---

### Task 3: Write generate_map.py

**Files:**
- Create: `generate_map.py`

**Step 1: Write the script**

```python
import json
from pathlib import Path

import folium
from folium.plugins import MarkerCluster

DATA_PATH = Path(__file__).parent / "data" / "cameras.json"
OUTPUT_PATH = Path(__file__).parent / "map.html"

COLOR_MAP = {
    "speed_camera": "red",
    "alpr": "blue",
    "traffic_camera": "orange",
}


def load_cameras() -> list[dict]:
    with open(DATA_PATH) as f:
        return json.load(f)


def build_popup(cam: dict) -> str:
    lines = []
    if cam.get("speed_limit"):
        lines.append(f"<b>Speed limit:</b> {cam['speed_limit']} km/h")
    lines.append(f"<b>Type:</b> {cam.get('camera_type', 'unknown')}")
    if cam.get("compass_direction"):
        lines.append(f"<b>Direction:</b> {cam['compass_direction']}")
    if cam.get("road_direction"):
        lines.append(f"<b>Road:</b> {cam['road_direction']}")
    return "<br>".join(lines)


def generate_map() -> None:
    cameras = load_cameras()

    m = folium.Map(location=[41.3, 64.5], zoom_start=6)
    cluster = MarkerCluster().add_to(m)

    for cam in cameras:
        color = COLOR_MAP.get(cam.get("camera_type", ""), "gray")
        folium.CircleMarker(
            location=[cam["latitude"], cam["longitude"]],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(build_popup(cam), max_width=250),
        ).add_to(cluster)

    m.save(str(OUTPUT_PATH))
    print(f"Map saved to {OUTPUT_PATH} ({len(cameras)} cameras)")


if __name__ == "__main__":
    generate_map()
```

**Step 2: Run the script**

Run: `uv run generate_map.py`
Expected: `Map saved to /path/to/map.html (576 cameras)`

**Step 3: Open in browser and verify**

Run: `open map.html`
Expected: Interactive map of Uzbekistan with colored clustered pins. Click a pin to see popup with camera details.

**Step 4: Commit**

```bash
git add generate_map.py
git commit -m "Add generate_map.py script for Folium visualization"
```

---

### Task 4: Clean up main.py

**Files:**
- Modify: `main.py`

**Step 1: Update main.py to call generate_map**

Replace the placeholder content in `main.py` with an import that calls `generate_map()`, so `uv run main.py` also generates the map.

```python
from generate_map import generate_map

if __name__ == "__main__":
    generate_map()
```

**Step 2: Test**

Run: `uv run main.py`
Expected: Same output as `uv run generate_map.py`.

**Step 3: Commit**

```bash
git add main.py
git commit -m "Wire main.py to generate_map"
```
