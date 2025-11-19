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

function parseWfsXmlToFeatureCollection(xml: string): FeatureCollection<Polygon> {
  const coordRegex = /<gml:coordinates[^>]*>([^<]+)<\/gml:coordinates>/gi;
  let match;
  const features = [];

  while ((match = coordRegex.exec(xml)) !== null) {
    const raw = match[1].trim();
    const points = raw
      .split(/\s+/)
      .map((pair) => pair.split(/[, ]+/).map(parseFloat))
      .filter((nums) => nums.length === 2 && nums.every((n) => !Number.isNaN(n)))
      .map(([lat, lng]) => [lng, lat] as [number, number]); // swap to [lng, lat]

    if (points.length < 3) continue;

    const closed =
      points.length > 0 &&
      (points[0][0] !== points[points.length - 1][0] ||
        points[0][1] !== points[points.length - 1][1])
        ? [...points, points[0]]
        : points;

    features.push({
      type: 'Feature' as const,
      geometry: {
        type: 'Polygon' as const,
        coordinates: [closed],
      },
      properties: {},
    });
  }

  return {
    type: 'FeatureCollection',
    features,
  };
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
    async getMap(
      north: number,
      south: number,
      west: number,
      east: number,
    ): Promise<FeatureCollection<Polygon>> {
      const clampDecimals = (n: number) => Number(n.toFixed(12));
      const minX = Math.min(west, east);
      const maxX = Math.max(west, east);
      const minY = Math.min(south, north);
      const maxY = Math.max(south, north);
      const nWest = clampDecimals(minX);
      const nEast = clampDecimals(maxX);
      const nSouth = clampDecimals(minY);
      const nNorth = clampDecimals(maxY);

      const url =
        'https://sdmdataaccess.sc.egov.usda.gov/Spatial/SDMWM.wfs' +
        '?SERVICE=wfs' +
        '&VERSION=1.1.0' +
        '&REQUEST=GetFeature' +
        '&TYPENAME=surveyareapoly' +
        '&SRSNAME=EPSG:4326' +
        `&BBOX=${nWest},${nSouth},${nEast},${nNorth}`;

      const { data: text = '' } = await axiosClient.get<string>(url, {
        responseType: 'text' as const,
      });
      // eslint-disable-next-line no-console
      console.log('[api.getMap] url:', url, 'responseLength:', text.length);
      const featureCollection = parseWfsXmlToFeatureCollection(text);
      // eslint-disable-next-line no-console
      console.log(
        '[api.getMap] parsed polygons:',
        featureCollection.features.length,
        'points:',
        featureCollection.features[0]?.geometry.coordinates[0]?.length ?? 0,
      );
      return featureCollection;
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
