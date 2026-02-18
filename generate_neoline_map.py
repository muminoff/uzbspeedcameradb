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
