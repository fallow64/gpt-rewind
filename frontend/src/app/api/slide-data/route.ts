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
      case -1:
        // Intro slide
        slideData = {};
        break;

      case 0:
        // Total hours slide
        slideData = {
          totalHours: 127.5, // Replace with actual calculation
        };
        break;

      case 1:
        // Monthly hours slide
        slideData = {
          monthlyHours: [12, 15, 18, 22, 19, 25, 28, 24, 20, 16, 14, 11], // Replace with actual data
        };
        break;

      case 2:
        // Time of day slide - 24 hours of activity data
        slideData = {
          hourlyActivity: [
            2,
            1,
            0,
            0,
            1,
            3, // 12am-6am (night)
            8,
            12,
            15,
            18,
            22,
            25, // 6am-12pm (morning)
            28,
            30,
            26,
            22,
            20,
            18, // 12pm-6pm (afternoon)
            24,
            28,
            32,
            26,
            18,
            8, // 6pm-12am (evening)
          ], // Replace with actual hourly activity data
        };
        break;
      case 3:
        // Longest conversation slide
        slideData = {
          longestConversationHours: 5.75,
        };
        break;

      case 4:
        // Easiest question slide
        slideData = {
          easiestQuestion: "write python", // Replace with actual simplest question
        };
        break;

      case 5:
        // Hardest question slide
        slideData = {
          hardestQuestion: "optimize distributed system architecture", // Replace with actual hardest question
        };
        break;

      case 6:
        // Estimated profession slide
        slideData = {
          estimatedProfession: "Software Engineer", // Replace with actual estimation
        };
        break;

      case 7:
        // Top topics slide
        slideData = {
          topTopics: ["Machine Learning", "Web Development", "Data Structures"], // Replace with actual top 3 topics
        };
        break;

      case 8:
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

      case 9:
        // Topics by hour slide
        slideData = {
          hourlyTopics: [
            "Sleep",
            "Sleep",
            "Sleep",
            "Sleep",
            "Sleep",
            "Sleep", // 12am-6am
            "Morning Routine",
            "Commute",
            "Work",
            "Work",
            "Work",
            "Lunch", // 6am-12pm
            "Meetings",
            "Work",
            "Work",
            "Break",
            "Projects",
            "Commute", // 12pm-6pm
            "Dinner",
            "Relaxation",
            "Hobbies",
            "Entertainment",
            "Homework",
            "Sleep", // 6pm-12am
          ], // Replace with actual hourly topics
        };
        break;

      case 10:
        // Outro slide
        slideData = {};
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
