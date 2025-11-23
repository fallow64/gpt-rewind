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

export interface CompleteConversationHistory {}

// Configuration constants
export const POSTCARD_CONFIG = {
  width: 1024,
  height: 640,
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
] as const;

export const MONTH_NAMES = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
] as const;

export const HOURS = [
  "12am",
  "1am",
  "2am",
  "3am",
  "4am",
  "5am",
  "6am",
  "7am",
  "8am",
  "9am",
  "10am",
  "11am",
  "12pm",
  "1pm",
  "2pm",
  "3pm",
  "4pm",
  "5pm",
  "6pm",
  "7pm",
  "8pm",
  "9pm",
  "10pm",
  "11pm",
] as const;
