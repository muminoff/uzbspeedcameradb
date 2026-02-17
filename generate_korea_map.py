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

DIRECTION_MAP = {"1": "up", "2": "down", "3": "both"}

DIRECTION_LABELS = {
    "1": "상행 (Upbound)",
    "2": "하행 (Downbound)",
    "3": "양방향 (Both)",
}


def _normalize_code(raw: str) -> str:
    stripped = raw.lstrip("0")
    return stripped if stripped else raw


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
            row["_lat"] = lat
            row["_lon"] = lon
            cameras.append(row)
    return cameras


def build_popup(cam: dict) -> str:
    lines = []
    speed = cam.get("제한속도", "").strip()
    if speed and speed != "0":
        lines.append(f"<b>제한속도:</b> {speed} km/h")
    code = cam.get("단속구분", "").strip()
    label = ENFORCEMENT_LABELS.get(_normalize_code(code), code)
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
    direction_code = cam.get("도로노선방향", "").strip()
    direction_label = DIRECTION_LABELS.get(_normalize_code(direction_code), "")
    if direction_label:
        lines.append(f"<b>방향:</b> {direction_label}")
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
        lat = cam["_lat"]
        lon = cam["_lon"]
        code = cam.get("단속구분", "").strip()
        color = ENFORCEMENT_COLORS.get(_normalize_code(code), DEFAULT_COLOR)
        popup_html = build_popup(cam)
        dir_code = cam.get("도로노선방향", "").strip()
        direction = DIRECTION_MAP.get(_normalize_code(dir_code), "both")
        data.append([lat, lon, color, popup_html, direction])

    callback = """\
function (row) {
    var color = row[2];
    var dir = row[4];
    var marker;
    if (dir === 'both') {
        marker = L.circleMarker(new L.LatLng(row[0], row[1]), {
            radius: 5,
            color: color,
            fillColor: color,
            fillOpacity: 0.7,
            weight: 1
        });
    } else {
        var points = dir === 'down' ? '0,0 12,0 6,18' : '0,18 12,18 6,0';
        var anchor = dir === 'down' ? [6, 0] : [6, 18];
        var svg = '<svg width="12" height="18" viewBox="0 0 12 18">' +
            '<polygon points="' + points + '" fill="' + color + '" stroke="#333" stroke-width="1"/>' +
            '</svg>';
        var icon = L.divIcon({
            html: svg,
            className: '',
            iconSize: [12, 18],
            iconAnchor: anchor
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
