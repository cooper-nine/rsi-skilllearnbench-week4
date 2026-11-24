"""Recompute the distance to the selected plate edge from the benchmark inputs."""
from datetime import datetime, timezone
import json
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point


def main():
    root = Path("/root")
    events = json.loads((root / "earthquakes_2024.json").read_bytes())["features"]
    plates = gpd.read_file(root / "PB2002_plates.json")
    points = gpd.GeoDataFrame(
        {"feature": range(len(events))},
        geometry=[Point(event["geometry"]["coordinates"][:2]) for event in events],
        crs="EPSG:4326",
    )
    memberships = gpd.sjoin(points, plates[["Code", "geometry"]], predicate="within")
    counts = memberships["Code"].value_counts()
    plate = counts.idxmax()
    selected = max((events[index] for index in memberships.loc[memberships["Code"] == plate, "feature"]),
                   key=lambda event: event["properties"]["mag"])
    print(json.dumps({"node": "filter", "plate": plate, "earthquakes": int(counts[plate]),
                      "earthquake_id": selected["id"]}))

    lon, lat, *_ = selected["geometry"]["coordinates"]
    metric_crs = "EPSG:4087"
    point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(metric_crs).iloc[0]
    plate_edge = plates.loc[plates["Code"] == plate].to_crs(metric_crs).geometry.union_all().boundary
    boundaries = gpd.read_file(root / "PB2002_boundaries.json").to_crs(metric_crs)
    selected_edges = boundaries.loc[(boundaries["PlateA"] == plate) | (boundaries["PlateB"] == plate)]
    edge_km = point.distance(plate_edge) / 1000
    segment_km = selected_edges.distance(point).min() / 1000
    print(json.dumps({"node": "measure", "crs": metric_crs, "polygon_edge_km": edge_km,
                      "boundary_segments_km": segment_km}))

    properties = selected["properties"]
    answer = {
        "id": selected["id"],
        "place": properties["place"],
        "time": datetime.fromtimestamp(properties["time"] / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "magnitude": properties["mag"],
        "latitude": lat,
        "longitude": lon,
        "distance_km": round(edge_km, 2),
    }
    (root / "answer.json").write_text(json.dumps(answer, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
