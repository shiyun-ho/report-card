'use client';

/**
 * React Query Provider for Report Card Assistant
 * 
 * Provides React Query functionality with proper configuration
 * for caching, background updates, and error handling.
 */

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Create a client with optimized settings for our use case
function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Stale time: how long data is considered fresh
        staleTime: 60 * 1000, // 1 minute default
        
        // Garbage collection time: how long unused data stays in cache
        gcTime: 5 * 60 * 1000, // 5 minutes default
        
        // Retry configuration
        retry: (failureCount, error) => {
          // Don't retry on authentication errors
          if (error instanceof Error && 
              (error.message.includes('Authentication required') || 
               error.message.includes('Permission denied'))) {
            return false;
          }
          
          // Retry up to 2 times for other errors
          return failureCount < 2;
        },
        
        // Exponential backoff for retries
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
        
        // Don't refetch on window focus by default (can be overridden per query)
        refetchOnWindowFocus: false,
        
        // Refetch on reconnect
        refetchOnReconnect: 'always',
      },
      mutations: {
        // Retry mutations once
        retry: 1,
        
        // Mutation retry delay
        retryDelay: 1000,
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined = undefined;

function getQueryClient() {
  if (typeof window === 'undefined') {
    // Server: always make a new query client
    return createQueryClient();
  } else {
    // Browser: make a new query client if we don't already have one
    if (!browserQueryClient) {
      browserQueryClient = createQueryClient();
    }
    return browserQueryClient;
  }
}

interface QueryProviderProps {
  children: React.ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  const queryClient = getQueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* Show React Query DevTools in development */}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools 
          initialIsOpen={false} 
          buttonPosition="bottom-left"
        />
      )}
    </QueryClientProvider>
  );
}

export default QueryProvider;