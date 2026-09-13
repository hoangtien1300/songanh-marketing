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
    const MEMBERS_DB_ID = env.MEMBERS_DB_ID || "19b4b5e73d90803abda4dff1da951ef6";

    // API: POST /api/auth/login (Xác thực đăng nhập qua Bảng Thành Viên Notion)
    if (url.pathname === "/api/auth/login" && request.method === "POST") {
      try {
        const body = await request.json().catch(() => ({}));
        const inputUser = (body.username || "").trim().toLowerCase();
        const inputPass = (body.password || "").trim();

        if (!inputUser || !inputPass) {
          return new Response(
            JSON.stringify({ success: false, message: "Vui lòng nhập đầy đủ Tên đăng nhập và Mật khẩu!" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        // Truy vấn Notion Bảng Thành Viên có cấp Webapp ID
        const nRes = await fetch(`https://api.notion.com/v1/databases/${MEMBERS_DB_ID}/query`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            filter: {
              property: "Webapp ID",
              rich_text: {
                is_not_empty: true
              }
            }
          })
        });

        if (!nRes.ok) {
          const errData = await nRes.json().catch(() => ({}));
          return new Response(
            JSON.stringify({ success: false, message: "Lỗi kết nối cơ sở dữ liệu Notion", details: errData }),
            { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const data = await nRes.json();
        const members = data.results || [];
        let matchedMember = null;

        for (const m of members) {
          const props = m.properties || {};

          // Lấy Webapp ID
          const widList = (props["Webapp ID"] && props["Webapp ID"].rich_text) || [];
          const rawWid = widList.map(t => t.plain_text || "").join("").trim().toLowerCase();

          // Lấy Phone
          const phone = (props["Phone"] && props["Phone"].phone_number) || "";
          const phoneClean = phone.replace(/[^0-9]/g, "");
          const inputClean = inputUser.replace(/[^0-9]/g, "");

          // Lấy Webapp Password
          const pwdList = (props["Webapp Password"] && props["Webapp Password"].rich_text) || [];
          const rawPwd = pwdList.map(t => t.plain_text || "").join("").trim();

          // Kiểm tra khớp tài khoản (theo Webapp ID hoặc SĐT)
          const isUserMatch = (rawWid && rawWid === inputUser) || 
                              (inputClean.length >= 8 && phoneClean.includes(inputClean));

          if (isUserMatch) {
            if (rawPwd === inputPass) {
              const nameList = (props["Tên"] && props["Tên"].title) || [];
              const name = nameList.map(t => t.plain_text || "").join("").trim() || "Thành viên Song Anh";

              // Kiểm tra trạng thái thành viên
              const statusObj = props["Trạng thái thành viên"] && props["Trạng thái thành viên"].status;
              const statusName = (statusObj && statusObj.name) || "";
              if (statusName.toLowerCase().includes("nghỉ") || statusName.toLowerCase().includes("khóa")) {
                return new Response(
                  JSON.stringify({ success: false, message: "Tài khoản này hiện đang tạm khóa hoặc đã ngưng hoạt động trên Notion!" }),
                  { status: 403, headers: { ...corsHeaders, "Content-Type": "application/json" } }
                );
              }

              // Xác định vai trò & avatar hiển thị
              let role = "Thành viên Song Anh";
              let avatar = "SA";
              const nameUpper = name.toUpperCase();
              if (nameUpper.includes("TIẾN") || rawWid.includes("tien") || rawWid === "admin") {
                role = "Quản trị viên / Điều Hành";
                avatar = "PT";
              } else if (nameUpper.includes("SANG") || rawWid.includes("sang")) {
                role = "Chuyên viên Kinh Doanh";
                avatar = "VS";
              } else if (nameUpper.includes("THIỆN")) {
                role = "Ban Giám Đốc";
                avatar = "MT";
              } else {
                const words = name.trim().split(/\s+/);
                avatar = words.length >= 2 ? (words[0][0] + words[words.length - 1][0]).toUpperCase() : name.substring(0, 2).toUpperCase();
              }

              // Lấy quyền Webapp permission ('Admin' hoặc 'Member')
              const permObj = props["Webapp permission"] && props["Webapp permission"].select;
              const permRaw = ((permObj && permObj.name) || "").trim().toLowerCase();
              let permission = "member";
              if (permRaw === "admin" || rawWid === "admin" || rawWid.includes("tien") || nameUpper.includes("TIẾN")) {
                permission = "admin";
              } else if (permRaw === "member") {
                permission = "member";
              } else {
                permission = (nameUpper.includes("TIẾN") || nameUpper.includes("THIỆN")) ? "admin" : "member";
              }

              matchedMember = {
                id: m.id,
                username: rawWid || inputUser,
                fullName: name,
                roleName: role,
                permission: permission,
                avatar: avatar,
                phone: phone
              };
              break;
            } else {
              return new Response(
                JSON.stringify({ success: false, message: "Mật khẩu truy cập không chính xác. Vui lòng kiểm tra lại!" }),
                { status: 401, headers: { ...corsHeaders, "Content-Type": "application/json" } }
              );
            }
          }
        }

        if (!matchedMember) {
          return new Response(
            JSON.stringify({ success: false, message: "Tài khoản chưa được cấp quyền truy cập trong Bảng Thành Viên trên Notion!" }),
            { status: 401, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const userSessionToken = "sa_notion_" + Math.random().toString(36).substring(2) + Date.now().toString(36);

        return new Response(
          JSON.stringify({
            success: true,
            user: matchedMember,
            token: userSessionToken,
            message: "Đăng nhập thành công!"
          }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );

      } catch (err) {
        return new Response(
          JSON.stringify({ success: false, message: "Lỗi máy chủ: " + err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // API: GET /api/gsc-data (Trả về dữ liệu GSC Master Audit live)
    if (url.pathname === "/api/gsc-data" && request.method === "GET") {
      try {
        const assetUrl = new URL("/gsc_live_data.json", request.url);
        const assetRes = env.ASSETS ? await env.ASSETS.fetch(new Request(assetUrl)) : await fetch(assetUrl);
        if (assetRes.ok) {
          const gscData = await assetRes.json();
          return new Response(JSON.stringify(gscData), {
            status: 200,
            headers: {
              ...corsHeaders,
              "Content-Type": "application/json; charset=utf-8",
              "Cache-Control": "public, max-age=300"
            }
          });
        }
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

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

    // API: POST /api/notion/update-task
    if (url.pathname === "/api/notion/update-task" && request.method === "POST") {
      try {
        const body = await request.json();
        const { page_id, title, status, done_count, note, description, remind_date, repeat_days, role_id, category_id, channel_id } = body;

        if (!page_id) {
          return new Response(
            JSON.stringify({ ok: false, error: "Thiếu page_id" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const properties = {};
        if (title !== undefined && title !== null && title.trim() !== "") {
          properties["Tên công việc"] = { title: [{ text: { content: title.trim() } }] };
        }
        if (status) {
          properties["Trạng thái"] = { status: { name: status } };
        }
        if (done_count !== undefined && done_count !== null && done_count !== "") {
          properties["Đã thực hiện"] = { number: parseInt(done_count) || 0 };
        }
        if (note !== undefined && note !== null) {
          properties["Ghi chú"] = { rich_text: [{ text: { content: String(note) } }] };
        }
        if (description !== undefined && description !== null) {
          properties["Mô tả công việc"] = { rich_text: [{ text: { content: String(description) } }] };
        }
        if (remind_date !== undefined) {
          if (remind_date && remind_date.trim() !== "") {
            properties["Nhắc hẹn"] = { date: { start: remind_date } };
          } else {
            properties["Nhắc hẹn"] = { date: null };
          }
        }
        if (role_id !== undefined) {
          properties["Vai trò"] = { relation: role_id ? [{ id: role_id }] : [] };
        }
        if (category_id !== undefined) {
          properties["Hạng mục"] = { relation: category_id ? [{ id: category_id }] : [] };
        }
        if (channel_id !== undefined) {
          properties["Kênh Social"] = { relation: channel_id ? [{ id: channel_id }] : [] };
        }
        if (Array.isArray(repeat_days) && repeat_days.length > 0) {
          properties["Lặp lại"] = { multi_select: repeat_days.map(d => ({ name: d })) };
        }

        const notionResponse = await fetch(`https://api.notion.com/v1/pages/${page_id}`, {
          method: "PATCH",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ properties })
        });

        const data = await notionResponse.json();
        if (!notionResponse.ok) {
          return new Response(
            JSON.stringify({ ok: false, error: data }),
            { status: notionResponse.status, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        return new Response(
          JSON.stringify({ ok: true, page: data }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // API: POST /api/notion/update-content-post
    if (url.pathname === "/api/notion/update-content-post" && request.method === "POST") {
      try {
        const body = await request.json();
        const { page_id, date_val, property_name, spin_text } = body;

        if (!page_id) {
          return new Response(
            JSON.stringify({ ok: false, error: "Thiếu page_id" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const targetProp = property_name || "Ngày đăng Zalo (0981169200)";
        const properties = {};

        if (date_val !== undefined) {
          if (date_val && String(date_val).trim() !== "") {
            let isoDate = String(date_val).trim();
            if (isoDate.includes("/")) {
              const parts = isoDate.split("/");
              if (parts.length === 3) {
                isoDate = `${parts[2]}-${parts[1].padStart(2, "0")}-${parts[0].padStart(2, "0")}`;
              }
            }
            properties[targetProp] = { date: { start: isoDate } };
          } else {
            properties[targetProp] = { date: null };
          }
        }

        if (spin_text !== undefined && spin_text !== null && String(spin_text).trim() !== "") {
          properties["Spin zalo 0981169200"] = {
            rich_text: [{ text: { content: String(spin_text).trim() } }]
          };
        }

        const notionResponse = await fetch(`https://api.notion.com/v1/pages/${page_id}`, {
          method: "PATCH",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ properties })
        });

        const data = await notionResponse.json();
        if (!notionResponse.ok) {
          return new Response(
            JSON.stringify({ ok: false, error: data }),
            { status: notionResponse.status, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        return new Response(
          JSON.stringify({ ok: true, page: data }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // API: GET /api/notion/get-freshness-article?page_id=...
    if (url.pathname === "/api/notion/get-freshness-article" && request.method === "GET") {
      try {
        const pageId = url.searchParams.get("page_id");
        if (!pageId) {
          return new Response(
            JSON.stringify({ ok: false, error: "Thiếu page_id" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const pageRes = await fetch(`https://api.notion.com/v1/pages/${pageId}`, {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION
          }
        });
        const pageData = await pageRes.json();
        const props = pageData.properties || {};

        let note = "";
        if (props["Ghi chú"] && props["Ghi chú"].rich_text) {
          note = props["Ghi chú"].rich_text.map(t => t.plain_text || "").join("");
        }

        const blocksRes = await fetch(`https://api.notion.com/v1/blocks/${pageId}/children?page_size=100`, {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION
          }
        });
        const blocksData = await blocksRes.json();
        const results = blocksData.results || [];

        let markdownLines = [];
        for (const b of results) {
          const btype = b.type;
          if (btype && b[btype] && b[btype].rich_text) {
            const txt = b[btype].rich_text.map(t => t.plain_text || "").join("");
            if (btype === "heading_1") markdownLines.push(`# ${txt}`);
            else if (btype === "heading_2") markdownLines.push(`## ${txt}`);
            else if (btype === "heading_3") markdownLines.push(`### ${txt}`);
            else if (btype === "bulleted_list_item") markdownLines.push(`- ${txt}`);
            else if (btype === "numbered_list_item") markdownLines.push(`1. ${txt}`);
            else if (btype === "to_do") markdownLines.push(b.to_do.checked ? `- [x] ${txt}` : `- [ ] ${txt}`);
            else markdownLines.push(txt);
          } else if (btype === "divider") {
            markdownLines.push("---");
          }
        }

        return new Response(
          JSON.stringify({
            ok: true,
            note: note,
            body_content: markdownLines.join("\n"),
            updated_time: pageData.last_edited_time
          }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // API: POST /api/notion/update-freshness-article
    if (url.pathname === "/api/notion/update-freshness-article" && request.method === "POST") {
      try {
        const body = await request.json();
        const { page_id, note, content } = body;

        if (!page_id) {
          return new Response(
            JSON.stringify({ ok: false, error: "Thiếu page_id" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const properties = {};
        if (note !== undefined && note !== null) {
          properties["Ghi chú"] = {
            rich_text: [{ text: { content: String(note).substring(0, 2000) } }]
          };
        }
        const todayStr = new Date().toISOString().substring(0, 10);
        properties["Ngày cập nhật"] = { date: { start: todayStr } };

        const pagePatchRes = await fetch(`https://api.notion.com/v1/pages/${page_id}`, {
          method: "PATCH",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ properties })
        });

        if (content && typeof content === "string" && content.trim()) {
          const lines = content.split("\n");
          const children = [];

          children.push({ object: "block", type: "divider", divider: {} });
          children.push({
            object: "block",
            type: "heading_2",
            heading_2: {
              rich_text: [{ type: "text", text: { content: `🎯 KẾ HOẠCH FRESHNESS 2026 (${new Date().toLocaleDateString("vi-VN")})` } }]
            }
          });

          for (const line of lines.slice(0, 40)) {
            const tr = line.trim();
            if (!tr) continue;
            if (tr.startsWith("## ")) {
              children.push({
                object: "block",
                type: "heading_2",
                heading_2: { rich_text: [{ type: "text", text: { content: tr.replace("## ", "") } }] }
              });
            } else if (tr.startsWith("### ")) {
              children.push({
                object: "block",
                type: "heading_3",
                heading_3: { rich_text: [{ type: "text", text: { content: tr.replace("### ", "") } }] }
              });
            } else if (tr.startsWith("- [ ] ") || tr.startsWith("- [x] ")) {
              children.push({
                object: "block",
                type: "to_do",
                to_do: {
                  checked: tr.startsWith("- [x] "),
                  rich_text: [{ type: "text", text: { content: tr.substring(6) } }]
                }
              });
            } else if (tr.startsWith("- ") || tr.startsWith("* ")) {
              children.push({
                object: "block",
                type: "bulleted_list_item",
                bulleted_list_item: { rich_text: [{ type: "text", text: { content: tr.substring(2) } }] }
              });
            } else if (!tr.startsWith("# ")) {
              children.push({
                object: "block",
                type: "paragraph",
                paragraph: { rich_text: [{ type: "text", text: { content: tr.substring(0, 2000) } }] }
              });
            }
          }

          if (children.length > 0) {
            await fetch(`https://api.notion.com/v1/blocks/${page_id}/children`, {
              method: "PATCH",
              headers: {
                "Authorization": `Bearer ${token}`,
                "Notion-Version": NOTION_API_VERSION,
                "Content-Type": "application/json"
              },
              body: JSON.stringify({ children })
            });
          }
        }

        const data = await pagePatchRes.json();
        return new Response(
          JSON.stringify({ ok: true, page: data }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // Rewrite /login to /index.html
    if (url.pathname === "/login") {
      const newUrl = new URL(request.url);
      newUrl.pathname = "/index.html";
      return env.ASSETS.fetch(new Request(newUrl, request));
    }

    // Default: Fallback to Cloudflare Workers Static Assets
    return env.ASSETS.fetch(request);
  }
};
