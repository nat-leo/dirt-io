'use client';

import api from '@/lib/api';
import { useRef, useCallback, useEffect, useState } from 'react';
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

function getViewportBounds(map: MapRef): Viewport {
  const bounds = map.getBounds();
  const north = bounds.getNorth();
  const south = bounds.getSouth();
  const east = bounds.getEast();
  const west = bounds.getWest();

  return {north, south, east, west};
}

function Map({
  getMap = api.getMap, // default to test square for stability; swap to api.getMap for live data
  initialViewState = {
    longitude: -100,
    latitude: 40,
    zoom: 3.5,
  },
}: MapProps) {
  const mapRef = useRef<MapRef | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [polygonData, setPolygonData] = useState<MapFeatureCollection | null>(null);

  const updatePolygonFromViewport = useCallback(async () => {
    const map = mapRef.current;
    if (!map) return;

    const { north, south, east, west } = getViewportBounds(map);

    console.log('Viewport corners:', {north, south, east, west});

    const geojson = await getMap(north, south, east, west);
    setPolygonData(geojson);
  }, [getMap]);

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
