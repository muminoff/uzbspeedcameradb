# Korea Camera Direction Indicators — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add shaped markers (▲ upbound, ▼ downbound, ● both) to the Korea speed camera map to visualize camera lane direction, and include a `direction` field for HUD device consumption.

**Architecture:** Modify `generate_korea_map.py` to add direction constants, normalize the `도로노선방향` column, pass direction as `row[4]` in the FastMarkerCluster data array, and update the JS callback to render SVG triangles for up/down and circles for both. Regenerate `korea.html`.

**Tech Stack:** Python 3.14+, Folium FastMarkerCluster, Leaflet L.divIcon with inline SVG

---

### Task 1: Add direction constants and update data pipeline

**Files:**
- Modify: `generate_korea_map.py:10-30` (constants section)
- Modify: `generate_korea_map.py:50-71` (build_popup)
- Modify: `generate_korea_map.py:79-86` (data array construction)

**Step 1: Add direction constants after existing constants**

Add these after `DEFAULT_COLOR = "gray"` (line 24):

```python
DIRECTION_MAP = {"1": "up", "2": "down", "3": "both"}

DIRECTION_LABELS = {
    "1": "상행 (Upbound)",
    "2": "하행 (Downbound)",
    "3": "양방향 (Both)",
}
```

**Step 2: Add direction line to build_popup**

Insert before the `region` lines at the end of `build_popup()`:

```python
    direction_code = cam.get("도로노선방향", "").strip()
    direction_label = DIRECTION_LABELS.get(_normalize_code(direction_code), "")
    if direction_label:
        lines.append(f"<b>방향:</b> {direction_label}")
```

**Step 3: Add direction to data array**

Change the data array construction in `generate_map()` from:

```python
    data = []
    for cam in cameras:
        lat = cam["_lat"]
        lon = cam["_lon"]
        code = cam.get("단속구분", "").strip()
        color = ENFORCEMENT_COLORS.get(_normalize_code(code), DEFAULT_COLOR)
        popup_html = build_popup(cam)
        data.append([lat, lon, color, popup_html])
```

To:

```python
    data = []
    for cam in cameras:
        lat = cam["_lat"]
        lon = cam["_lon"]
        code = cam.get("단속구분", "").strip()
        color = ENFORCEMENT_COLORS.get(_normalize_code(code), DEFAULT_COLOR)
        popup_html = build_popup(cam)
        dir_code = cam.get("도로노선방향", "").strip()
        direction = DIRECTION_MAP.get(_normalize_code(dir_code), "both")
        data.append([lat, lon, color, popup_html, direction])
```

**Step 4: Verify script still runs (no callback change yet — row[4] is just ignored)**

```bash
uv run python generate_korea_map.py
```

Expected: `Map saved to ... (41904 cameras)` — no errors.

**Step 5: Commit**

```bash
git add generate_korea_map.py
git commit -m "Add direction data to Korea camera map pipeline"
```

---

### Task 2: Update JS callback to render shaped markers

**Files:**
- Modify: `generate_korea_map.py:88-99` (JS callback string)

**Step 1: Replace the callback string**

Change the `callback` variable from the current CircleMarker-only version to:

```python
    callback = """\
function (row) {
    var color = row[2];
    var dir = row[4];
    if (dir === 'both') {
        var marker = L.circleMarker(new L.LatLng(row[0], row[1]), {
            radius: 5,
            color: color,
            fillColor: color,
            fillOpacity: 0.7,
            weight: 1
        });
    } else {
        var rot = dir === 'down' ? ' style="transform:rotate(180deg)"' : '';
        var svg = '<div' + rot + '><svg width="14" height="14" viewBox="0 0 14 14">' +
            '<polygon points="7,1 13,13 1,13" fill="' + color + '" stroke="#333" stroke-width="1"/>' +
            '</svg></div>';
        var icon = L.divIcon({
            html: svg,
            className: '',
            iconSize: [14, 14],
            iconAnchor: [7, 7]
        });
        var marker = L.marker(new L.LatLng(row[0], row[1]), {icon: icon});
    }
    marker.bindPopup(row[3], {maxWidth: 300});
    return marker;
}"""
```

**Step 2: Regenerate the map**

```bash
uv run python generate_korea_map.py
```

Expected: `Map saved to ... (41904 cameras)` — no errors.

**Step 3: Verify file size is reasonable**

```bash
ls -lh korea.html
```

Expected: Similar size to before (~23MB), possibly slightly larger due to SVG markup in the data.

**Step 4: Commit**

```bash
git add generate_korea_map.py korea.html
git commit -m "Add directional shaped markers to Korea speed camera map"
```

---

### Task 3: Visual verification in browser

**Files:**
- None (verification only)

**Step 1: Open korea.html in browser**

Navigate to `korea.html` and zoom into an area with cameras.

**Step 2: Verify at street level**

Zoom to level 16+ and check:
- [ ] ▲ triangles visible for upbound cameras
- [ ] ▼ inverted triangles visible for downbound cameras
- [ ] ● circles visible for both-direction cameras
- [ ] Colors still match enforcement types (red, blue, green, orange, gray)
- [ ] Clicking any marker shows popup with direction line (방향: 상행/하행/양방향)
- [ ] No JavaScript console errors
- [ ] Clustering still works at zoom-out

**Step 3: Verify Uzbekistan map is untouched**

```bash
open index.html
```

Ensure unchanged and functional.

**Step 4: Push to remote**

```bash
git push origin main
```
