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

type GetMapFn = (nw: Coordinate, ne: Coordinate, se: Coordinate, sw: Coordinate) => Coordinate[];

interface MapProps {
  getMap?: GetMapFn;
  initialViewState?: { // Optional: let stories override initial view for testing
    longitude: number;
    latitude: number;
    zoom: number;
  };
}

type ViewportExtent = {
  nw: Coordinate;
  ne: Coordinate;
  se: Coordinate;
  sw: Coordinate;
};

function getViewportCorners(map: MapRef): Coordinate[] {
  const bounds = map.getBounds();
  const nw = bounds.getNorthWest();
  const ne = bounds.getNorthEast();
  const se = bounds.getSouthEast();
  const sw = bounds.getSouthWest();

  return [
    { lng: nw.lng, lat: nw.lat },
    { lng: ne.lng, lat: ne.lat },
    { lng: se.lng, lat: se.lat },
    { lng: sw.lng, lat: sw.lat },
  ];
}

function Map({
  getMap = api.getMap, // default to real API in the app
  initialViewState = {
    longitude: -100,
    latitude: 40,
    zoom: 3.5,
  },
}: MapProps) {
  const mapRef = useRef<MapRef | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [polygonData, setPolygonData] = useState<MapFeatureCollection | null>(null);

  const updatePolygonFromViewport = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;

    const [nw, ne, se, sw] = getViewportCorners(map);

    console.log('Viewport corners:', { nw, ne, se, sw });

    const coords = getMap(nw, ne, se, sw);

    const ring = [...coords, coords[0]].map(
      ({ lng, lat }: Coordinate) => [lng, lat] as [number, number],
    );

    const geojson: MapFeatureCollection = {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: {
            type: 'Polygon',
            coordinates: [ring],
          },
          properties: {},
        },
      ],
    };

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
export type { MapProps, GetMapFn, Coordinate, MapFeatureCollection, ViewportExtent };
