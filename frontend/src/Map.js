'use client';

import DeckGL from '@deck.gl/react';
import {MapView} from '@deck.gl/core';
import {ScatterplotLayer} from '@deck.gl/layers';
import {useMemo} from 'react';

const INITIAL_VIEW_STATE = {
  longitude: -122.45,
  latitude: 37.8,
  zoom: 3,
  pitch: 0,
  bearing: 0,
};

const SAMPLE_DATA = [
  {name: 'San Francisco', population: '815k', position: [-122.45, 37.8]},
  {name: 'Los Angeles', population: '3.8M', position: [-118.2437, 34.0522]},
  {name: 'New York', population: '8.3M', position: [-74.006, 40.7128]},
  {name: 'Seattle', population: '750k', position: [-122.3321, 47.6062]},
];

export default function Map() {
  const layers = useMemo(
    () => [
      new ScatterplotLayer({
        id: 'cities',
        data: SAMPLE_DATA,
        pickable: true,
        getPosition: ({position}) => position,
        getFillColor: [89, 131, 252],
        getRadius: 90000,
        radiusUnits: 'meters',
      }),
    ],
    [],
  );

  return (
    <DeckGL
      initialViewState={INITIAL_VIEW_STATE}
      controller={{dragPan: true, scrollZoom: true}}
      views={new MapView({repeat: true})}
      layers={layers}
      style={{width: '100vw', height: '100vh', background: '#0f172a'}}
      getTooltip={({object}) =>
        object ? `${object.name} – Population: ${object.population}` : null
      }
    />
  );
}
