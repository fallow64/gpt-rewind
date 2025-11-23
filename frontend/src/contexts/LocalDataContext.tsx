"use client";

import { createContext, useContext, useState, ReactNode } from "react";
import { CompleteConversationHistory } from "@/src/types";

interface LocalDataContextType {
  localData: CompleteConversationHistory | null;
  setLocalData: (data: CompleteConversationHistory) => void;
  clearData: () => void;
}

const LocalDataContext = createContext<LocalDataContextType | undefined>(
  undefined
);

export function LocalDataProvider({ children }: { children: ReactNode }) {
  const [localData, setLocalData] =
    useState<CompleteConversationHistory | null>(null);

  const clearData = () => setLocalData(null);

  return (
    <LocalDataContext.Provider value={{ localData, setLocalData, clearData }}>
      {children}
    </LocalDataContext.Provider>
  );
}

export function useLocalData() {
  const context = useContext(LocalDataContext);
  if (context === undefined) {
    throw new Error("useData must be used within a DataProvider");
  }
  return context;
}
