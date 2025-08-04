/**
 * Voice Token API Route
 * Generates LiveKit room tokens for voice chat sessions
 */
import { json } from "@remix-run/node";
import { AccessToken } from "livekit-server-sdk";

/**
 * Handle CORS preflight requests (GET)
 */
export async function loader({ request }) {
  // Handle OPTIONS requests (CORS preflight)
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: getCorsHeaders(request),
    });
  }

  return json(
    { error: "Method not allowed" },
    {
      status: 405,
      headers: getCorsHeaders(request),
    },
  );
}

/**
 * Generate LiveKit room token for voice chat (POST)
 */
export async function action({ request }) {
  // Handle preflight OPTIONS request
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: getCorsHeaders(request),
    });
  }
  try {
    const body = await request.json();
    const { conversation_id, shop_domain } = body;

    if (!conversation_id) {
      return json(
        { error: "Missing conversation_id" },
        { status: 400, headers: getCorsHeaders(request) },
      );
    }

    // Get LiveKit credentials from environment
    const apiKey = process.env.LIVEKIT_API_KEY;
    const apiSecret = process.env.LIVEKIT_API_SECRET;

    if (!apiKey || !apiSecret) {
      console.error("LiveKit credentials not configured");
      return json(
        { error: "Voice chat not configured" },
        { status: 500, headers: getCorsHeaders(request) },
      );
    }

    // Create room name based on conversation
    const roomName = `shopify-voice-${conversation_id}`;

    // Generate access token
    const token = new AccessToken(apiKey, apiSecret, {
      identity: "user", // User identity
      ttl: "1h", // Token valid for 1 hour
    });

    // Grant permissions
    token.addGrant({
      room: roomName,
      roomJoin: true,
      canPublish: true,
      canSubscribe: true,
      canPublishData: true,
    });

    const jwt = await token.toJwt();

    return json(
      {
        token: jwt,
        room_name: roomName,
        url: process.env.LIVEKIT_URL,
      },
      { headers: getCorsHeaders(request) },
    );
  } catch (error) {
    console.error("Error generating voice token:", error);
    return json(
      { error: "Failed to generate token" },
      { status: 500, headers: getCorsHeaders(request) },
    );
  }
}

/**
 * Gets CORS headers for the response
 * @param {Request} request - The request object
 * @returns {Object} CORS headers object
 */
function getCorsHeaders(request) {
  const origin = request.headers.get("Origin") || "*";
  const requestHeaders =
    request.headers.get("Access-Control-Request-Headers") ||
    "Content-Type, Accept";

  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": requestHeaders,
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Max-Age": "86400", // 24 hours
  };
}
