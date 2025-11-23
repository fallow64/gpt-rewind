"use client";

import { createContext, useContext, useState, ReactNode, use } from "react";
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

// Create a cache for promises to enable Suspense
const promiseCache = new Map<string, Promise<any>>();

function fetchSlideData(conversationId: string, slide: number): Promise<any> {
  const cacheKey = `${conversationId}-${slide}`;

  if (promiseCache.has(cacheKey)) {
    return promiseCache.get(cacheKey)!;
  }

  const promise = fetch(
    `http://localhost:8000/data/${conversationId}/insights/${slide}`
  ).then(async (response) => {
    if (!response.ok) {
      throw new Error(
        `Failed to fetch slide data: ${response.statusText}. Index: ${slide}`
      );
    }
    const json = await response.json();
    return json.data;
  });

  promiseCache.set(cacheKey, promise);
  return promise;
}

export function SlideDataProvider({ slide, children }: SlideDataProviderProps) {
  const { conversationId } = useConversation();

  const [dataPromise] = useState(() => fetchSlideData(conversationId!, slide));
  const [error, setError] = useState<Error | null>(null);

  // Use React's use() hook to unwrap the promise - this integrates with Suspense
  let data;
  try {
    data = use(dataPromise);
  } catch (err) {
    if (err instanceof Promise) {
      // Still loading, Suspense will catch this
      throw err;
    }
    // Actual error
    setError(err instanceof Error ? err : new Error("Unknown error occurred"));
    throw err;
  }

  const refetch = () => {
    const cacheKey = `${conversationId}-${slide}`;
    promiseCache.delete(cacheKey);
    window.location.reload(); // Simple refetch for now
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
