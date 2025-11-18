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

type LngLat = { lng: number; lat: number };
type PolygonFC = FeatureCollection<Polygon>;

function getViewportCorners(map: MapRef): LngLat[] {
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

function Map() {
  const mapRef = useRef<MapRef | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [polygonData, setPolygonData] = useState<PolygonFC | null>(null);

  const updatePolygonFromViewport = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;

    const corners = getViewportCorners(map);

    // Logging stays in one place
    console.log('Viewport corners:', corners);

    // Assuming api.getMap accepts four corners as in your original code
    const coords = api.getMap(corners[0], corners[1], corners[2], corners[3]);

    // Wrap returned points into a simple closed polygon ring
    const ring = [...coords, coords[0]].map(({ lng, lat }: LngLat) => [lng, lat] as [number, number]);

    const geojson: PolygonFC = {
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
  }, []);

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

  // Optional: if you want an initial fetch in case onLoad doesn’t fire
  useEffect(() => {
    updatePolygonFromViewport();
  }, [updatePolygonFromViewport]);

  return (
    <div className="w-full h-[70vh] min-h-[360px]">
      <DeckGLMap
        ref={mapRef}
        onLoad={handleLoad}
        onMove={handleMove}
        mapLib={maplibregl}
        initialViewState={{
          longitude: -100,
          latitude: 40,
          zoom: 3.5,
        }}
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
