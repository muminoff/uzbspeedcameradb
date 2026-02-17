# Korea Camera Direction Indicators — Design

**Date:** 2026-02-18
**Status:** Approved

## Goal

Visualize camera lane direction (upbound/downbound/both) on the Korea speed camera map using shaped markers, and add a clean `direction` field for HUD device consumption.

## Direction Data

The `도로노선방향` column encodes which lane(s) the camera monitors:

| Raw code | Normalized | Direction | Korean label | Map symbol |
|----------|-----------|-----------|-------------|------------|
| `1`, `01` | `1` | `"up"` | 상행 (Upbound) | ▲ triangle |
| `2`, `02` | `2` | `"down"` | 하행 (Downbound) | ▼ triangle (rotated) |
| `3`, `03` | `3` | `"both"` | 양방향 (Both) | ● circle |

## Visual Encoding

**Two independent visual channels:**
- **Color** = enforcement type (unchanged): red (speed), blue (signal), green (bus lane), orange (school zone), gray (other)
- **Shape** = direction (new): ▲ upbound, ▼ downbound, ● both

### Marker implementation

- **Up/Down:** `L.marker` with `L.divIcon` containing a 14x14px inline SVG triangle. Downbound is rotated 180°.
- **Both:** `L.circleMarker` (existing, unchanged).

SVG triangle template:
```html
<svg width="14" height="14" viewBox="0 0 14 14">
  <polygon points="7,1 13,13 1,13" fill="{color}" stroke="#333" stroke-width="1"/>
</svg>
```

For downbound, wrap in `<div style="transform:rotate(180deg)">`.

### Popup

Add direction line to popup:
```
방향: 상행 (Upbound)
```

## Data Array

The FastMarkerCluster data array becomes:
```
[lat, lon, color, popup_html, direction]
```

Where `direction` is `"up"`, `"down"`, or `"both"`.

## Files Changed

- **Modify:** `generate_korea_map.py` — add direction constants, update data array, update JS callback
- **Regenerate:** `korea.html`

## HUD Compatibility

The `direction` field (`"up"` / `"down"` / `"both"`) is a clean, language-agnostic value that a HUD device can consume directly from the data array or from a future JSON export.
