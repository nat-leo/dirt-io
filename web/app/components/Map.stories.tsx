// Map.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import Map, { GetMapFn, Coordinate, MapFeatureCollection } from './Map';

const meta: Meta<typeof Map> = {
  title: 'Maps/Map',
  component: Map,
  parameters: {
    layout: 'fullscreen',
  },
};
export default meta;

type Story = StoryObj<typeof Map>;

/**
 * Simple mock: just returns the four corners as a polygon ring.
 * In reality you can return any shape you want.
 */
const basicMockGetMap: GetMapFn = (north, south, west, east) => {
  const coords: [number, number][] = [
    [west, north],
    [east, north],
    [east, south],
    [west, south],
    [west, north],
  ];
  const collection: MapFeatureCollection = {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        geometry: { type: 'Polygon', coordinates: [coords] },
        properties: {},
      },
    ],
  };
  return collection;
};

/**
 * More detailed mock: approximate a “high LoD” wavy boundary using the corners.
 */
const detailedMockGetMap: GetMapFn = (north, south, west, east) => {
  const midTop: Coordinate = { lng: (west + east) / 2, lat: north + 0.2 };
  const midRight: Coordinate = { lng: east + 0.2, lat: (north + south) / 2 };
  const midBottom: Coordinate = { lng: (west + east) / 2, lat: south - 0.2 };
  const midLeft: Coordinate = { lng: west - 0.2, lat: (north + south) / 2 };

  const coords: [number, number][] = [
    [west, north],
    [midTop.lng, midTop.lat],
    [east, north],
    [midRight.lng, midRight.lat],
    [east, south],
    [midBottom.lng, midBottom.lat],
    [west, south],
    [midLeft.lng, midLeft.lat],
    [west, north],
  ];

  return {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        geometry: { type: 'Polygon', coordinates: [coords] },
        properties: {},
      },
    ],
  };
};

export const BasicMock: Story = {
  args: {
    getMap: basicMockGetMap,
    initialViewState: {
      longitude: -100,
      latitude: 40,
      zoom: 3.5,
    },
  },
};

export const DetailedMock: Story = {
  args: {
    getMap: detailedMockGetMap,
    initialViewState: {
      longitude: -122.4,
      latitude: 37.8,
      zoom: 9,
    },
  },
};

const emptyMockGetMap: GetMapFn = () => {
  return { type: 'FeatureCollection', features: [] };
};

export const NoData: Story = {
  args: {
    getMap: emptyMockGetMap,
  },
};
