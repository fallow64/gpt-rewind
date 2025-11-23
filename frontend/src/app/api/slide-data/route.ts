import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/src/auth";

export async function GET(req: NextRequest) {
  try {
    // Check authentication
    const session = await auth();
    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Get pageIndex from query parameters
    const searchParams = req.nextUrl.searchParams;
    const pageIndex = searchParams.get("pageIndex");

    if (!pageIndex) {
      return NextResponse.json(
        { error: "pageIndex query parameter is required" },
        { status: 400 }
      );
    }

    const pageIndexNum = parseInt(pageIndex, 10);

    // TODO: Fetch data from your database or data source based on pageIndex
    // This is where you would query your stored conversation data
    // and calculate/return the specific data needed for that slide

    // Example response structure based on pageIndex
    let slideData;

    switch (pageIndexNum) {
      case 1:
        // Total hours slide
        slideData = {
          totalHours: 127.5, // Replace with actual calculation
        };
        break;

      case 2:
        // Monthly hours slide
        slideData = {
          monthlyHours: [12, 15, 18, 22, 19, 25, 28, 24, 20, 16, 14, 11], // Replace with actual data
        };
        break;

      default:
        return NextResponse.json(
          { error: `No data available for pageIndex ${pageIndexNum}` },
          { status: 404 }
        );
    }

    return NextResponse.json(slideData);
  } catch (error) {
    console.error("Error fetching slide data:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
