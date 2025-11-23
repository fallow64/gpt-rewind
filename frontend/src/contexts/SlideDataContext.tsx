"use client";

import {
  createContext,
  ReactNode,
  useContext,
  useState,
  useEffect,
  useRef,
} from "react";
import { useConversation } from "./ConversationContext";

interface SlideDataContextType {
  data: any;
  error: Error | null;
  refetch: () => void;
  audioUrl: string | null;
}

const SlideDataContext = createContext<SlideDataContextType | undefined>(
  undefined
);

interface SlideDataProviderProps {
  slide: number;
  children: ReactNode;
  isActive?: boolean;
  isAudioEnabled?: boolean;
}

// Create a cache for data to avoid refetching
const dataCache = new Map<string, any>();
const pendingPromises = new Map<string, Promise<any>>();

// Global audio instance tracker - only one audio should play at a time
let currentAudioInstance: HTMLAudioElement | null = null;

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

export function SlideDataProvider({
  slide,
  children,
  isActive = false,
  isAudioEnabled = true,
}: SlideDataProviderProps) {
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
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Build audio URL
  const audioUrl = `http://localhost:8000/data/${conversationId}/sounds/${slide}`;

  // Play/pause audio based on isActive state and audio enabled setting
  useEffect(() => {
    if (!audioRef.current) {
      const audio = new Audio(audioUrl);
      audio.loop = false;
      audio.volume = 0.3; // Set to 30% volume
      audioRef.current = audio;
    }

    if (isActive && isAudioEnabled) {
      // Stop any currently playing audio before starting new one
      if (currentAudioInstance && currentAudioInstance !== audioRef.current) {
        currentAudioInstance.pause();
        currentAudioInstance.currentTime = 0;
      }

      // Set this as the current playing audio
      currentAudioInstance = audioRef.current;

      // Start playing when active
      audioRef.current.play().catch((err) => {
        console.warn("Audio autoplay failed:", err);
      });
    } else {
      // Pause when not active or audio is disabled
      audioRef.current.pause();

      // Clear global reference if this was the current playing audio
      if (currentAudioInstance === audioRef.current) {
        currentAudioInstance = null;
      }
    }

    // Cleanup: stop audio when slide unmounts
    return () => {
      if (audioRef.current && !isActive) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
    };
  }, [audioUrl, isActive, isAudioEnabled]);

  const refetch = () => {
    dataCache.delete(cacheKey);
    pendingPromises.delete(cacheKey);
    window.location.reload(); // Simple refetch - triggers re-render
  };

  return (
    <SlideDataContext.Provider value={{ data, error, refetch, audioUrl }}>
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
