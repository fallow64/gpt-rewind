"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  use,
} from "react";

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
const promiseCache = new Map<number, Promise<any>>();

function fetchSlideData(slide: number): Promise<any> {
  if (promiseCache.has(slide)) {
    return promiseCache.get(slide)!;
  }

  const promise = fetch(`/api/slide-data?pageIndex=${slide}`).then(
    async (response) => {
      if (!response.ok) {
        throw new Error(
          `Failed to fetch slide data: ${response.statusText}. Index: ${slide}`
        );
      }
      return response.json();
    }
  );

  promiseCache.set(slide, promise);
  return promise;
}

export function SlideDataProvider({ slide, children }: SlideDataProviderProps) {
  const [dataPromise] = useState(() => fetchSlideData(slide));
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
    promiseCache.delete(slide);
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
