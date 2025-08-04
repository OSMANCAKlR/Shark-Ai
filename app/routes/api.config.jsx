/**
 * Config API Route
 * Returns current application configuration including dynamic URLs
 */
import { json } from "@remix-run/node";
import { readFileSync } from "fs";
import path from "path";

export async function loader({ request }) {
  try {
    // Read shopify.app.toml to get current application_url
    const tomlPath = path.join(process.cwd(), "shopify.app.toml");
    const tomlContent = readFileSync(tomlPath, "utf-8");

    // Simple regex to extract application_url
    const urlMatch = tomlContent.match(/application_url\s*=\s*"([^"]+)"/);
    const applicationUrl = urlMatch ? urlMatch[1] : null;

    console.log(`📡 Config API: Current application_url = ${applicationUrl}`);

    return json(
      {
        applicationUrl,
        success: true,
      },
      {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
          "Cache-Control": "no-cache", // Don't cache since URL changes frequently
        },
      },
    );
  } catch (error) {
    console.error("Error reading shopify.app.toml:", error);
    return json(
      {
        error: "Could not read application configuration",
        success: false,
      },
      {
        status: 500,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      },
    );
  }
}

export async function action({ request }) {
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }

  return json({ error: "Method not allowed" }, { status: 405 });
}
