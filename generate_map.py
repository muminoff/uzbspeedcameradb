import json
from pathlib import Path

import folium
from folium.plugins import MarkerCluster

DATA_PATH = Path(__file__).parent / "data" / "cameras.json"
OUTPUT_PATH = Path(__file__).parent / "index.html"

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
