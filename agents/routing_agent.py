from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Dict, List, Tuple

import pandas as pd


LOCATION_ALIASES: Dict[str, Tuple[float, float]] = {
    # Sehore district
    "sehore": (23.2033, 77.0850),
    "ashta": (23.0179, 76.7206),
    "nasrullaganj": (22.6927, 76.7157),
    "ichhawar": (23.0167, 76.8803),
    "rehti": (22.9250, 77.3167),
    "budhni": (22.9873, 77.6099),
    "shyampur": (23.2700, 77.2200),
    # Bhopal district
    "bhopal": (23.2599, 77.4126),
    "mandideep": (23.0767, 77.5500),
    # Vidisha district
    "vidisha": (23.5251, 77.8061),
    "basoda": (23.8533, 77.9367),
    "sironj": (24.1033, 77.6917),
    "lateri": (23.8367, 78.3667),
    "gyaraspur": (23.7867, 78.0233),
    "kurwai": (24.0833, 78.0500),
    # Raisen district
    "raisen": (23.3303, 77.7820),
    "sanchi": (23.4865, 77.7378),
    "obaidullaganj": (23.1167, 77.6000),
    "goharganj": (23.1523, 77.7030),
    "begumganj": (23.5983, 77.9667),
    "silwani": (23.5500, 78.1300),
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * radius * asin(sqrt(a))


@dataclass
class RoutingAgent:
    facility_csv_path: str

    def __post_init__(self) -> None:
        self.df = pd.read_csv(self.facility_csv_path)

    def find_nearest(self, location: str, top_k: int = 3) -> Dict[str, object]:
        query = location.strip().lower()
        if query not in LOCATION_ALIASES:
            for alias in LOCATION_ALIASES:
                if alias in query or query in alias:
                    query = alias
                    break
            else:
                query = "sehore"
        lat, lon = LOCATION_ALIASES[query]
        scored: List[Dict[str, object]] = []
        for row in self.df.to_dict(orient="records"):
            distance = haversine_km(lat, lon, row["lat"], row["lon"])
            scored.append({**row, "distance_km": round(distance, 2)})

        nearest = sorted(scored, key=lambda item: item["distance_km"])[:top_k]
        return {
            "query_location": location,
            "resolved_location": query,
            "facilities": nearest,
        }
