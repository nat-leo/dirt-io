// Map.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import Map, { GetMapFn, Coordinate } from './Map';

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
const basicMockGetMap: GetMapFn = (nw, ne, se, sw) => {
  return [nw, ne, se, sw];
};

/**
 * More detailed mock: approximate a “high LoD” wavy boundary using the corners.
 */
const detailedMockGetMap: GetMapFn = (nw, ne, se, sw) => {
  const midTop: Coordinate = { lng: (nw.lng + ne.lng) / 2, lat: nw.lat + 0.2 };
  const midRight: Coordinate = { lng: ne.lng + 0.2, lat: (ne.lat + se.lat) / 2 };
  const midBottom: Coordinate = { lng: (sw.lng + se.lng) / 2, lat: se.lat - 0.2 };
  const midLeft: Coordinate = { lng: nw.lng - 0.2, lat: (nw.lat + sw.lat) / 2 };

  return [nw, midTop, ne, midRight, se, midBottom, sw, midLeft];
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
  return [];
};

export const NoData: Story = {
  args: {
    getMap: emptyMockGetMap,
  },
};