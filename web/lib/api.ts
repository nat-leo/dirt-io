import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
import type { FeatureCollection, Polygon } from 'geojson';

const BASE_URL =
  process.env.FASTAPI_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || '';

if (!BASE_URL) {
  // eslint-disable-next-line no-console
  console.warn(
    'BASE_URL/NEXT_PUBLIC_API_BASE_URL is not set; API client will use relative URLs.',
  );
}

function createApiClient(baseUrl?: string) {
  const axiosClient = axios.create({
    baseURL: baseUrl || undefined,
    timeout: 15_000,
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: false,
  });

  axiosClient.interceptors.request.use((config) => {
    return config;
  });

  axiosClient.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error) => Promise.reject(error),
  );

  return {

    get: <T = unknown>(url: string, config?: AxiosRequestConfig) =>
      axiosClient.get<T>(url, config).then((res) => res.data),

    post: <T = unknown>(
      url: string,
      data?: unknown,
      config?: AxiosRequestConfig,
    ) => axiosClient.post<T>(url, data, config).then((res) => res.data),

    put: <T = unknown>(
      url: string,
      data?: unknown,
      config?: AxiosRequestConfig,
    ) => axiosClient.put<T>(url, data, config).then((res) => res.data),

    patch: <T = unknown>(
      url: string,
      data?: unknown,
      config?: AxiosRequestConfig,
    ) => axiosClient.patch<T>(url, data, config).then((res) => res.data),

    delete: <T = unknown>(url: string, config?: AxiosRequestConfig) =>
      axiosClient.delete<T>(url, config).then((res) => res.data),

    async getMap(north: number, south: number, west: number, east: number): Promise<FeatureCollection<Polygon>> {
      const bbox = `${west},${south},${east},${north}`;
      const featureCollection = await axiosClient.get<FeatureCollection<Polygon>>(
        '/map',
        { params: { BBOX: bbox } },
      );
      
      return featureCollection.data;
    },

    getSquare(
      north: number,
      south: number,
      west: number,
      east: number,
    ): FeatureCollection<Polygon> {
      const coords: [number, number][] = [
        [west, north],
        [east, north],
        [east, south],
        [west, south],
        [west, north],
      ];

      return {
        type: 'FeatureCollection',
        features: [
          {
            type: 'Feature',
            geometry: {
              type: 'Polygon',
              coordinates: [coords],
            },
            properties: {},
          },
        ],
      };
    },

  };
}

export const realApiClient = createApiClient(BASE_URL || undefined);

export type ApiClient = ReturnType<typeof createApiClient>;

export { createApiClient };
