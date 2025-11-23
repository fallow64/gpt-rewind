"use client";

import { createContext, ReactNode, useContext } from "react";
import { useSessionStorage } from "usehooks-ts";

interface ConversationContextType {
  conversationId: string | null;
  setConversationId: (id: string) => void;
}

const ConversationContext = createContext<ConversationContextType | undefined>(
  undefined
);

interface ConversationProviderProps {
  children: ReactNode;
}

export function ConversationProvider({ children }: ConversationProviderProps) {
  const [conversationId, setConversationId] = useSessionStorage<string | null>(
    "conversationId",
    null
  );

  return (
    <ConversationContext.Provider value={{ conversationId, setConversationId }}>
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversation() {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error(
      "useConversation must be used within a ConversationProvider"
    );
  }
  return context;
}
