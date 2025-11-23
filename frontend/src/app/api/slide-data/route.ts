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

      case 3:
        // Time of day slide
        slideData = {
          timeOfDayHours: [8.5, 32.0, 45.5, 41.5], // [night, morning, afternoon, evening] Replace with actual calculation
        };
        break;
      case 4:
        // Longest conversation slide
        slideData = {
          longestConversationHours: 5.75,
        };
        break;

      case 5:
        // Easiest question slide
        slideData = {
          easiestQuestion: "write python", // Replace with actual simplest question
        };
        break;

      case 6:
        // Hardest question slide
        slideData = {
          hardestQuestion: "optimize distributed system architecture", // Replace with actual hardest question
        };
        break;

      case 7:
        // Estimated profession slide
        slideData = {
          estimatedProfession: "Software Engineer", // Replace with actual estimation
        };
        break;

      case 8:
        // Top topics slide
        slideData = {
          topTopics: ["Machine Learning", "Web Development", "Data Structures"], // Replace with actual top 3 topics
        };
        break;

      case 9:
        // Topics by month slide
        slideData = {
          monthlyTopics: [
            "Python Basics",
            "Web Development",
            "Web Development",
            "Machine Learning",
            "Machine Learning",
            "Data Science",
            "APIs",
            "APIs",
            "Cloud Computing",
            "DevOps",
            "DevOps",
            "System Design",
          ], // Replace with actual monthly topics
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
