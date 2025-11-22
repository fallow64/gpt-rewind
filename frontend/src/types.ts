export interface PostcardProps {
  contentHtml?: React.ReactNode;
  rotation: number;
  zIndex: number;
  offset: { x: number; y: number };
  width?: number;
  height?: number;
}

export interface PostcardStackItem {
  rotation: number;
  offset: { x: number; y: number };
}

// Configuration constants
export const POSTCARD_CONFIG = {
  width: 1280,
  height: 720,
  animationDuration: 600,
  backgroundCardColor: "#304158ff",
} as const;

// Default background card positions
export const DEFAULT_BACKGROUND_CARDS: PostcardStackItem[] = [
  { rotation: -5, offset: { x: 30, y: -10 } },
  { rotation: 4, offset: { x: -15, y: -25 } },
  { rotation: -6, offset: { x: 40, y: 10 } },
  { rotation: -2, offset: { x: 20, y: -20 } },
  { rotation: 5, offset: { x: -25, y: 30 } },
  { rotation: 6, offset: { x: -40, y: 15 } },
  { rotation: 3, offset: { x: -20, y: -30 } },
  { rotation: -5, offset: { x: 45, y: 20 } },
  { rotation: -3, offset: { x: 25, y: 30 } },
  { rotation: 5, offset: { x: -15, y: 35 } },
  { rotation: -4, offset: { x: 35, y: -25 } },
];
