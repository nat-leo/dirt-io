import React, { useState, useCallback, useEffect } from "react";
import { Polygon } from "@react-google-maps/api";

// Convert WKT POLYGON string to Google Maps LatLngLiteral array
function parseWktPolygon(wkt) {
  return wkt
    .replace("POLYGON ((", "")
    .replace("))", "")
    .trim()
    .split(",")
    .map((pair) => {
      const [lng, lat] = pair.trim().split(/\s+/).map(Number);
      return { lat, lng };
    });
}

export default function PolygonLayer({ map, onClick }) {
  const [locations, setLocations] = useState([]);

  const handleMapClick = useCallback(
    async (e) => {
      const lat = e.latLng.lat();
      const lng = e.latLng.lng();

      try {
        const res = await fetch(`http://localhost:8000/soil?lon=${lng}&lat=${lat}`);
        if (!res.ok) throw new Error(`API error ${res.status}`);
        const json = await res.json();

        if (json.data && json.data.length > 0) {
          // Use the first polygon from the API response
          const wkt = json.data[0][2];
          const path = parseWktPolygon(wkt);

          // Store as a single location object with path
          setLocations([{ lat, lng, path }]);

          if (onClick) onClick({ lat, lng });
        }
      } catch (err) {
        console.error("Error fetching polygon:", err);
        // fallback: just store clicked point
        setLocations([{ lat, lng }]);
        if (onClick) onClick({ lat, lng });
      }
    },
    [onClick]
  );

  useEffect(() => {
    if (!map) return;
    const listener = map.addListener("click", handleMapClick);
    return () => listener.remove();
  }, [map, handleMapClick]);

  return (
    <>
      {locations.map((loc, i) => (
        <Polygon
          key={i}
          paths={loc.path || [
            // fallback square if no API path yet
            { lat: loc.lat + 0.0015, lng: loc.lng },
            { lat: loc.lat, lng: loc.lng + 0.0015 },
            { lat: loc.lat - 0.0015, lng: loc.lng },
            { lat: loc.lat, lng: loc.lng - 0.0015 },
          ]}
          options={{
            fillColor: "#FF0000",
            fillOpacity: 0.5,
            strokeColor: "#FF0000",
            strokeOpacity: 1,
            strokeWeight: 2,
          }}
        />
      ))}
    </>
  );
}
