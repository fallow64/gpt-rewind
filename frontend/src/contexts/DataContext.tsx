"use client";

import { createContext, useContext, useState, ReactNode } from "react";

interface DataContextType {
  uploadedData: any | null;
  setUploadedData: (data: any) => void;
  clearData: () => void;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export function DataProvider({ children }: { children: ReactNode }) {
  const [uploadedData, setUploadedData] = useState<any | null>(null);

  const clearData = () => setUploadedData(null);

  return (
    <DataContext.Provider value={{ uploadedData, setUploadedData, clearData }}>
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error("useData must be used within a DataProvider");
  }
  return context;
}
