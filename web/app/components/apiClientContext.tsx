// lib/ApiClientContext.tsx
'use client';

import { createContext, useContext, useMemo } from 'react';
import type { ApiClient } from '@/lib/api';
import { mockApiClient } from '@/lib/api.mock';
import { realApiClient } from '@/lib/api';

const ApiClientContext = createContext<ApiClient | null>(null);

export function ApiClientProvider({
  client,
  children,
}: {
  client?: ApiClient;
  children: React.ReactNode;
}) {
  const defaultClient = useMemo(() => {
    if (client) return client;
    return process.env.NEXT_PUBLIC_API_MODE === 'mock'
      ? mockApiClient
      : realApiClient;
  }, [client]);

  return (
    <ApiClientContext.Provider value={defaultClient}>
      {children}
    </ApiClientContext.Provider>
  );
}

export function useApiClient(): ApiClient {
  const ctx = useContext(ApiClientContext);
  if (!ctx) {
    throw new Error('useApiClient must be used within <ApiClientProvider>');
  }
  return ctx;
}
