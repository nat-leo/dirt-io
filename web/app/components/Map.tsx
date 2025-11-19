'use client';

import { useRef, useCallback, useEffect, useState } from 'react';
import { useApiClient } from './apiClientContext';
import maplibregl from 'maplibre-gl';
import {
  Map as DeckGLMap,
  NavigationControl,
  MapRef,
  ViewStateChangeEvent,
  Source,
  Layer,
} from 'react-map-gl/maplibre';
import type { FeatureCollection, Polygon } from 'geojson';
import 'maplibre-gl/dist/maplibre-gl.css';

type Coordinate = { lng: number; lat: number };
type MapFeatureCollection = FeatureCollection<Polygon>;

type GetMapFn =
  | ((north: number, south: number, west: number, east: number) => MapFeatureCollection)
  | ((north: number, south: number, west: number, east: number) => Promise<MapFeatureCollection>);

interface MapProps {
  getMap?: GetMapFn;
  initialViewState?: { // Optional: let stories override initial view for testing
    longitude: number;
    latitude: number;
    zoom: number;
  };
}

type Viewport = {
    north: number,
    south: number,
    west: number,
    east: number,
};

const METERS_PER_DEG = 111_300; // approximate
const TARGET_AREA_M2 = 10_000_000_000; // 10,000 km^2

function getViewportBounds(map: MapRef): Viewport {
  const bounds = map.getBounds();
  const north = bounds.getNorth();
  const south = bounds.getSouth();
  const east = bounds.getEast();
  const west = bounds.getWest();

  return {north, south, east, west};
}

function Map({
  getMap, // optional override for stories/tests; defaults to injected client
  initialViewState = {
    longitude: -100,
    latitude: 40,
    zoom: 3.5,
  },
}: MapProps) {
  const mapRef = useRef<MapRef | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [polygonData, setPolygonData] = useState<MapFeatureCollection | null>(null);
  const api = useApiClient();

  const updatePolygonFromViewport = useCallback(async () => {
    const map = mapRef.current;
    if (!map) return;

    const { north, south, east, west } = getViewportBounds(map);

    // shrink BBOX to half the viewport size (center preserved)
    const centerLat = (north + south) / 2;
    const centerLng = (east + west) / 2;
    const latSpan = (north - south) / 2; // half height
    const lngSpan = (east - west) / 2; // half width
    const halfNorth = centerLat + latSpan / 2;
    const halfSouth = centerLat - latSpan / 2;
    const halfEast = centerLng + lngSpan / 2;
    const halfWest = centerLng - lngSpan / 2;

    // Calculate current box area (rough meters)
    const widthDeg = halfEast - halfWest;
    const heightDeg = halfNorth - halfSouth;
    const cosLat = Math.cos((centerLat * Math.PI) / 180);
    const currentAreaM2 = Math.abs(widthDeg * heightDeg * METERS_PER_DEG * METERS_PER_DEG * cosLat);

    let bbox = { north: halfNorth, south: halfSouth, east: halfEast, west: halfWest };

    // If the half-viewport box exceeds the target area, shrink to an exact target-area square centered on the viewport.
    if (currentAreaM2 > TARGET_AREA_M2) {
      const safeCos = Math.max(Math.abs(cosLat), 0.01); // avoid division by tiny cos near poles
      const sideDeg = Math.sqrt(TARGET_AREA_M2 / (METERS_PER_DEG * METERS_PER_DEG * safeCos));
      const halfSide = sideDeg / 2;
      bbox = {
        north: centerLat + halfSide,
        south: centerLat - halfSide,
        east: centerLng + halfSide,
        west: centerLng - halfSide,
      };
    }

    console.log('Viewport corners:', {north, south, east, west});

    const fetchMap = getMap ?? api.getMap;
    const geojson = await fetchMap(bbox.north, bbox.south, bbox.west, bbox.east);
    setPolygonData(geojson);
  }, [getMap, api]);

  const handleMove = useCallback(
    (_evt: ViewStateChangeEvent) => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }

      debounceRef.current = setTimeout(() => {
        updatePolygonFromViewport();
      }, 500);
    },
    [updatePolygonFromViewport],
  );

  const handleLoad = useCallback(() => {
    updatePolygonFromViewport();
  }, [updatePolygonFromViewport]);

  useEffect(() => {
    updatePolygonFromViewport();
  }, [updatePolygonFromViewport]);

  // Expose map and current polygon to window for e2e test hooks only.
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).__MAP__ = mapRef.current;
      (window as any).__POLYGON__ = polygonData;
    }
  }, [polygonData]);

  return (
    <div className="w-full h-[70vh] min-h-[360px]">
      <DeckGLMap
        ref={mapRef}
        onLoad={handleLoad}
        onMove={handleMove}
        mapLib={maplibregl}
        initialViewState={initialViewState}
        style={{ width: '100%', height: '100%' }}
        mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
      >
        {polygonData && (
          <Source id="random-polygon" type="geojson" data={polygonData}>
            <Layer
              id="random-polygon-fill"
              type="fill"
              paint={{
                'fill-color': '#4F46E5',
                'fill-opacity': 0.25,
                'fill-outline-color': '#312e81',
              }}
            />
            <Layer
              id="random-polygon-outline"
              type="line"
              paint={{
                'line-color': '#312e81',
                'line-width': 2,
              }}
            />
          </Source>
        )}

        <NavigationControl />
      </DeckGLMap>
    </div>
  );
}

export default Map;
export type { MapProps, GetMapFn, Coordinate, MapFeatureCollection, Viewport };
