"use client";

import { createContext, useContext, useState, ReactNode } from "react";
import { useConversation } from "./ConversationContext";

interface SlideDataContextType {
  data: any;
  error: Error | null;
  refetch: () => void;
}

const SlideDataContext = createContext<SlideDataContextType | undefined>(
  undefined
);

interface SlideDataProviderProps {
  slide: number;
  children: ReactNode;
}

// Create a cache for data to avoid refetching
const dataCache = new Map<string, any>();
const pendingPromises = new Map<string, Promise<any>>();

async function fetchSlideData(
  conversationId: string,
  slide: number
): Promise<any> {
  const cacheKey = `${conversationId}-${slide}`;

  if (dataCache.has(cacheKey)) {
    return dataCache.get(cacheKey);
  }

  if (pendingPromises.has(cacheKey)) {
    return pendingPromises.get(cacheKey);
  }

  const promise = fetch(
    `http://localhost:8000/data/${conversationId}/insights/${slide}`
  )
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(
          `Failed to fetch slide data: ${response.statusText}. Index: ${slide}`
        );
      }
      const json = await response.json();
      const data = json.data;
      dataCache.set(cacheKey, data);
      pendingPromises.delete(cacheKey);
      return data;
    })
    .catch((err) => {
      pendingPromises.delete(cacheKey);
      throw err;
    });

  pendingPromises.set(cacheKey, promise);
  return promise;
}

export function SlideDataProvider({ slide, children }: SlideDataProviderProps) {
  const { conversationId } = useConversation();

  if (!conversationId) {
    throw new Error(
      "No conversation ID found in context. Have you uploaded data?"
    );
  }

  const cacheKey = `${conversationId}-${slide}`;

  // Check if data is already cached
  if (!dataCache.has(cacheKey)) {
    // If there's a pending promise, throw it for Suspense
    if (pendingPromises.has(cacheKey)) {
      throw pendingPromises.get(cacheKey);
    }

    // Start fetching and throw the promise
    const promise = fetchSlideData(conversationId, slide);
    throw promise;
  }

  // Data is available from cache
  const data = dataCache.get(cacheKey);
  const [error, setError] = useState<Error | null>(null);

  const refetch = () => {
    dataCache.delete(cacheKey);
    pendingPromises.delete(cacheKey);
    window.location.reload(); // Simple refetch - triggers re-render
  };

  return (
    <SlideDataContext.Provider value={{ data, error, refetch }}>
      {children}
    </SlideDataContext.Provider>
  );
}

export function useSlide() {
  const context = useContext(SlideDataContext);
  if (context === undefined) {
    throw new Error("useSlide must be used within a SlideDataProvider");
  }
  return context;
}
