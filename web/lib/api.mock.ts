// api.mock.ts
import type { ApiClient } from './api';
import type { FeatureCollection, Polygon } from 'geojson';

const square: FeatureCollection<Polygon> = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-108.16, 38.78],
            [-108.13, 38.78],
            [-108.13, 38.75],
            [-108.16, 38.75],
            [-108.16, 38.78],
          ],
        ],
      },
      properties: { id: 'mock-square' },
    },
  ],
};

export const mockApiClient: ApiClient = {
  get: async () => {
    throw new Error('mockApiClient.get not implemented');
  },
  post: async () => {
    throw new Error('mockApiClient.post not implemented');
  },
  put: async () => {
    throw new Error('mockApiClient.put not implemented');
  },
  patch: async () => {
    throw new Error('mockApiClient.patch not implemented');
  },
  delete: async () => {
    throw new Error('mockApiClient.delete not implemented');
  },
  async getMap(
    north: number,
    south: number,
    west: number,
    east: number,
  ) {
    console.log('[mockApiClient.getMap]', { north, south, west, east });
    return square;
  },
  getSquare(
    north: number,
    south: number,
    west: number,
    east: number,
  ) {
    console.log('[mockApiClient.getSquare]', { north, south, west, east });
    return square;
  },
};
