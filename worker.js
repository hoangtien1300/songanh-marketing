/**
 * Cloudflare Worker for Song Anh Marketing Suite
 * Handles API routes for Notion comments proxy & static assets
 */

const NOTION_API_KEY = atob("bnRuXzIwMjMxNjk5ODU2NmFkQzVtb1Z3TER1NXZaY2pIRllMS2RjUGN2S08xbXExdUU=");
const NOTION_API_VERSION = "2022-06-28";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Handle CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    const token = env.NOTION_TOKEN || NOTION_API_KEY;

    // API: POST /api/notion/add-comment
    if (url.pathname === "/api/notion/add-comment" && request.method === "POST") {
      try {
        const body = await request.json();
        const { page_id, comment_text, author } = body;

        if (!page_id || !comment_text) {
          return new Response(
            JSON.stringify({ ok: false, error: "Thiếu page_id hoặc comment_text" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const prefix = author ? `[${author}]: ` : "";
        const finalContent = `${prefix}${comment_text}`;

        const notionResponse = await fetch("https://api.notion.com/v1/comments", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            parent: { page_id: page_id },
            rich_text: [
              {
                text: {
                  content: finalContent
                }
              }
            ]
          })
        });

        const data = await notionResponse.json();
        if (!notionResponse.ok) {
          return new Response(
            JSON.stringify({ ok: false, error: data }),
            { status: notionResponse.status, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        return new Response(
          JSON.stringify({ ok: true, comment: data }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // API: GET /api/notion/get-comments?page_id=...
    if (url.pathname === "/api/notion/get-comments" && request.method === "GET") {
      try {
        const pageId = url.searchParams.get("page_id");
        if (!pageId) {
          return new Response(
            JSON.stringify({ ok: false, error: "Thiếu page_id" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const notionResponse = await fetch(`https://api.notion.com/v1/comments?block_id=${pageId}`, {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION
          }
        });

        const data = await notionResponse.json();
        const comments = (data.results || []).map(c => {
          const text = (c.rich_text || []).map(t => t.plain_text || "").join("");
          const date = c.created_time ? c.created_time.substring(0, 10) : "";
          return { id: c.id, text, date };
        });

        return new Response(
          JSON.stringify({ ok: true, count: comments.length, comments }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // Default: Fallback to Cloudflare Workers Static Assets
    return env.ASSETS.fetch(request);
  }
};
