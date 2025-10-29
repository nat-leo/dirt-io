import React, { useState, useCallback, useEffect } from "react";
import { Polygon } from "@react-google-maps/api";

/**
 * PolygonLayer renders polygons on a Google Map for each click.
 *
 * @param {google.maps.Map} map - The Google Maps instance
 * @param {(location: {lat: number, lng: number}) => void} onClick
 *   Optional callback triggered after a polygon is added
 */
export default function PolygonLayer({ map, onClick }) {
  const [locations, setLocations] = useState([]);

  /**
   * Creates a polygon path around a center point.
   *
   * @param {number} lat - Latitude of the center
   * @param {number} lng - Longitude of the center
   * @returns {google.maps.LatLngLiteral[]} Array of coordinates forming a polygon
   */
  const createPolygonPath = (lat, lng) => {
    const size = 0.0015;
    return [
      { lat: lat + size, lng: lng },
      { lat: lat, lng: lng + size },
      { lat: lat - size, lng: lng },
      { lat: lat, lng: lng - size },
    ];
  };

  const handleMapClick = useCallback(
    async (e) => {
      const newLocation = { lat: e.latLng.lat(), lng: e.latLng.lng() };

      // Future: replace with API call to determine polygon properties
      // const polygonData = await fetchPolygonFromAPI(newLocation);

      setLocations((prev) => [newLocation]); // setLocations((prev) => [...prev, newLocation]);
      if (onClick) onClick(newLocation);
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
          paths={createPolygonPath(loc.lat, loc.lng)}
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
