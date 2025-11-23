# Using Uploaded Data in GPT Rewind

## Overview

The application now stores the uploaded JSON data in a React Context that is available throughout the application during the user's session.

## Architecture

### DataContext (`src/contexts/DataContext.tsx`)

The `DataContext` provides:

- `uploadedData`: The parsed JSON data from the uploaded file
- `setUploadedData(data)`: Function to store the data
- `clearData()`: Function to clear the stored data

### Usage in Components

Import and use the `useData` hook in any component:

```tsx
import { useData } from "@/src/contexts/DataContext";

function MyComponent() {
  const { uploadedData } = useData();

  // Use the data
  if (uploadedData) {
    console.log("User uploaded data:", uploadedData);
    // Process and display the data
  }

  return (
    // Your JSX
  );
}
```

## How It Works

1. **Upload Flow** (`src/app/page.tsx`):

   - User uploads a JSON file
   - File is parsed and validated
   - Data is stored in DataContext via `setUploadedData(jsonData)`
   - Data is sent to API endpoint for server-side processing
   - User is redirected to insights page

2. **Insights Page** (`src/app/insights/page.tsx`):

   - Accesses uploaded data via `useData()` hook
   - Data is available to all slide components
   - Logs data availability for debugging

3. **Slide Components** (e.g., `TopTopicsThisYearSlide.tsx`):
   - Import and use the `useData` hook
   - Access `uploadedData` to display user-specific insights
   - Fallback to sample data if no upload exists

## Example: Processing Uploaded Data

```tsx
import { useData } from "@/src/contexts/DataContext";

function MySlide() {
  const { uploadedData } = useData();

  // Process the uploaded data
  const processedData = uploadedData
    ? processMyData(uploadedData)
    : defaultSampleData;

  return (
    <div>
      {processedData.map((item) => (
        <div key={item.id}>{item.value}</div>
      ))}
    </div>
  );
}

function processMyData(rawData: any) {
  // Transform the uploaded JSON into the format you need
  // Example: Extract conversation topics, timestamps, etc.
  return transformedData;
}
```

## Data Persistence

⚠️ **Important**: The data is stored in React state and will be lost on page refresh.

For persistent storage, consider:

- Storing in browser localStorage/sessionStorage
- Saving to a database via the API endpoint
- Using a state management library with persistence

## API Integration

The uploaded data is also sent to `/api/process-data` endpoint where you can:

- Validate the data structure
- Perform server-side analysis
- Store in a database
- Generate additional insights
- Return processed results to the client

See `src/app/api/process-data/route.ts` for the API implementation.

## Security Considerations

- Data is only available during the active session
- Authentication is required to access the insights page
- Consider implementing data size limits for uploads
- Validate and sanitize uploaded data on both client and server
