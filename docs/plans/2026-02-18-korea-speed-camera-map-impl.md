# Korea Speed Camera Map — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an interactive Folium map of South Korea's 41,914 speed/traffic enforcement cameras, deployed as `korea.html` on GitHub Pages.

**Architecture:** Convert the Korean government CSV (EUC-KR) to UTF-8 and commit it as `data/korea_cameras.csv`. A standalone `generate_korea_map.py` reads this CSV, builds a Folium map using `FastMarkerCluster` with a JavaScript callback for CircleMarkers colored by enforcement type, and saves `korea.html`.

**Tech Stack:** Python 3.14+, Folium (already installed), `FastMarkerCluster` plugin, CSV stdlib module.

---

### Task 1: Convert and commit the Korean camera dataset

**Files:**
- Create: `data/korea_cameras.csv`

**Step 1: Convert CSV from EUC-KR to UTF-8**

```bash
iconv -f euc-kr -t utf-8 "/Users/sardor/Downloads/전국무인교통단속카메라표준데이터.csv" > data/korea_cameras.csv
```

**Step 2: Verify the converted file**

```bash
head -2 data/korea_cameras.csv
wc -l data/korea_cameras.csv
```

Expected: First line shows Korean column headers in readable UTF-8. Line count: 41914.

**Step 3: Commit**

```bash
git add data/korea_cameras.csv
git commit -m "Add Korea speed camera dataset (41,913 cameras, UTF-8)"
```

---

### Task 2: Create generate_korea_map.py with data loading

**Files:**
- Create: `generate_korea_map.py`

**Step 1: Create the script with imports, constants, and load function**

```python
import csv
from pathlib import Path

import folium
from folium.plugins import FastMarkerCluster

DATA_PATH = Path(__file__).parent / "data" / "korea_cameras.csv"
OUTPUT_PATH = Path(__file__).parent / "korea.html"

ENFORCEMENT_COLORS = {
    "1": "red",      # 속도위반 (speed)
    "2": "blue",     # 신호위반 (signal)
    "3": "green",    # 버스전용차로 (bus lane)
    "4": "orange",   # 보호구역 (school zone)
}

ENFORCEMENT_LABELS = {
    "1": "속도위반 (Speed)",
    "2": "신호위반 (Signal)",
    "3": "버스전용차로 (Bus lane)",
    "4": "보호구역 (School zone)",
}

DEFAULT_COLOR = "gray"


def load_cameras() -> list[dict]:
    cameras = []
    with open(DATA_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row["위도"])
                lon = float(row["경도"])
            except (ValueError, KeyError):
                continue
            if lat < 33 or lat > 39 or lon < 124 or lon > 132:
                continue
            cameras.append(row)
    return cameras
```

**Step 2: Verify data loads correctly**

```bash
uv run python -c "from generate_korea_map import load_cameras; cams = load_cameras(); print(f'Loaded {len(cams)} cameras')"
```

Expected: `Loaded ~41900 cameras` (a few filtered out for invalid coords).

**Step 3: Commit**

```bash
git add generate_korea_map.py
git commit -m "Add Korea map generator with data loading"
```

---

### Task 3: Add popup builder and map generation

**Files:**
- Modify: `generate_korea_map.py`

**Step 1: Add build_popup and generate_map functions**

Append to `generate_korea_map.py`:

```python
def build_popup(cam: dict) -> str:
    lines = []
    speed = cam.get("제한속도", "").strip()
    if speed and speed != "0":
        lines.append(f"<b>제한속도:</b> {speed} km/h")
    code = cam.get("단속구분", "").strip()
    label = ENFORCEMENT_LABELS.get(code, code)
    lines.append(f"<b>단속구분:</b> {label}")
    addr = cam.get("소재지도로명주소", "").strip()
    if addr:
        lines.append(f"<b>주소:</b> {addr}")
    place = cam.get("설치장소", "").strip()
    if place:
        lines.append(f"<b>설치장소:</b> {place}")
    year = cam.get("설치연도", "").strip()
    if year:
        lines.append(f"<b>설치연도:</b> {year}")
    region = cam.get("시도명", "").strip()
    district = cam.get("시군구명", "").strip()
    if region:
        lines.append(f"<b>지역:</b> {region} {district}")
    return "<br>".join(lines)


def generate_map() -> None:
    cameras = load_cameras()

    m = folium.Map(location=[36.5, 127.5], zoom_start=7)

    data = []
    for cam in cameras:
        lat = float(cam["위도"])
        lon = float(cam["경도"])
        code = cam.get("단속구분", "").strip()
        color = ENFORCEMENT_COLORS.get(code, DEFAULT_COLOR)
        popup_html = build_popup(cam).replace("'", "\\'").replace("\n", "")
        data.append([lat, lon, color, popup_html])

    callback = """\
function (row) {
    var marker = L.circleMarker(new L.LatLng(row[0], row[1]), {
        radius: 5,
        color: row[2],
        fillColor: row[2],
        fillOpacity: 0.7,
        weight: 1
    });
    marker.bindPopup(row[3], {maxWidth: 300});
    return marker;
}"""

    FastMarkerCluster(data=data, callback=callback).add_to(m)

    m.save(str(OUTPUT_PATH))
    print(f"Map saved to {OUTPUT_PATH} ({len(cameras)} cameras)")


if __name__ == "__main__":
    generate_map()
```

**Step 2: Generate the map**

```bash
uv run python generate_korea_map.py
```

Expected: `Map saved to /Users/sardor/Projects/uzbspeedcameradb/korea.html (41900+ cameras)`

**Step 3: Verify the output file exists and has reasonable size**

```bash
ls -lh korea.html
```

Expected: File size roughly 15-30MB.

**Step 4: Open in browser to verify visually**

```bash
open korea.html
```

Verify: Map centered on South Korea, clustered markers visible, clicking a cluster zooms in, clicking a marker shows popup with Korean text.

**Step 5: Commit**

```bash
git add generate_korea_map.py korea.html
git commit -m "Add Korea speed camera interactive map (41K cameras)"
```

---

### Task 4: Visual verification and final polish

**Files:**
- Possibly modify: `generate_korea_map.py` (if issues found)

**Step 1: Verify in browser**

Open `korea.html` and check:
- [ ] Map loads and shows South Korea
- [ ] Markers cluster at zoom-out, expand on zoom-in
- [ ] Marker colors match enforcement types (red=speed, blue=signal, green=bus lane, orange=school zone)
- [ ] Clicking a marker shows popup with Korean address, speed limit, type
- [ ] No JavaScript errors in console

**Step 2: Verify existing Uzbekistan map still works**

```bash
open index.html
```

Ensure unchanged and functional.

**Step 3: Final commit if any polish was needed**

```bash
git add -A && git commit -m "Polish Korea map visualization"
```
