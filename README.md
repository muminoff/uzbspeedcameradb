# Uzbekistan Speed Camera Database

A static dataset of speed and traffic enforcement cameras across Uzbekistan, available in both JSON and CSV formats. Sourced from OpenStreetMap.

## Stats

- **576 cameras** across the entire country
- 259 cameras with compass direction
- 88 cameras with name/road info

### By Camera Type

| Type | Count | Description |
|------|-------|-------------|
| `speed_camera` | 452 | Fixed speed enforcement cameras |
| `alpr` | 110 | Automatic License Plate Recognition |
| `traffic_camera` | 14 | General traffic enforcement cameras |

### By Region (approximate)

| Region | Cameras |
|--------|---------|
| Tashkent city | 148 |
| Karakalpakstan / Khorezm | 123 |
| Navoiy / Jizzax | 76 |
| Fergana Valley | 59 |
| Tashkent region | 51 |
| Samarkand | 24 |
| Bukhara | 13 |
| Kashkadarya / Surkhandarya | 7 |
| Other | 75 |

### By Speed Limit

| Speed Limit | Cameras |
|-------------|---------|
| 30 km/h | 2 |
| 50 km/h | 26 |
| 60 km/h | 194 |
| 70 km/h | 156 |
| 100 km/h | 42 |
| 110 km/h | 6 |
| Unknown | 147 |

## Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique camera identifier |
| `osm_node_id` | integer | OpenStreetMap node ID for traceability |
| `latitude` | float | Camera latitude coordinate |
| `longitude` | float | Camera longitude coordinate |
| `speed_limit` | integer | Speed limit in km/h (null if unknown) |
| `camera_type` | string | `speed_camera`, `alpr`, or `traffic_camera` |
| `compass_direction` | string | Direction camera faces (N, S, E, W, NE, NW, SE, SW) or null |
| `road_direction` | string | Road/location name from OSM or null |
| `source` | string | Data source ("openstreetmap") |

## Files

- `data/cameras.json` — Full dataset in JSON format
- `data/cameras.csv` — Full dataset in CSV format

## Data Source

Data extracted from [OpenStreetMap](https://www.openstreetmap.org/) using the Overpass API. Includes nodes tagged as `highway=speed_camera`, `man_made=surveillance` with `surveillance:zone=traffic`, and `enforcement=maxspeed` within Uzbekistan (ISO 3166-1: UZ).

Licensed under [ODbL](https://opendatacommons.org/licenses/odbl/).

## Usage

Use the JSON or CSV file directly in your application. No API or server required.

## Contributing

To add or update camera data, edit `data/cameras.json` and regenerate the CSV, or submit a pull request.
