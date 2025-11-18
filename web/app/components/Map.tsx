'use client';
import api from '@/lib/api';
import {useRef, useCallback, useState, useEffect} from 'react';
import maplibregl from 'maplibre-gl';
import {
  Map as DeckGLMap,
  NavigationControl,
  MapRef,
  ViewStateChangeEvent,
  Source,
  Layer,
} from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

function Map() {
  const mapRef = useRef<MapRef | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [polygonData, setPolygonData] = useState<any>(null); // simple state for demo

  const logBounds = useCallback(() => {
    const map = mapRef.current;
    if(!map) return;
    
    const bounds = map.getBounds();
    const nw = bounds.getNorthWest();
    const ne = bounds.getNorthEast();
    const se = bounds.getSouthEast();
    const sw = bounds.getSouthWest();

    console.log('Viewport corners:', {
      nw: [nw.lng, nw.lat],
      ne: [ne.lng, ne.lat],
      se: [se.lng, se.lat],
      sw: [sw.lng, sw.lat],
    });

  }, []);

  const refreshPolygon = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;
    const bounds = map.getBounds();
    const nw = bounds.getNorthWest();
    const ne = bounds.getNorthEast();
    const se = bounds.getSouthEast();
    const sw = bounds.getSouthWest();

    const coords = api.getMap(
      {lng: nw.lng, lat: nw.lat},
      {lng: ne.lng, lat: ne.lat},
      {lng: se.lng, lat: se.lat},
      {lng: sw.lng, lat: sw.lat},
    );

    // Wrap returned points into a simple polygon (closed ring)
    const ring = [...coords, coords[0]].map(({lng, lat}) => [lng, lat]);
    setPolygonData({
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: {type: 'Polygon', coordinates: [ring]},
          properties: {},
        },
      ],
    });
  }, []);

  const handleMove = useCallback((evt: ViewStateChangeEvent) => {
    if(debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      logBounds();
      refreshPolygon();
    }, 500);

  }, [logBounds, refreshPolygon]);

  const handleLoad = () => {
    refreshPolygon();
  };

  useEffect(() => {
    // initial fetch if map is already ready
    refreshPolygon();
  }, [refreshPolygon]);

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
        style={{width: '100%', height: '100%'}}
        mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json" // light style
        //mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json" // dark style
      >
        {polygonData ? (
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
        ) : null}
        <NavigationControl />
      </DeckGLMap>
    </div>
  );
}

export default Map;
