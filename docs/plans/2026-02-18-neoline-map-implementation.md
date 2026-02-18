# NEOLINE Speed Camera Map Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate an interactive Leaflet map (`neoline.html`) visualizing 91,437 NEOLINE radar detector POIs across Russia/CIS/Eastern Europe.

**Architecture:** Python script (`generate_neoline_map.py`) reads CSV, builds Folium FastMarkerCluster map with color-coded POI types and directional markers, outputs standalone HTML. Mirrors `generate_korea_map.py` pattern exactly.

**Tech Stack:** Python 3.14, Folium (0.20+), FastMarkerCluster, Leaflet.js

---

### Task 1: Copy data file into project

**Files:**
- Copy: `/Users/sardor/Projects/neonline/X-COP_7500s_Baza_GPS_decoded.csv` -> `data/X-COP_7500s_Baza_GPS_decoded.csv`

**Step 1: Copy the CSV**

```bash
cp /Users/sardor/Projects/neonline/X-COP_7500s_Baza_GPS_decoded.csv data/X-COP_7500s_Baza_GPS_decoded.csv
```

**Step 2: Verify the copy**

```bash
wc -l data/X-COP_7500s_Baza_GPS_decoded.csv
```

Expected: `91438` (91,437 data rows + 1 header)

**Step 3: Commit**

```bash
git add data/X-COP_7500s_Baza_GPS_decoded.csv
git commit -m "Add NEOLINE X-COP 7500s decoded camera database (91,437 records)"
```

---

### Task 2: Create generate_neoline_map.py — data loading and popup builder

**Files:**
- Create: `generate_neoline_map.py`

This task creates the script with constants, `load_cameras()`, and `build_popup()`. The `generate_map()` function is added in Task 3.

**Step 1: Create the file with imports, constants, and load_cameras()**

```python
import csv
from pathlib import Path

import folium
from folium.plugins import FastMarkerCluster

DATA_PATH = Path(__file__).parent / "data" / "X-COP_7500s_Baza_GPS_decoded.csv"
OUTPUT_PATH = Path(__file__).parent / "neoline.html"

POI_TYPE_COLORS = {
    "0xA5": "red",
    "0xE0": "blue",
    "0xE7": "green",
    "0xE8": "orange",
    "0x97": "purple",
    "0xA8": "cyan",
    "0xE6": "brown",
    "0xE9": "pink",
}

DEFAULT_COLOR = "gray"


def load_cameras() -> list[dict]:
    cameras = []
    with open(DATA_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row["latitude"])
                lon = float(row["longitude"])
            except (ValueError, KeyError):
                continue
            row["_lat"] = lat
            row["_lon"] = lon
            cameras.append(row)
    return cameras


def build_popup(cam: dict) -> str:
    lines = []
    lines.append(f"<b>POI Type:</b> {cam.get('poi_type', 'unknown')}")
    direction = "Reverse" if cam.get("direction") == "1" else "Forward"
    lines.append(f"<b>Direction:</b> {direction}")
    lines.append(f"<b>Category:</b> {cam.get('category', 'unknown')}")
    lines.append(f"<b>Byte10:</b> {cam.get('byte10', '')}")
    lines.append(f"<b>Byte21/22/23:</b> {cam.get('byte21', '')} / {cam.get('byte22', '')} / {cam.get('byte23', '')}")
    raw = cam.get("raw_hex", "")
    if raw:
        lines.append(f"<b>Raw:</b> <code>{raw[:24]}...</code>")
    lines.append(f"<b>Coords:</b> {cam['_lat']:.6f}, {cam['_lon']:.6f}")
    return "<br>".join(lines)
```

**Step 2: Verify it loads**

```bash
cd /Users/sardor/Projects/uzbspeedcameradb
.venv/bin/python -c "from generate_neoline_map import load_cameras, build_popup; cams = load_cameras(); print(f'{len(cams)} cameras loaded'); print(build_popup(cams[0]))"
```

Expected: `91437 cameras loaded` followed by HTML popup content.

**Step 3: Commit**

```bash
git add generate_neoline_map.py
git commit -m "Add NEOLINE map generator: data loading and popup builder"
```

---

### Task 3: Add generate_map() with FastMarkerCluster and directional markers

**Files:**
- Modify: `generate_neoline_map.py` (append `generate_map()` and `__main__` block)

**Step 1: Add generate_map() function**

Append this to the end of `generate_neoline_map.py`:

```python
def generate_map() -> None:
    cameras = load_cameras()

    m = folium.Map(location=[55.0, 60.0], zoom_start=4)

    data = []
    for cam in cameras:
        lat = cam["_lat"]
        lon = cam["_lon"]
        poi_type = cam.get("poi_type", "").strip()
        color = POI_TYPE_COLORS.get(poi_type, DEFAULT_COLOR)
        popup_html = build_popup(cam)
        direction = "reverse" if cam.get("direction") == "1" else "forward"
        data.append([lat, lon, color, popup_html, direction])

    callback = """\
function (row) {
    var color = row[2];
    var dir = row[4];
    var marker;
    if (dir === 'forward') {
        marker = L.circleMarker(new L.LatLng(row[0], row[1]), {
            radius: 5,
            color: color,
            fillColor: color,
            fillOpacity: 0.7,
            weight: 1
        });
    } else {
        var svg = '<svg width="12" height="18" viewBox="0 0 12 18">' +
            '<polygon points="0,0 12,0 6,18" fill="' + color + '" stroke="#333" stroke-width="1"/>' +
            '</svg>';
        var icon = L.divIcon({
            html: svg,
            className: '',
            iconSize: [12, 18],
            iconAnchor: [6, 0]
        });
        marker = L.marker(new L.LatLng(row[0], row[1]), {icon: icon});
    }
    marker.bindPopup(row[3], {maxWidth: 300});
    return marker;
}"""

    FastMarkerCluster(data=data, callback=callback).add_to(m)

    m.save(str(OUTPUT_PATH))
    print(f"Map saved to {OUTPUT_PATH} ({len(cameras)} cameras)")


if __name__ == "__main__":
    generate_map()
```

**Step 2: Run the generator**

```bash
cd /Users/sardor/Projects/uzbspeedcameradb
.venv/bin/python generate_neoline_map.py
```

Expected: `Map saved to /Users/sardor/Projects/uzbspeedcameradb/neoline.html (91437 cameras)`

**Step 3: Verify the output file exists and has reasonable size**

```bash
ls -lh neoline.html
```

Expected: File exists, roughly 15-30 MB (similar scale to korea.html at 28 MB).

**Step 4: Commit**

```bash
git add generate_neoline_map.py
git commit -m "Add map generation with FastMarkerCluster and directional markers"
```

---

### Task 4: Generate final HTML and commit

**Files:**
- Generated: `neoline.html`

**Step 1: Open the map in browser and visually verify**

Use Playwright MCP to open `neoline.html` and verify:
- Map loads centered on Russia
- Markers are visible and clustered
- Clicking a cluster expands it
- Clicking a marker shows popup with all fields
- Red markers (0xA5) are the most frequent
- Triangle markers appear for reverse-direction POIs

**Step 2: Commit the generated HTML**

```bash
git add neoline.html
git commit -m "Add generated NEOLINE speed camera interactive map (91,437 POIs)"
```

---

### Task 5: Final verification

**Step 1: Verify all files are committed**

```bash
git status
git log --oneline -5
```

Expected: Clean working tree. Recent commits show the 4 commits from this plan.

**Step 2: Open both maps side by side to confirm consistency**

Use Playwright MCP to open `neoline.html` and `korea.html` to verify they follow the same UX pattern (clustering, popups, directional markers).
