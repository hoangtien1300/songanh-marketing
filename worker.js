import crypto from 'node:crypto';
import { Buffer } from 'node:buffer';

/**
 * Cloudflare Worker for Song Anh Marketing Suite
 * Handles API routes for Notion comments proxy, Google Sheets live sync & static assets
 */

const NOTION_API_KEY = atob("bnRuXzIwMjMxNjk5ODU2NmFkQzVtb1Z3TER1NXZaY2pIRllMS2RjUGN2S08xbXExdUU=");
const NOTION_API_VERSION = "2022-06-28";
const GEMINI_API_KEY = "AIzaSyCfHOamit9Is482exJFgQGPuURfjnfnWzA";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

// Google Service Account Authentication for Google Sheets API
const GOOGLE_SA_B64 = "eyJjbGllbnRfZW1haWwiOiAic29uZ2FuaC1zZW8tYm90QHNvbmctYW5oLXNlby1hbmFseXRpY3MuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLCAicHJpdmF0ZV9rZXkiOiAiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdmdJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLZ3dnZ1NrQWdFQUFvSUJBUUN4OEc1ekQreFAvc2c4XG5YUldHc2NvaVFvOGVwaHJESC9TZGV2eGczWWsrN2tXTVp2L0EvUFdWNVgwRGdIRjJNWi85UGZlRnpadDVUaFRsXG5IaDBISzVBR3pjU2tuWVBtSEFLR0dZZ0k0V1BWVmx3MVVSRmFaRExHSXNha1dTTGo0N3FqSnJaVHdEMTVteVVoXG5CdklWVEFlSzVpQ0FXYnpVS21zdjlaeXJ2djVJZlQzVTdIZWZhdW5yZExWQi82T3A4TDNuMUZ6ZUJyaUhyRUgzXG5oRDJkdjZFWFh2OVFReEV6QklZVWVTaEFBSEN0UXhBMy9YTUQ2aHJDREZjVjV5cEpHQVp0a0ZYOUJPRWU1U3dRXG5kSGIyUzFMZ1pQWmpiVm5qRTAzNUgrWEpmOGtKY2lTVUY1cS9vRFpBWmh1RDFLTW84OHJiRTNQbjRZeDJUeFZlXG52Mk12MmpnUEFnTUJBQUVDZ2dFQUpGU242SHhXenBxQnZibHZ2TG11UU1LQVFFeS82Qmt0TTc0NXEzbHdIVlkvXG5Bd1RBc1dHMHJ1OVZVQks0bDk1WUFUZld3dzRROFhxY3o0OFBkRGhUeHQvYWg1WFZxWFVNbXQ2NXBMNklTTFhDXG5TK3lLYzM5RDBxcWxEa2RZMVZqWThaamszMExBQ29VLzFuZDVsQm1hN0tSQi9KTFYrQ2ZWRE16RU9WamN5R1hhXG5wNEZmR0EzQ2lpMzZ5LzJCUi85Qkk1U202dEtCMk1yVkZxck13MGNIRSttUTExZmhINGwrZkRIYzFzSytMa01GXG5WUmpoM2FyMXZwVzhRL1ZUSEZQQmVqd0R5QWJ0akg5dzdlNEhqUnhmWVZoTHpRVWVmQ2k5bmtqTVVFbjhjaDdOXG5udEhHRHNoNFRtZk42TlJwZnNqVHhOaER5a2NzanJHblBOb0I4ZWpxMlFLQmdRRGdXT1ZaUlI3RU0vMGlvOW52XG5vUThEV2N4YnlnZmNQZUtaS2tSMW9FU2d2SS9uM0p6dUdJRTcranpsVy9PbWUvb3A5SXdMOXF6RHpEMmtKSGhoXG5yekhzZzU5eHppT3ZBZWExVVdQWWZodk51Y3FyaGpxbmJ4Y2NxZG5wV2tjZkcxQ3J2emVzRUhaM1VKUm9WdlhjXG5sTDRTekNZUlVvVW5EODFVZlhNcXFocnhTd0tCZ1FETEMxZVlBS0ZpNjNuWmp1NlBqMnlRYmgrdCt3Qmx1VlRFXG5mcWlkT3NOVXlKeXZQbDl2MmdJbWxMOWVtY0ExQmZlS1gwR1g1ejlnL20wMUN6cmcxQlNpRGZUVkI3UW1JUFJWXG54b2JyYnVpRGFrdm9UNlVUUmRYYmJXcTFFbWgvZEx4bm1lZFJ5MTlCVnhia2xILzkwOGNxZlo5Q004OC9DMGlJXG5PTU5DODJTZHpRS0JnRWFYRWdzbHVZbUl4alI1RStEWGI0N2hXWERrUDlibnpmM2RrODdqRDlUM245d1h5WFVOXG5WdFNWWjBYUHlmbHZkd1p1Z1FaZXBudXhMeEFQdmFVVzZBR0FaTkg5UjdNUVNSUnlPSlZ0RUxpSnBpQ1VTcTVXXG5RUkp1eXpjbWhjeGUzdUk3ZDN2M2JoOGF4cWVSL1NoYjBQYS9MNWN4dk4zT2xnL29yUzBXZXdYREFvR0JBTUl1XG5Nck0zeHlBbk92MEphTFQ2NFVTdlRMVENtM3F0WjVnVDJZV2tzVEhnT1ppTytnNnFXK3d4eldMWGY2NDE2cXIyXG50bkJqdzRVclRaMnhBN29JbVVMeVBmZU55b2U4ZEcrajBWeFBVU1o4L2VOS2FBQ3FoUCs1QUpmeTV1VWQ2eURaXG5XeFFxZndxcUUwYS9qamhkMU5lYUZEam4rNGU3YnI1NEtxVll5Qnp4QW9HQkFOVncrQXV1M1dtMk9aZnc3eUp6XG55TEcwYWYrR1JqQm9Wd0lpRkV3Nmg0Y3pQR0hVM3pUVW53RkIzOHh0MGd3K1dZZjRTMFJnTGw4UjZvMjFuVW9VXG5DcDJibDZEQVdoS3hUb1hiRXNXWnRZR1NneFVXOG4xQ0g2YlJKZXIxNHF3elQyaXpjdHlLRHBXUGQ3MTJmcFJYXG5jeFZoaDJudjd2eGoxQ0haNnNZb1N0MW5cbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsICJwcm9qZWN0X2lkIjogInNvbmctYW5oLXNlby1hbmFseXRpY3MifQ==";
const GOOGLE_SPREADSHEET_ID = "1SBTFW0cghaPqucocvc7R3KfTvnTR5g5rngCLbMeK64g";

let cachedGoogleToken = null;
let googleTokenExpiresAt = 0;

async function getGoogleSheetsToken() {
  const now = Math.floor(Date.now() / 1000);
  if (cachedGoogleToken && now < googleTokenExpiresAt - 120) {
    return cachedGoogleToken;
  }
  
  const sa = JSON.parse(Buffer.from(GOOGLE_SA_B64, 'base64').toString('utf-8'));
  const header = { alg: 'RS256', typ: 'JWT' };
  const claim = {
    iss: sa.client_email,
    scope: 'https://www.googleapis.com/auth/spreadsheets',
    aud: 'https://oauth2.googleapis.com/token',
    exp: now + 3600,
    iat: now
  };
  
  const b64Header = Buffer.from(JSON.stringify(header)).toString('base64url');
  const b64Claim = Buffer.from(JSON.stringify(claim)).toString('base64url');
  const signInput = `${b64Header}.${b64Claim}`;
  
  const sign = crypto.createSign('RSA-SHA256');
  sign.update(signInput);
  sign.end();
  const signature = sign.sign(sa.private_key, 'base64url');
  const assertion = `${signInput}.${signature}`;
  
  const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      assertion: assertion
    }).toString()
  });
  
  const tokenData = await tokenRes.json();
  if (!tokenData.access_token) {
    throw new Error('Google OAuth2 error: ' + JSON.stringify(tokenData));
  }
  
  cachedGoogleToken = tokenData.access_token;
  googleTokenExpiresAt = now + (tokenData.expires_in || 3600);
  return cachedGoogleToken;
}

const WEBSITE_SHEET_MAP = {
  "mohinhkientruc.org": "1SBTFW0cghaPqucocvc7R3KfTvnTR5g5rngCLbMeK64g",
  "mohinh3d.org": "1GgvoisIm09WCo1nDvk5QqBx63dRhAsKNjWAQ561kf60",
  "architecturalmodel.org": "15Ju555vjMbR_d8vg97THuJxdrUrSP1TJyTzq0ENshqI",
  "mohinhsonganh.com": "1iOPel0UY3wPiowrb6KNGAOLCsFh950efgFw6UoJp_yo",
  "vatlieumohinh.com": "1WCKlTZ2ney41Ntd_RNRiQz08PZ08aImvVNjU9Uald7A"
};

function stripHtmlTagsAndEntities(html) {
  if (!html) return "";
  return String(html)
    .replace(/<[^>]*>/g, " ")
    .replace(/&#8211;/g, "–")
    .replace(/&#8212;/g, "—")
    .replace(/&#8230;/g, "…")
    .replace(/&#038;|&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#039;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/\s+/g, " ")
    .trim();
}

async function syncPostToGoogleSheet({ channel, postUrl, title, status, caption, update_type }) {
  if (!postUrl || postUrl.trim() === '') return null;
  const cleanPostUrl = postUrl.trim();
  const cleanDomain = cleanPostUrl.replace(/^https?:\/\//i, '').split('/')[0].toLowerCase();

  let targetSheetId = null;
  let matchedDomain = null;
  for (const [d, sid] of Object.entries(WEBSITE_SHEET_MAP)) {
    if (cleanDomain.includes(d) || (channel && channel.toLowerCase().includes(d))) {
      targetSheetId = sid;
      matchedDomain = d;
      break;
    }
  }

  if (!targetSheetId) {
    return { ok: false, reason: "No matching Google Sheet found for domain: " + cleanDomain };
  }

  const googleToken = await getGoogleSheetsToken();
  if (!googleToken) {
    return { ok: false, reason: "Could not obtain Google Sheets access token" };
  }

  // 1. Cố gắng lấy dữ liệu từ WordPress REST API công khai
  let wpData = null;
  try {
    const urlObj = new URL(cleanPostUrl);
    const pathParts = urlObj.pathname.split('/').filter(Boolean);
    const slug = pathParts.length > 0 ? pathParts[pathParts.length - 1] : "";
    if (slug) {
      const wpRes = await fetch(`https://${matchedDomain}/wp-json/wp/v2/posts?slug=${encodeURIComponent(slug)}`, {
        headers: { "Accept": "application/json" }
      });
      if (wpRes.ok) {
        const postsList = await wpRes.json();
        if (Array.isArray(postsList) && postsList.length > 0) {
          wpData = postsList[0];
        }
      }
      if (!wpData) {
        const wpPageRes = await fetch(`https://${matchedDomain}/wp-json/wp/v2/pages?slug=${encodeURIComponent(slug)}`, {
          headers: { "Accept": "application/json" }
        });
        if (wpPageRes.ok) {
          const pagesList = await wpPageRes.json();
          if (Array.isArray(pagesList) && pagesList.length > 0) {
            wpData = pagesList[0];
          }
        }
      }
    }
  } catch (wpErr) {
    console.warn("WP REST API lookup skipped:", wpErr.message);
  }

  const wpTitle = wpData && wpData.title && wpData.title.rendered ? stripHtmlTagsAndEntities(wpData.title.rendered) : (title || "").trim();
  const wpExcerpt = wpData && wpData.excerpt && wpData.excerpt.rendered ? stripHtmlTagsAndEntities(wpData.excerpt.rendered) : (caption || "").trim();
  const wpId = wpData ? wpData.id : "";

  // 2. Đọc toàn bộ tab Url từ Google Sheet
  const getRowsRes = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${targetSheetId}/values/Url!A:W`, {
    headers: { 'Authorization': `Bearer ${googleToken}` }
  });

  if (!getRowsRes.ok) {
    const errText = await getRowsRes.text();
    return { ok: false, error: errText };
  }

  const getRowsData = await getRowsRes.json();
  const allRows = getRowsData.values || [];
  if (allRows.length === 0) {
    return { ok: false, reason: "Tab Url is empty in Google Sheet" };
  }

  const headerRow = allRows[0];
  const colMap = {};
  for (let idx = 0; idx < headerRow.length; idx++) {
    const h = headerRow[idx].trim().toLowerCase();
    if (h.includes('đường dẫn url')) colMap.url = idx;
    if (h.includes('tiêu đề') && !h.includes('title 1')) colMap.title = idx;
    if (h.includes('trạng thái wp')) colMap.status_wp = idx;
    if (h === 'trạng thái') colMap.status = idx;
    if (h.includes('title 1') && !h.includes('length')) colMap.title1 = idx;
    if (h.includes('title 1 length')) colMap.title1_len = idx;
    if (h.includes('meta description 1') && !h.includes('length')) colMap.meta = idx;
    if (h.includes('meta description 1 length')) colMap.meta_len = idx;
    if (h.includes('h1')) colMap.h1 = idx;
    if (h.includes('ngày đăng')) colMap.date_published = idx;
    if (h.includes('ngày cập nhật')) colMap.date_modified = idx;
    if (h.includes('id wp')) colMap.wp_id = idx;
    if (h.includes('ghi chú')) colMap.notes = idx;
  }

  if (colMap.url === undefined) colMap.url = 2;
  if (colMap.title === undefined) colMap.title = 1;
  if (colMap.status === undefined) colMap.status = 10;
  if (colMap.title1 === undefined) colMap.title1 = 12;
  if (colMap.title1_len === undefined) colMap.title1_len = 13;
  if (colMap.date_modified === undefined) colMap.date_modified = 20;
  if (colMap.notes === undefined) colMap.notes = 22;

  const normalizeUrl = (u) => String(u || '').trim().toLowerCase().replace(/\/+$/, '');
  const targetNormUrl = normalizeUrl(cleanPostUrl);

  let targetRowIdx = -1;
  for (let r = 1; r < allRows.length; r++) {
    const rowUrl = normalizeUrl(allRows[r][colMap.url]);
    if (rowUrl === targetNormUrl || (targetNormUrl !== '' && rowUrl.includes(targetNormUrl))) {
      targetRowIdx = r + 1;
      break;
    }
  }

  const now = new Date();
  const vnTime = new Date(now.getTime() + (7 * 60 * 60 * 1000));
  const dd = String(vnTime.getUTCDate()).padStart(2, "0");
  const mm = String(vnTime.getUTCMonth() + 1).padStart(2, "0");
  const yyyy = vnTime.getUTCFullYear();
  const formattedDateVN = `${dd}/${mm}/${yyyy}`;

  const actStatus = (status === 'Đã xuất bản' || status === 'publish') ? 'Đã hoàn thành' : (status || 'Đang làm');
  const logNoteText = (caption || title || "").substring(0, 400);

  if (targetRowIdx > 1) {
    // Cập nhật dòng cũ
    const curRow = allRows[targetRowIdx - 1] || [];
    while (curRow.length < 24) curRow.push('');

    if (colMap.title !== undefined) curRow[colMap.title] = wpTitle;
    if (colMap.status_wp !== undefined) curRow[colMap.status_wp] = 'publish';
    if (colMap.status !== undefined) curRow[colMap.status] = actStatus;
    if (colMap.title1 !== undefined) curRow[colMap.title1] = wpTitle;
    if (colMap.title1_len !== undefined) curRow[colMap.title1_len] = String(wpTitle.length);
    if (colMap.date_modified !== undefined) curRow[colMap.date_modified] = formattedDateVN;
    if (colMap.wp_id !== undefined && wpId) curRow[colMap.wp_id] = String(wpId);
    
    if (colMap.notes !== undefined) {
      const notePrefix = `[${update_type || 'Refresh'} ${formattedDateVN}]`;
      curRow[colMap.notes] = curRow[colMap.notes] ? `${curRow[colMap.notes]}\n${notePrefix} ${logNoteText}` : `${notePrefix} ${logNoteText}`;
    }

    const maxColLetter = String.fromCharCode(65 + Math.min(25, curRow.length - 1));
    await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${targetSheetId}/values/Url!A${targetRowIdx}:${maxColLetter}${targetRowIdx}?valueInputOption=USER_ENTERED`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${googleToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ values: [curRow] })
    });

    return { ok: true, action: 'updated', row: targetRowIdx, domain: matchedDomain, title: wpTitle };
  } else {
    // Thêm dòng mới
    const newCounter = allRows.length > 1 ? allRows.length : 1;
    const newCode = `URL-${String(newCounter).padStart(3, '0')}`;
    const isPage = cleanPostUrl.includes('/gioi-thieu') || cleanPostUrl.includes('/lien-he') || cleanPostUrl.includes('/dich-vu');

    const newRow = new Array(24).fill('');
    newRow[0] = newCode;
    if (colMap.title !== undefined) newRow[colMap.title] = wpTitle;
    if (colMap.url !== undefined) newRow[colMap.url] = cleanPostUrl;
    newRow[3] = isPage ? 'Page' : 'Post';
    if (colMap.status_wp !== undefined) newRow[colMap.status_wp] = 'publish';
    newRow[8] = 'Xuất bản & Tối ưu bài viết mới';
    newRow[9] = '✍️ Văn & 🔍 Trí';
    if (colMap.status !== undefined) newRow[colMap.status] = actStatus;
    if (colMap.title1 !== undefined) newRow[colMap.title1] = wpTitle;
    if (colMap.title1_len !== undefined) newRow[colMap.title1_len] = String(wpTitle.length);
    if (colMap.meta !== undefined) newRow[colMap.meta] = wpExcerpt || logNoteText;
    if (colMap.meta_len !== undefined) newRow[colMap.meta_len] = String((wpExcerpt || logNoteText).length);
    if (colMap.h1 !== undefined) newRow[colMap.h1] = wpTitle;
    if (colMap.date_published !== undefined) newRow[colMap.date_published] = formattedDateVN;
    if (colMap.date_modified !== undefined) newRow[colMap.date_modified] = formattedDateVN;
    if (colMap.wp_id !== undefined && wpId) newRow[colMap.wp_id] = String(wpId);
    if (colMap.notes !== undefined) newRow[colMap.notes] = `[${update_type || 'New Post'} ${formattedDateVN}] ${logNoteText}`;

    await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${targetSheetId}/values/Url!A:append?valueInputOption=USER_ENTERED`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${googleToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ values: [newRow] })
    });

    return { ok: true, action: 'appended', code: newCode, domain: matchedDomain, title: wpTitle };
  }
}

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

        // Truy vấn Notion Bảng Thành Viên chỉ lấy các account có cả Webapp ID và Webapp Password
        const nRes = await fetch(`https://api.notion.com/v1/databases/${MEMBERS_DB_ID}/query`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            filter: {
              and: [
                {
                  property: "Webapp ID",
                  rich_text: {
                    is_not_empty: true
                  }
                },
                {
                  property: "Webapp Password",
                  rich_text: {
                    is_not_empty: true
                  }
                }
              ]
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
          const rawWid = widList.map(t => t.plain_text || "").join("").trim();
          const rawWidLower = rawWid.toLowerCase();

          // Lấy Webapp Password
          const pwdList = (props["Webapp Password"] && props["Webapp Password"].rich_text) || [];
          const rawPwd = pwdList.map(t => t.plain_text || "").join("").trim();

          // Lấy Phone
          const phone = (props["Phone"] && props["Phone"].phone_number) || "";
          const phoneClean = phone.replace(/[^0-9]/g, "");
          const inputClean = inputUser.replace(/[^0-9]/g, "");

          // Lấy Tên
          const nameList = (props["Tên"] && props["Tên"].title) || (props["Name"] && props["Name"].title) || [];
          const name = nameList.map(t => t.plain_text || "").join("").trim() || "Thành viên Song Anh";
          const nameLower = name.toLowerCase();

          // Kiểm tra khớp tài khoản (theo Webapp ID, SĐT, hoặc Tên)
          const isUserMatch = (rawWidLower === inputUser) ||
                              (rawWidLower.replace(/[^a-z0-9]/g, "") === inputUser.replace(/[^a-z0-9]/g, "")) ||
                              (inputClean.length >= 9 && phoneClean.includes(inputClean)) ||
                              (nameLower === inputUser);

          if (isUserMatch) {
            const isPassMatch = (rawPwd === inputPass);
            if (isPassMatch) {

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
        const newUrl = new URL(request.url);
        newUrl.pathname = "/gsc_live_data.json";
        newUrl.search = "";
        return await env.ASSETS.fetch(new Request(newUrl.toString(), { method: "GET" }));
      } catch(e) {
        return new Response(JSON.stringify({ error: e.message, stack: e.stack }), { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } });
      }
    }

    // API: GET /api/ga4-data (Trả về dữ liệu GA4 Live Analytics)
    if (url.pathname === "/api/ga4-data" && request.method === "GET") {
      try {
        const newUrl = new URL(request.url);
        newUrl.pathname = "/ga4_live_data.json";
        newUrl.search = "";
        return await env.ASSETS.fetch(new Request(newUrl.toString(), { method: "GET" }));
      } catch(e) {
        return new Response(JSON.stringify({ error: e.message, stack: e.stack }), { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } });
      }
    }

    // API: POST /api/ai/enhance-prompt (Viết lại prompt Tiếng Việt chuyên sâu cho mohinh3d.org)
    if (url.pathname === "/api/ai/enhance-prompt" && request.method === "POST") {
      try {
        const body = await request.json().catch(() => ({}));
        const rawIdea = (body.rawIdea || "").trim();
        const style = (body.style || "resin_print").trim();

        if (!rawIdea) {
          return new Response(
            JSON.stringify({ success: false, message: "Vui lòng nhập ý tưởng thô!" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const apiKey = env.GEMINI_API_KEY || GEMINI_API_KEY;
        const systemInstruction = `Bạn là chuyên gia thiết kế và prompt engineer cao cấp cho thương hiệu "mohinh3d.org" - xưởng công nghệ in 3D resin và chế tác mô hình 3D cao cấp.
Nhiệm vụ của bạn: Từ ý tưởng hoặc mô tả thô của người dùng, hãy tạo ra:
1. "promptVi": Câu prompt mô tả chi tiết hoàn chỉnh bằng TIẾNG VIỆT (khoảng 2-4 câu), nêu bật góc máy, ánh sáng studio, chất liệu in 3D resin hoặc sa bàn thu nhỏ, chi tiết sắc nét, phông nền sạch sẽ, độ thẩm mỹ chuyên nghiệp, sẵn sàng để người dùng xem và tinh chỉnh.
2. "promptEn": Câu prompt tối ưu bằng TIẾNG ANH chuyên dùng cho các model tạo ảnh AI (như Flux, Stable Diffusion, Midjourney), chứa các từ khóa đắt giá như: "highly detailed 3D resin printed scale model, miniature architectural tabletop, crisp edges, smooth surface finish, photorealistic, 8k resolution, soft ambient studio lighting, clean background, macro photography, octane render, masterpiece, sharp focus, no watermark".
Trả về kết quả DUY NHẤT dưới dạng JSON hợp lệ:
{
  "promptVi": "...",
  "promptEn": "..."
}`;

        const promptReq = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [
              {
                parts: [
                  { text: `${systemInstruction}\n\nÝ tưởng thô: "${rawIdea}"\nPhong cách mong muốn: "${style}"` }
                ]
              }
            ],
            generationConfig: {
              responseMimeType: "application/json",
              temperature: 0.7
            }
          })
        });

        if (!promptReq.ok) {
          const errText = await promptReq.text();
          return new Response(
            JSON.stringify({ success: false, message: "Lỗi gọi AI Gemini: " + errText }),
            { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const gData = await promptReq.json();
        const candidateText = gData?.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
        let parsed = {};
        try {
          parsed = JSON.parse(candidateText);
        } catch(e) {
          parsed = { promptVi: candidateText, promptEn: rawIdea };
        }

        return new Response(
          JSON.stringify({
            success: true,
            promptVi: parsed.promptVi || rawIdea,
            promptEn: parsed.promptEn || rawIdea
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

    // API: GET /api/ai/image-proxy (Proxy ảnh tránh CORS Canvas Taint khi render watermark)
    if (url.pathname === "/api/ai/image-proxy" && request.method === "GET") {
      try {
        const targetUrl = url.searchParams.get("url");
        if (!targetUrl) {
          return new Response("Missing url param", { status: 400, headers: corsHeaders });
        }
        const imgRes = await fetch(targetUrl);
        const contentType = imgRes.headers.get("content-type") || "image/jpeg";
        const imgBuffer = await imgRes.arrayBuffer();
        return new Response(imgBuffer, {
          status: 200,
          headers: {
            ...corsHeaders,
            "Content-Type": contentType,
            "Cache-Control": "public, max-age=86400"
          }
        });
      } catch(e) {
        return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders });
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

    // API: POST /api/notion/report-work (Báo cáo công việc đã làm -> Comment Notion Task + Cập nhật Task + Ghi Log Notion DB)
    if (url.pathname === "/api/notion/report-work" && request.method === "POST") {
      try {
        const body = await request.json();
        const {
          task_id,
          task_title,
          work_title,
          category,
          channel,
          performer,
          date,
          result_url,
          notes,
          update_status
        } = body;

        if (!task_id || !work_title) {
          return new Response(
            JSON.stringify({ ok: false, error: "Thiếu Task ID hoặc Nội dung công việc đã làm" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const effectivePerformer = performer || "Phạm Hoàng Tiến";
        const effectiveCategory = category || "Hệ thống";
        const effectiveChannel = channel || "Toàn hệ thống";
        const now = new Date();
        const dd = String(now.getDate()).padStart(2, '0');
        const mm = String(now.getMonth() + 1).padStart(2, '0');
        const yyyy = now.getFullYear();
        const hh = String(now.getHours()).padStart(2, '0');
        const min = String(now.getMinutes()).padStart(2, '0');
        const ss = String(now.getSeconds()).padStart(2, '0');
        const timeStr = `${dd}/${mm}/${yyyy} ${hh}:${min}:${ss}`;

        // 1. Gửi bình luận vào Notion Page của Task làm nhật ký thao tác
        const commentLines = [
          `[BÁO CÁO CÔNG VIỆC - ${timeStr}]`,
          `• Người thực hiện: ${effectivePerformer}`,
          `• Hạng mục: ${effectiveCategory} | Kênh: ${effectiveChannel}`,
          `• Nội dung công việc: ${work_title.trim()}`
        ];
        if (result_url && result_url.trim()) {
          commentLines.push(`• Link / Kết quả: ${result_url.trim()}`);
        }
        if (notes && notes.trim()) {
          commentLines.push(`• Ghi chú: ${notes.trim()}`);
        }
        if (update_status && update_status !== 'keep' && update_status !== 'Giữ nguyên') {
          commentLines.push(`• Cập nhật trạng thái: ${update_status}`);
        }
        const commentContent = commentLines.join('\n');

        let commentData = null;
        try {
          const commentRes = await fetch("https://api.notion.com/v1/comments", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Notion-Version": NOTION_API_VERSION,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              parent: { page_id: task_id },
              rich_text: [
                {
                  text: {
                    content: commentContent
                  }
                }
              ]
            })
          });
          commentData = await commentRes.json();
        } catch (cErr) {
          console.warn("Lỗi gửi comment Notion task:", cErr);
        }

        // 2. Cập nhật trạng thái Task trên Notion (nếu có yêu cầu)
        let taskUpdated = false;
        if (update_status && update_status !== 'keep' && update_status !== 'Giữ nguyên') {
          try {
            const patchRes = await fetch(`https://api.notion.com/v1/pages/${task_id}`, {
              method: "PATCH",
              headers: {
                "Authorization": `Bearer ${token}`,
                "Notion-Version": NOTION_API_VERSION,
                "Content-Type": "application/json"
              },
              body: JSON.stringify({
                properties: {
                  "Trạng thái": {
                    status: {
                      name: update_status
                    }
                  }
                }
              })
            });
            if (patchRes.ok) {
              taskUpdated = true;
            }
          } catch (pErr) {
            console.warn("Không thể cập nhật trạng thái Task Notion:", pErr);
          }
        }

        // 3. Ghi nhận vào Notion Database: NHẬT KÝ THAO TÁC MARKETING SONG ANH
        const ACTIVITY_LOG_DB_ID = "3c24b5e7-3d90-81b4-b505-f85f9c9bfcae";
        const cleanWorkTitle = work_title.trim();
        const actionTitle = `[${effectiveCategory}] ${effectiveChannel}: ${cleanWorkTitle}`;
        let notesText = `- Task: ${task_title || task_id}`;
        if (result_url && result_url.trim()) notesText += `\n- Link: ${result_url.trim()}`;
        if (notes && notes.trim()) notesText += `\n- Ghi chú: ${notes.trim()}`;

        let logData = null;
        try {
          const logRes = await fetch("https://api.notion.com/v1/pages", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Notion-Version": NOTION_API_VERSION,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              parent: { database_id: ACTIVITY_LOG_DB_ID },
              properties: {
                "Hành Động": {
                  title: [{ text: { content: actionTitle.substring(0, 1900) } }]
                },
                "Người Thực Hiện": {
                  rich_text: [{ text: { content: effectivePerformer } }]
                },
                "Thời Gian": {
                  rich_text: [{ text: { content: timeStr } }]
                },
                "Trạng Thái": {
                  select: { name: "Hoàn thành" }
                },
                "Mô Tả Ngắn": {
                  rich_text: [{ text: { content: notesText.substring(0, 1900) } }]
                },
                "ID Log": {
                  number: Math.floor(Date.now() / 1000)
                }
              }
            })
          });
          logData = await logRes.json();
        } catch (lErr) {
          console.warn("Không thể ghi log Notion DB:", lErr);
        }

        return new Response(
          JSON.stringify({
            ok: true,
            message: "Đã lưu báo cáo công việc vào comment của task trên Notion & đồng bộ nhật ký thành công!",
            comment: commentData,
            activity_log: logData,
            task_updated: taskUpdated,
            created_time: timeStr,
            action_title: actionTitle,
            notes_text: notesText
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

    // API: POST /api/notion/report-recomment (Báo cáo Re-comment / Seeding FB -> Comment vào Bài Post Notion + Cập nhật Ngày Re-cmt + Comment Task Cha + Log DB)
    if (url.pathname === "/api/notion/report-recomment" && request.method === "POST") {
      try {
        const body = await request.json();
        const {
          target_type, // "wall" or "group"
          channel,
          post_id,
          post_title,
          post_url,
          group_name,
          comment_content,
          date,
          task_id,
          performer,
          update_notion_date,
          current_recomment_count
        } = body;

        if (!post_url && !comment_content) {
          return new Response(
            JSON.stringify({ ok: false, error: "Thiếu Link bài viết Facebook hoặc Nội dung bình luận" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const isGroup = target_type === "group";
        const GROUP_POSTS_HISTORY_DB_ID = "3c24b5e7-3d90-81df-aa41-d2f5c355f32f";
        const POSTS_HUB_DB_ID = "3de4b5e7-3d90-81d4-aa43-f800ae1870c7";

        const effectivePerformer = performer || "Phạm Hoàng Tiến";
        const effectiveChannel = channel || "Fanpage Mô hình kiến trúc Song Anh";
        const effectivePostTitle = (post_title && post_title.trim()) || (isGroup ? "Bài viết Group Facebook" : "Bài viết Facebook");
        const effectivePostUrl = (post_url && post_url.trim()) || "";
        const effectiveComment = (comment_content && comment_content.trim()) || "";
        
        const now = new Date();
        const dd = String(now.getDate()).padStart(2, '0');
        const mm = String(now.getMonth() + 1).padStart(2, '0');
        const yyyy = now.getFullYear();
        const hh = String(now.getHours()).padStart(2, '0');
        const min = String(now.getMinutes()).padStart(2, '0');
        const ss = String(now.getSeconds()).padStart(2, '0');
        const timeStr = `${dd}/${mm}/${yyyy} ${hh}:${min}:${ss}`;
        const todayIso = `${yyyy}-${mm}-${dd}`;

        let postCommentData = null;
        let postUpdated = false;
        let targetPageId = post_id;

        if (isGroup) {
          // ==================== CƠ CHẾ GROUP FACEBOOK ====================
          // Database: LỊCH SỬ ĐĂNG BÀI & RE-COMMENT GROUP (3c24b5e7-3d90-81df-aa41-d2f5c355f32f)
          if (targetPageId) {
            // 1a. Lưu comment vào chính trang bài viết Group trên Notion
            try {
              const postCmtRes = await fetch("https://api.notion.com/v1/comments", {
                method: "POST",
                headers: {
                  "Authorization": `Bearer ${token}`,
                  "Notion-Version": NOTION_API_VERSION,
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({
                  parent: { page_id: targetPageId },
                  rich_text: [
                    {
                      text: {
                        content: `💬 [BÁO CÁO RE-COMMENT GROUP FB - ${timeStr}]\n• Người thực hiện: ${effectivePerformer}\n• Tài khoản: ${effectiveChannel}\n• Group: ${group_name || 'Group Facebook'}\n• Link bài FB: ${effectivePostUrl}\n• Nội dung Re-comment:\n${effectiveComment}`
                      }
                    }
                  ]
                })
              });
              postCommentData = await postCmtRes.json();
            } catch (cErr) {
              console.warn("Lỗi lưu comment vào bài group Notion:", cErr);
            }

            // 1b. Cập nhật ngày Re-comment & tăng lượt Re-comment trên Notion page của bài viết Group
            if (update_notion_date !== false) {
              try {
                const groupPropPatch = {
                  "Ngày Re-comment": {
                    date: { start: todayIso }
                  },
                  "Trạng Thái": {
                    select: { name: "Đã đăng công khai" }
                  }
                };
                if (typeof current_recomment_count === 'number') {
                  groupPropPatch["Lượt Re-Comment"] = {
                    number: current_recomment_count + 1
                  };
                }

                const patchRes = await fetch(`https://api.notion.com/v1/pages/${targetPageId}`, {
                  method: "PATCH",
                  headers: {
                    "Authorization": `Bearer ${token}`,
                    "Notion-Version": NOTION_API_VERSION,
                    "Content-Type": "application/json"
                  },
                  body: JSON.stringify({ properties: groupPropPatch })
                });
                if (patchRes.ok) {
                  postUpdated = true;
                }
              } catch (pErr) {
                console.warn("Lỗi cập nhật ngày Re-comment bài group:", pErr);
              }
            }
          } else {
            // 2. Tạo bản ghi bài viết mới trong Bảng Lịch Sử Đăng Bài & Re-comment Group
            try {
              const newGroupProps = {
                "Tên Bài Đăng": {
                  title: [{ text: { content: effectivePostTitle } }]
                },
                "Tài Khoản Đăng": {
                  select: { name: effectiveChannel }
                },
                "Link Bài Đăng Thực Tế": {
                  url: effectivePostUrl || null
                },
                "Ngày Đăng": {
                  date: { start: todayIso }
                },
                "Ngày Re-comment": {
                  date: { start: todayIso }
                },
                "Trạng Thái": {
                  select: { name: "Đã đăng công khai" }
                },
                "Lượt Re-Comment": {
                  number: 1
                }
              };

              const newGroupRes = await fetch("https://api.notion.com/v1/pages", {
                method: "POST",
                headers: {
                  "Authorization": `Bearer ${token}`,
                  "Notion-Version": NOTION_API_VERSION,
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({
                  parent: { database_id: GROUP_POSTS_HISTORY_DB_ID },
                  properties: newGroupProps
                })
              });
              if (newGroupRes.ok) {
                const newGroupData = await newGroupRes.json();
                targetPageId = newGroupData.id;
                postUpdated = true;

                // Thêm comment vào trang bài Group vừa tạo
                await fetch("https://api.notion.com/v1/comments", {
                  method: "POST",
                  headers: {
                    "Authorization": `Bearer ${token}`,
                    "Notion-Version": NOTION_API_VERSION,
                    "Content-Type": "application/json"
                  },
                  body: JSON.stringify({
                    parent: { page_id: targetPageId },
                    rich_text: [
                      {
                        text: {
                          content: `💬 [BÁO CÁO RE-COMMENT GROUP FB - ${timeStr}]\n• Người thực hiện: ${effectivePerformer}\n• Tài khoản: ${effectiveChannel}\n• Group: ${group_name || 'Group Facebook'}\n• Link bài FB: ${effectivePostUrl}\n• Nội dung Re-comment:\n${effectiveComment}`
                        }
                      }
                    ]
                  })
                });
              }
            } catch (ngErr) {
              console.warn("Lỗi tạo bài viết mới trong Bảng Group Posts:", ngErr);
            }
          }
        } else {
          // ==================== CƠ CHẾ TƯỜNG NHÀ (FANPAGE / PROFILE) ====================
          // Database: BẢNG NHẬT KÝ BÀI ĐĂNG (POSTS HUB) (3de4b5e7-3d90-81d4-aa43-f800ae1870c7)
          if (targetPageId) {
            // 1a. Lưu comment vào chính trang bài viết trên Notion
            try {
              const postCmtRes = await fetch("https://api.notion.com/v1/comments", {
                method: "POST",
                headers: {
                  "Authorization": `Bearer ${token}`,
                  "Notion-Version": NOTION_API_VERSION,
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({
                  parent: { page_id: targetPageId },
                  rich_text: [
                    {
                      text: {
                        content: `💬 [BÁO CÁO RE-COMMENT FB - ${timeStr}]\n• Người thực hiện: ${effectivePerformer}\n• Kênh: ${effectiveChannel}\n• Link bài FB: ${effectivePostUrl}\n• Nội dung Re-comment:\n${effectiveComment}`
                      }
                    }
                  ]
                })
              });
              postCommentData = await postCmtRes.json();
            } catch (cErr) {
              console.warn("Lỗi lưu comment vào bài post Notion:", cErr);
            }

            // 1b. Cập nhật ngày Re-comment trên Notion page của bài viết
            if (update_notion_date !== false) {
              try {
                const propPatch = {};
                const chLower = effectiveChannel.toLowerCase();
                if (chLower.includes("fanpage")) {
                  propPatch["Ngày Re-comment Fanpage (Mô hình kiến trúc Song Anh)"] = {
                    date: { start: todayIso }
                  };
                } else if (chLower.includes("profile")) {
                  propPatch["Ngày Re-comment FB Profile Song Anh"] = {
                    date: { start: todayIso }
                  };
                } else {
                  propPatch["Ngày Re-comment"] = {
                    date: { start: todayIso }
                  };
                }

                const patchRes = await fetch(`https://api.notion.com/v1/pages/${targetPageId}`, {
                  method: "PATCH",
                  headers: {
                    "Authorization": `Bearer ${token}`,
                    "Notion-Version": NOTION_API_VERSION,
                    "Content-Type": "application/json"
                  },
                  body: JSON.stringify({ properties: propPatch })
                });
                if (patchRes.ok) {
                  postUpdated = true;
                }
              } catch (pErr) {
                console.warn("Lỗi cập nhật ngày Re-comment bài post:", pErr);
              }
            }
          } else {
            // 2. Nếu là bài viết mới (chưa có post_id, chỉ có Link FB và Tiêu đề)
            try {
              const newProps = {
                "Tiêu đề bài đăng": {
                  title: [{ text: { content: effectivePostTitle } }]
                },
                "Link bài viết": {
                  url: effectivePostUrl || null
                },
                "Ngày đăng": {
                  date: { start: todayIso }
                },
                "Trạng thái": {
                  select: { name: "Đã đăng" }
                },
                "Nội dung bài đăng": {
                  rich_text: [{ text: { content: effectiveComment.substring(0, 1900) } }]
                }
              };
              if (task_id) {
                newProps["Liên kết Công việc"] = {
                  relation: [{ id: task_id }]
                };
              }

              const newPostRes = await fetch("https://api.notion.com/v1/pages", {
                method: "POST",
                headers: {
                  "Authorization": `Bearer ${token}`,
                  "Notion-Version": NOTION_API_VERSION,
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({
                  parent: { database_id: POSTS_HUB_DB_ID },
                  properties: newProps
                })
              });
              if (newPostRes.ok) {
                const newPostData = await newPostRes.json();
                targetPageId = newPostData.id;
                postUpdated = true;

                // Thêm comment vào trang bài viết vừa tạo
                await fetch("https://api.notion.com/v1/comments", {
                  method: "POST",
                  headers: {
                    "Authorization": `Bearer ${token}`,
                    "Notion-Version": NOTION_API_VERSION,
                    "Content-Type": "application/json"
                  },
                  body: JSON.stringify({
                    parent: { page_id: targetPageId },
                    rich_text: [
                      {
                        text: {
                          content: `💬 [BÁO CÁO RE-COMMENT FB - ${timeStr}]\n• Người thực hiện: ${effectivePerformer}\n• Kênh: ${effectiveChannel}\n• Link bài FB: ${effectivePostUrl}\n• Nội dung Re-comment:\n${effectiveComment}`
                        }
                      }
                    ]
                  })
                });
              }
            } catch (npErr) {
              console.warn("Lỗi tạo bài viết mới trong Posts Hub:", npErr);
            }
          }
        }

        // 3. Gửi comment tóm tắt vào Task cha (ví dụ [Re-Cmt FB] Fanpage... hoặc [Re-cmt FB Group]...)
        let taskCommentData = null;
        let effectiveTaskId = task_id;
        if (!effectiveTaskId) {
          if (isGroup) {
            effectiveTaskId = effectiveChannel.toLowerCase().includes("fanpage")
              ? "2d94b5e7-3d90-8011-87ac-dc794fe4c579"
              : "4fd4b5e7-3d90-823c-8771-018e657ecb8f";
          } else {
            effectiveTaskId = effectiveChannel.toLowerCase().includes("fanpage")
              ? "25e4b5e7-3d90-80e4-aa00-de02bd93c241"
              : "4fd4b5e7-3d90-823c-8771-018e657ecb8f";
          }
        }

        if (effectiveTaskId) {
          try {
            const taskCmtRes = await fetch("https://api.notion.com/v1/comments", {
              method: "POST",
              headers: {
                "Authorization": `Bearer ${token}`,
                "Notion-Version": NOTION_API_VERSION,
                "Content-Type": "application/json"
              },
              body: JSON.stringify({
                parent: { page_id: effectiveTaskId },
                rich_text: [
                  {
                    text: {
                      content: `💬 [BÁO CÁO RE-COMMENT FB${isGroup ? ' GROUP' : ''} - ${timeStr}]\n• Người thực hiện: ${effectivePerformer}\n• Kênh / Tài khoản: ${effectiveChannel}\n• Bài viết: ${effectivePostTitle}${isGroup && group_name ? `\n• Group: ${group_name}` : ''}\n• Link bài FB: ${effectivePostUrl}\n• Nội dung Re-comment:\n${effectiveComment}`
                    }
                  }
                ]
              })
            });
            taskCommentData = await taskCmtRes.json();
          } catch (tcErr) {
            console.warn("Lỗi comment vào Task cha:", tcErr);
          }

          // 3b. Tự động cập nhật +1 Đã thực hiện cho Task trên Notion để báo cáo KPI tuần
          try {
            const cleanTaskId = effectiveTaskId.trim();
            const taskGetRes = await fetch(`https://api.notion.com/v1/pages/${cleanTaskId}`, {
              headers: {
                "Authorization": `Bearer ${token}`,
                "Notion-Version": NOTION_API_VERSION
              }
            });
            if (taskGetRes.ok) {
              const taskData = await taskGetRes.json();
              const curDone = (taskData.properties && taskData.properties["Đã thực hiện"] && typeof taskData.properties["Đã thực hiện"].number === "number")
                ? taskData.properties["Đã thực hiện"].number
                : 0;
              await fetch(`https://api.notion.com/v1/pages/${cleanTaskId}`, {
                method: "PATCH",
                headers: {
                  "Authorization": `Bearer ${token}`,
                  "Notion-Version": NOTION_API_VERSION,
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({
                  properties: {
                    "Đã thực hiện": { number: curDone + 1 }
                  }
                })
              });

              // Cập nhật tự động lên Task Cha (mục gốc) nếu có
              const parentRels = (taskData.properties && taskData.properties["mục gốc"] && taskData.properties["mục gốc"].relation) || [];
              for (const pRel of parentRels) {
                if (pRel && pRel.id) {
                  try {
                    const pGet = await fetch(`https://api.notion.com/v1/pages/${pRel.id}`, {
                      headers: { "Authorization": `Bearer ${token}`, "Notion-Version": NOTION_API_VERSION }
                    });
                    if (pGet.ok) {
                      const pData = await pGet.json();
                      const pDone = (pData.properties && pData.properties["Đã thực hiện"] && typeof pData.properties["Đã thực hiện"].number === "number")
                        ? pData.properties["Đã thực hiện"].number
                        : 0;
                      await fetch(`https://api.notion.com/v1/pages/${pRel.id}`, {
                        method: "PATCH",
                        headers: { "Authorization": `Bearer ${token}`, "Notion-Version": NOTION_API_VERSION, "Content-Type": "application/json" },
                        body: JSON.stringify({ properties: { "Đã thực hiện": { number: pDone + 1 } } })
                      });
                    }
                  } catch (pe) {
                    console.warn("Lỗi cập nhật task cha trong report-recomment:", pe);
                  }
                }
              }
            }
          } catch (tPatchErr) {
            console.warn("Lỗi cập nhật Đã thực hiện cho Task trên Notion:", tPatchErr);
          }
        }

        // 4. Ghi nhận vào Notion Database: NHẬT KÝ THAO TÁC MARKETING SONG ANH
        const ACTIVITY_LOG_DB_ID = "3c24b5e7-3d90-81b4-b505-f85f9c9bfcae";
        const shortChannel = effectiveChannel.replace(/Mô hình kiến trúc\s*/i, '').replace(/Facebook\s*/i, '').trim();
        const actionTitle = `[Re-Cmt FB${isGroup ? ' Group' : ''}] ${shortChannel}: ${effectivePostTitle.substring(0, 100)}`;
        let notesText = `- Task: [Re-Cmt FB${isGroup ? ' Group' : ''}] ${effectiveChannel}\n- Post: ${effectivePostTitle}`;
        if (isGroup && group_name) notesText += `\n- Group: ${group_name}`;
        if (effectivePostUrl) notesText += `\n- Link: ${effectivePostUrl}`;
        if (effectiveComment) notesText += `\n- Nội dung Re-comment: ${effectiveComment.substring(0, 250)}...`;

        let logData = null;
        try {
          const logRes = await fetch("https://api.notion.com/v1/pages", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Notion-Version": NOTION_API_VERSION,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              parent: { database_id: ACTIVITY_LOG_DB_ID },
              properties: {
                "Hành Động": {
                  title: [{ text: { content: actionTitle.substring(0, 1900) } }]
                },
                "Người Thực Hiện": {
                  rich_text: [{ text: { content: effectivePerformer } }]
                },
                "Thời Gian": {
                  rich_text: [{ text: { content: timeStr } }]
                },
                "Trạng Thái": {
                  select: { name: "Hoàn thành" }
                },
                "Mô Tả Ngắn": {
                  rich_text: [{ text: { content: notesText.substring(0, 1900) } }]
                },
                "ID Log": {
                  number: Math.floor(Date.now() / 1000)
                }
              }
            })
          });
          logData = await logRes.json();
        } catch (lErr) {
          console.warn("Không thể ghi log Notion DB:", lErr);
        }

        return new Response(
          JSON.stringify({
            ok: true,
            message: "Đã lưu Re-comment vào bài post Notion, task cha và nhật ký thành công!",
            post_comment: postCommentData,
            task_comment: taskCommentData,
            post_updated: postUpdated,
            target_page_id: targetPageId,
            activity_log: logData,
            created_time: timeStr,
            action_title: actionTitle,
            notes_text: notesText
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

    // API: GET / POST /api/notion/sync-tasks (Đồng bộ trực tiếp BẢNG DANH SÁCH CÔNG VIỆC SONG ANH từ Notion)
    if (url.pathname === "/api/notion/sync-tasks" && (request.method === "GET" || request.method === "POST")) {
      try {
        const tasks = [];
        let hasMore = true;
        let startCursor = undefined;
        const TASKS_DB_ID = "19a4b5e73d9080f4a51ef769967547a5";

        while (hasMore) {
          const bodyPayload = { page_size: 100 };
          if (startCursor) bodyPayload.start_cursor = startCursor;

          const res = await fetch(`https://api.notion.com/v1/databases/${TASKS_DB_ID}/query`, {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Notion-Version": NOTION_API_VERSION,
              "Content-Type": "application/json",
            },
            body: JSON.stringify(bodyPayload)
          });

          if (!res.ok) {
            const errText = await res.text();
            throw new Error(`Notion error ${res.status}: ${errText}`);
          }

          const pageData = await res.json();
          const results = pageData.results || [];

          for (const p of results) {
            const props = p.properties || {};
            const pageId = p.id;

            // Title
            let title = "";
            if (props["Tên công việc"] && props["Tên công việc"].title) {
              title = props["Tên công việc"].title.map(t => t.plain_text || "").join("").trim();
            }
            if (!title) {
              for (const k in props) {
                if (props[k] && props[k].type === "title") {
                  title = (props[k].title || []).map(t => t.plain_text || "").join("").trim();
                  break;
                }
              }
            }

            const statusObj = props["Trạng thái"] && props["Trạng thái"].status;
            const statusName = statusObj ? (statusObj.name || "Duy trì") : "Duy trì";

            const doneCount = (props["Đã thực hiện"] && typeof props["Đã thực hiện"].number === "number") ? props["Đã thực hiện"].number : 0;
            const kpiVal = (props["KPI"] && typeof props["KPI"].number === "number") ? props["KPI"].number : 0;

            const repeatList = (props["Lặp lại"] && props["Lặp lại"].multi_select) ? props["Lặp lại"].multi_select.map(i => i.name) : [];
            const slotList = (props["Buổi"] && props["Buổi"].multi_select) ? props["Buổi"].multi_select.map(i => i.name) : [];

            // Ghi chú & Mô tả
            let note = "";
            if (props["Ghi chú"] && props["Ghi chú"].rich_text) {
              note = props["Ghi chú"].rich_text.map(t => t.plain_text || "").join("").trim();
            }
            let description = "";
            if (props["Mô tả công việc"] && props["Mô tả công việc"].rich_text) {
              description = props["Mô tả công việc"].rich_text.map(t => t.plain_text || "").join("").trim();
            }

            // Remind date
            const remindObj = props["Nhắc hẹn"] && props["Nhắc hẹn"].date;
            const remindDate = remindObj ? (remindObj.start || "") : "";

            // Relations
            const parentRel = (props["mục gốc"] && props["mục gốc"].relation) || [];
            const parentId = parentRel.length > 0 ? parentRel[0].id : null;
            const subtaskRel = (props["mục con"] && props["mục con"].relation) || [];
            const subtaskIds = subtaskRel.map(r => r.id);

            tasks.push({
              id: pageId,
              title: title || "(Không có tiêu đề)",
              status: statusName,
              done_count: doneCount,
              kpi: kpiVal,
              repeat: repeatList,
              slot: slotList,
              note: note,
              description: description,
              remind_date: remindDate,
              parent_id: parentId,
              subtask_ids: subtaskIds,
              notion_url: p.url || `https://notion.so/${pageId.replace(/-/g, '')}`,
              last_edited_time: p.last_edited_time
            });
          }

          hasMore = pageData.has_more || false;
          startCursor = pageData.next_cursor || undefined;
        }

        const channelNameById = {
          "39d4b5e7-3d90-8145-8ff2-e255190d0e6a": "Fanpage Mô hình kiến trúc Song Anh",
          "3aa4b5e7-3d90-80f2-b98c-c03c4e6f384c": "Fanpage Architectural Model Org",
          "3aa4b5e7-3d90-80fa-916f-f05294adbd65": "Fanpage Làm mô hình Song Anh",
          "3af4b5e7-3d90-81da-b761-e2a06944238f": "Fanpage Vật liệu mô hình",
          "39d4b5e7-3d90-8131-9be4-c0ee9fea8fb8": "Profile Song Anh",
          "3af4b5e7-3d90-8142-a4d6-fcb9ad5ce344": "Profile Tiến RS",
          "3af4b5e7-3d90-812e-b863-cefd7b4f6727": "Profile Mô hình Song Anh",
          "39d4b5e7-3d90-81ff-9360-f252aebbfc18": "Zalo Steven (0981169200)",
          "39d4b5e7-3d90-8132-a289-c10337cc85a8": "Zalo CSKH (0988080440)",
          "39d4b5e7-3d90-81fd-9671-cd411da3b218": "Zalo Sale (0376415131)",
          "39d4b5e7-3d90-8103-a730-fdcf1280acc3": "Zalo CSKH 0386 989 087",
          "39d4b5e7-3d90-81d6-bc82-c9d5644a13ac": "GBP Sa bàn kiến trúc Song Anh",
          "39d4b5e7-3d90-8104-88f1-df54c99bc328": "GBP Dịch vụ làm mô hình kiến trúc Song Anh",
          "39d4b5e7-3d90-81b8-8e18-e5ef67a3683e": "GBP Mô hình kiến trúc Song Anh",
          "3d64b5e7-3d90-8126-bc9c-c16c36b14b39": "Website mohinhkientruc.org",
          "3d64b5e7-3d90-8136-ab59-cdd9684764bb": "Website architecturalmodel.org",
          "3e04b5e7-3d90-819e-adf9-e84cc762e991": "Group Facebook"
        };

        const POSTS_DB_ID = env.MARKETING_POSTS_DB_ID || "3de4b5e7-3d90-81d4-aa43-f800ae1870c7";
        const posts = [];
        let pHasMore = true;
        let pStartCursor = undefined;

        while (pHasMore) {
          const pPayload = { page_size: 100 };
          if (pStartCursor) pPayload.start_cursor = pStartCursor;

          const pRes = await fetch(`https://api.notion.com/v1/databases/${POSTS_DB_ID}/query`, {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Notion-Version": NOTION_API_VERSION,
              "Content-Type": "application/json",
            },
            body: JSON.stringify(pPayload)
          });

          if (pRes.ok) {
            const pData = await pRes.json();
            for (const p of (pData.results || [])) {
              const pProps = p.properties || {};
              let pTitle = "";
              if (pProps["Tiêu đề bài đăng"] && pProps["Tiêu đề bài đăng"].title) {
                pTitle = pProps["Tiêu đề bài đăng"].title.map(t => t.plain_text || "").join("").trim();
              }
              const pDateObj = pProps["Ngày đăng"] && pProps["Ngày đăng"].date;
              const pDateStart = pDateObj ? (pDateObj.start || "") : "";
              let dateVn = pDateStart;
              if (pDateStart && pDateStart.includes("-")) {
                const parts = pDateStart.split("T")[0].split("-");
                if (parts.length === 3) dateVn = `${parts[2]}/${parts[1]}/${parts[0]}`;
              }

              const pChannelRels = (pProps["Kênh xuất bản"] && pProps["Kênh xuất bản"].relation) || [];
              const chId = pChannelRels.length > 0 ? pChannelRels[0].id : "";
              const chName = channelNameById[chId] || "";

              const pTaskRels = (pProps["Liên kết Công việc"] && pProps["Liên kết Công việc"].relation) || [];
              const tId = pTaskRels.length > 0 ? pTaskRels[0].id : "";

              const pUrl = (pProps["Link bài viết"] && pProps["Link bài viết"].url) || "";
              let caption = "";
              if (pProps["Nội dung bài đăng"] && pProps["Nội dung bài đăng"].rich_text) {
                caption = pProps["Nội dung bài đăng"].rich_text.map(t => t.plain_text || "").join("").trim();
              }
              const status = (pProps["Trạng thái"] && pProps["Trạng thái"].select && pProps["Trạng thái"].select.name) || "Đã đăng";

              posts.push({
                id: `notion-post-${p.id}`,
                notion_page_id: p.id,
                title: pTitle,
                channel: chName,
                date: dateVn || pDateStart,
                post_date: dateVn || pDateStart,
                post_url: pUrl,
                content_snippet: caption || pTitle,
                status: status,
                task_id: tId
              });
            }
            pHasMore = pData.has_more || false;
            pStartCursor = pData.next_cursor || undefined;
          } else {
            pHasMore = false;
          }
        }

        return new Response(
          JSON.stringify({ 
            ok: true, 
            success: true, 
            count: tasks.length, 
            tasks, 
            posts_count: posts.length,
            posts, 
            synced_at: new Date().toISOString() 
          }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, success: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // API: POST /api/notion/update-task
    if (url.pathname === "/api/notion/update-task" && request.method === "POST") {
      try {
        const body = await request.json();
        const { page_id, title, status, done_count, note, description, remind_date, repeat_days, role_id, category_id, channel_id, field_id, linhvuc_id } = body;

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
        const targetLinhVucId = field_id || linhvuc_id;
        if (targetLinhVucId !== undefined) {
          properties["Lĩnh vực"] = { relation: targetLinhVucId ? [{ id: targetLinhVucId }] : [] };
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

    // API: POST /api/notion/create-task (Tạo mới Task trên Notion BẢNG DANH SÁCH CÔNG VIỆC SONG ANH)
    if (url.pathname === "/api/notion/create-task" && request.method === "POST") {
      try {
        const body = await request.json();
        const { title, status, kpi, done_count, note, description, remind_date, role_id, category_id, channel_id, field_id, linhvuc_id } = body;

        if (!title || String(title).trim() === "") {
          return new Response(
            JSON.stringify({ ok: false, error: "Tiêu đề công việc không được để trống" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const TASKS_DB_ID = "19a4b5e7-3d90-80f4-a51e-f769967547a5";
        const properties = {
          "Tên công việc": { title: [{ text: { content: String(title).trim() } }] },
          "Trạng thái": { status: { name: status || "Chưa lên lịch" } }
        };

        if (kpi !== undefined && kpi !== null && kpi !== "") {
          properties["KPI"] = { number: parseInt(kpi) || 0 };
        }
        if (done_count !== undefined && done_count !== null && done_count !== "") {
          properties["Đã thực hiện"] = { number: parseInt(done_count) || 0 };
        }
        if (note && String(note).trim() !== "") {
          properties["Ghi chú"] = { rich_text: [{ text: { content: String(note).trim() } }] };
        }
        if (description && String(description).trim() !== "") {
          properties["Mô tả công việc"] = { rich_text: [{ text: { content: String(description).trim() } }] };
        }
        if (remind_date && String(remind_date).trim() !== "") {
          properties["Nhắc hẹn"] = { date: { start: String(remind_date).trim() } };
        }

        // Vai trò mặc định: Marketing (19d4b5e7-3d90-8026-954c-f3aa288dfe14)
        const targetRoleId = role_id || "19d4b5e7-3d90-8026-954c-f3aa288dfe14";
        if (targetRoleId) {
          properties["Vai trò"] = { relation: [{ id: targetRoleId }] };
        }

        if (category_id && String(category_id).trim() !== "") {
          properties["Hạng mục"] = { relation: [{ id: String(category_id).trim() }] };
        }

        if (channel_id && String(channel_id).trim() !== "") {
          properties["Kênh"] = { relation: [{ id: String(channel_id).trim() }] };
        }

        // Lĩnh vực mặc định: Mô Hình (19a4b5e7-3d90-8022-9844-d93fd68a0812)
        const targetLinhvucId = field_id || linhvuc_id || "19a4b5e7-3d90-8022-9844-d93fd68a0812";
        if (targetLinhvucId) {
          properties["Lĩnh vực"] = { relation: [{ id: targetLinhvucId }] };
        }

        let notionRes = await fetch("https://api.notion.com/v1/pages", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            parent: { database_id: TASKS_DB_ID },
            properties: properties
          })
        });

        let data = await notionRes.json();
        // Fallback retry nếu relation Kênh cần đổi thành Kênh Social hoặc bỏ relation nếu lỗi page not found
        if (!notionRes.ok && data && data.message) {
          let shouldRetry = false;
          if (data.message.includes("Kênh") || data.message.includes("channel")) {
            delete properties["Kênh"];
            if (channel_id && String(channel_id).trim() !== "") {
              properties["Kênh Social"] = { relation: [{ id: String(channel_id).trim() }] };
            }
            shouldRetry = true;
          } else if (data.message.includes("Vai trò") || data.message.includes("Lĩnh vực")) {
            delete properties["Vai trò"];
            delete properties["Lĩnh vực"];
            shouldRetry = true;
          }
          if (shouldRetry) {
            notionRes = await fetch("https://api.notion.com/v1/pages", {
              method: "POST",
              headers: {
                "Authorization": `Bearer ${token}`,
                "Notion-Version": NOTION_API_VERSION,
                "Content-Type": "application/json"
              },
              body: JSON.stringify({
                parent: { database_id: TASKS_DB_ID },
                properties: properties
              })
            });
            data = await notionRes.json();
          }
        }

        if (!notionRes.ok) {
          return new Response(
            JSON.stringify({ ok: false, error: data }),
            { status: notionRes.status, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        return new Response(
          JSON.stringify({ ok: true, task: data, page_id: data.id }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // API: POST /api/notion/delete-task (Lưu trữ / Xóa Task khỏi Notion)
    if (url.pathname === "/api/notion/delete-task" && request.method === "POST") {
      try {
        const body = await request.json();
        const { page_id } = body;

        if (!page_id) {
          return new Response(
            JSON.stringify({ ok: false, error: "Thiếu page_id cần xóa" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const notionResponse = await fetch(`https://api.notion.com/v1/pages/${page_id}`, {
          method: "PATCH",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ archived: true })
        });

        const data = await notionResponse.json();
        if (!notionResponse.ok) {
          return new Response(
            JSON.stringify({ ok: false, error: data }),
            { status: notionResponse.status, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        return new Response(
          JSON.stringify({ ok: true, deleted: true, page_id }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // =========================================================================
    // 🌐 NOTION API: SOCIAL CHANNELS 2-WAY SYNC CONTROLLER
    // =========================================================================
    const NOTION_SOCIAL_DB_PRIMARY = "19d4b5e7-3d90-8043-a0d6-d3627fd6c8df";
    const NOTION_SOCIAL_DB_FALLBACK = "39d4b5e7-3d90-8170-af7c-efd31f1d056b";

    function getPlatformMeta(platform) {
      const p = String(platform || "").toLowerCase();
      if (p.includes("facebook") || p.includes("fb")) return { icon: "fa-brands fa-facebook text-blue-600", bg: "bg-blue-100 text-blue-800 border-blue-200", category: "facebook" };
      if (p.includes("google") || p.includes("gbp") || p.includes("map")) return { icon: "fa-brands fa-google text-red-500", bg: "bg-red-100 text-red-800 border-red-200", category: "gbp" };
      if (p.includes("pinterest")) return { icon: "fa-brands fa-pinterest text-rose-600", bg: "bg-rose-100 text-rose-800 border-rose-200", category: "pinterest" };
      if (p.includes("youtube")) return { icon: "fa-brands fa-youtube text-red-600", bg: "bg-red-100 text-red-800 border-red-200", category: "youtube" };
      if (p.includes("tiktok")) return { icon: "fa-brands fa-tiktok text-slate-900", bg: "bg-slate-100 text-slate-900 border-slate-300", category: "tiktok" };
      if (p.includes("twitter") || p === "x") return { icon: "fa-brands fa-x-twitter text-slate-900", bg: "bg-slate-100 text-slate-900 border-slate-300", category: "x" };
      if (p.includes("zalo")) return { icon: "fa-solid fa-comment-dots text-sky-600", bg: "bg-sky-100 text-sky-800 border-sky-200", category: "zalo" };
      if (p.includes("website") || p.includes("web") || p.includes("site")) return { icon: "fa-solid fa-globe text-emerald-600", bg: "bg-emerald-100 text-emerald-800 border-emerald-200", category: "website" };
      return { icon: "fa-solid fa-share-nodes text-indigo-600", bg: "bg-indigo-100 text-indigo-800 border-indigo-200", category: "other" };
    }

    const DOMAIN_REL_MAP = {
      "mo-hinh": "19a4b5e7-3d90-8022-9844-d93fd68a0812",
      "tmdt": "1ab4b5e7-3d90-8054-af11-d969b565692b",
      "golf": "19a4b5e7-3d90-8057-8150-c9d261b49484",
      "khac": "1a44b5e7-3d90-80b5-a67b-d52bfeac2ccd"
    };

    // 1. GET /api/notion/get-social-channels
    if (url.pathname === "/api/notion/get-social-channels" && request.method === "GET") {
      try {
        const token = env.NOTION_TOKEN || NOTION_API_KEY;
        let targetDb = NOTION_SOCIAL_DB_PRIMARY;
        let res = await fetch(`https://api.notion.com/v1/databases/${targetDb}/query`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ page_size: 100 })
        });

        if (res.status === 404) {
          targetDb = NOTION_SOCIAL_DB_FALLBACK;
          res = await fetch(`https://api.notion.com/v1/databases/${targetDb}/query`, {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Notion-Version": NOTION_API_VERSION,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({ page_size: 100 })
          });
        }

        if (!res.ok) {
          const errData = await res.json();
          return new Response(
            JSON.stringify({ ok: false, error: errData.message || "Lỗi truy vấn Notion", source_db: targetDb }),
            { status: res.status, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const data = await res.json();
        const pages = data.results || [];
        const channels = pages.map(p => {
          const props = p.properties || {};
          const nameArr = props["Tên"]?.title || props["Tên kênh"]?.title || props["Name"]?.title || [];
          const name = nameArr.map(x => x.plain_text || "").join("").trim();
          const direct_url = props["URL"]?.url || "";
          
          const low = (name + " " + direct_url).toLowerCase();
          
          let platform = props["Nền tảng"]?.select?.name;
          if (!platform) {
            if (low.includes("zalo")) platform = "Zalo";
            else if (low.includes("facebook") || low.includes("fanpage") || low.includes("profile")) platform = "Facebook";
            else if (low.includes("google") || low.includes("gbp") || low.includes("maps.app.goo.gl")) platform = "Google";
            else if (low.includes("youtube") || low.includes("channel")) platform = "Youtube";
            else if (low.includes("tiktok")) platform = "Tiktok";
            else if (low.includes("pinterest")) platform = "Pinterest";
            else if (low.includes("x.com") || low.includes("twitter")) platform = "X";
            else if (low.includes("website") || low.includes(".vn") || low.includes(".org") || low.includes(".com")) platform = "Website";
            else platform = "Khác";
          }

          const gioithieu = (props["Giới thiệu"]?.rich_text || props["Lý do"]?.rich_text || []).map(x => x.plain_text || "").join("").trim();
          const vaitro = (props["Vai trò"]?.rich_text || props["Mục đích"]?.rich_text || []).map(x => x.plain_text || "").join("").trim();
          const mucdich = (props["Mục đích"]?.rich_text || []).map(x => x.plain_text || "").join("").trim();
          
          const relDomain = (props["LĨNH VỰC CÔNG VIỆC"]?.relation || props["Lĩnh vực"]?.relation || []).map(r => r.id);
          let domain_scope = "mo-hinh";
          if (low.includes("golf") || (relDomain.includes(DOMAIN_REL_MAP["golf"]) && !relDomain.includes(DOMAIN_REL_MAP["mo-hinh"]))) {
            domain_scope = "golf";
          } else if (relDomain.includes(DOMAIN_REL_MAP["tmdt"]) && !relDomain.includes(DOMAIN_REL_MAP["mo-hinh"])) {
            domain_scope = "tmdt";
          } else if (low.includes("vatlieumohinh") || low.includes("lammohinh") || low.includes("vật liệu") || low.includes("ánh dương") || low.includes("shop")) {
            domain_scope = "tmdt";
          } else if (relDomain.includes(DOMAIN_REL_MAP["khac"]) && !relDomain.includes(DOMAIN_REL_MAP["mo-hinh"])) {
            domain_scope = "khac";
          } else {
            domain_scope = "mo-hinh";
          }

          const meta = getPlatformMeta(platform);
          return {
            id: p.id,
            name: name || "Chưa đặt tên",
            platform: platform,
            category: meta.category,
            icon_class: meta.icon,
            badge_class: meta.bg,
            type: vaitro || "Tài khoản B2B",
            frequency: "Duy trì hoạt động",
            direct_url: direct_url || "#",
            notion_url: p.url,
            desc: gioithieu || "Kênh phân phối nội dung của Song Anh.",
            gioithieu,
            vaitro,
            mucdich,
            domain_scope,
            status: "Active"
          };
        }).filter(c => c.name);

        return new Response(
          JSON.stringify({ ok: true, channels, total: channels.length, source_db: targetDb }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // 2. POST /api/notion/save-social-channel
    if (url.pathname === "/api/notion/save-social-channel" && request.method === "POST") {
      try {
        const body = await request.json();
        const { id, name, platform, direct_url, gioithieu, vaitro, mucdich, desc, domain_scope } = body;
        const token = env.NOTION_TOKEN || NOTION_API_KEY;

        if (!name || String(name).trim() === "") {
          return new Response(
            JSON.stringify({ ok: false, error: "Tên kênh không được để trống" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const properties = {
          "Tên kênh": { title: [{ text: { content: String(name).trim() } }] }
        };
        if (platform) {
          properties["Nền tảng"] = { select: { name: platform } };
        }
        if (direct_url !== undefined) {
          const trimmedUrl = String(direct_url).trim();
          properties["URL"] = (trimmedUrl && trimmedUrl.startsWith("http")) ? { url: trimmedUrl } : { url: null };
        }
        if (gioithieu !== undefined || desc !== undefined) {
          properties["Giới thiệu"] = { rich_text: [{ text: { content: String(gioithieu || desc || "") } }] };
        }
        if (vaitro !== undefined) {
          properties["Vai trò"] = { rich_text: [{ text: { content: String(vaitro || "") } }] };
        }
        if (mucdich !== undefined) {
          properties["Mục đích"] = { rich_text: [{ text: { content: String(mucdich || "") } }] };
        }
        if (domain_scope && DOMAIN_REL_MAP[domain_scope]) {
          properties["Lĩnh vực"] = { relation: [{ id: DOMAIN_REL_MAP[domain_scope] }] };
        }

        const isUuid = id && id.length >= 32 && !id.startsWith("soc-");
        if (isUuid) {
          const updateRes = await fetch(`https://api.notion.com/v1/pages/${id}`, {
            method: "PATCH",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Notion-Version": NOTION_API_VERSION,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({ properties })
          });
          const updateData = await updateRes.json();
          if (!updateRes.ok) {
            return new Response(
              JSON.stringify({ ok: false, error: updateData.message || "Lỗi cập nhật trang Notion" }),
              { status: updateRes.status, headers: { ...corsHeaders, "Content-Type": "application/json" } }
            );
          }
          return new Response(
            JSON.stringify({ ok: true, updated: true, page_id: id, url: updateData.url }),
            { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        } else {
          let targetDb = NOTION_SOCIAL_DB_PRIMARY;
          let createRes = await fetch("https://api.notion.com/v1/pages", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Notion-Version": NOTION_API_VERSION,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              parent: { database_id: targetDb },
              properties
            })
          });

          if (createRes.status === 404) {
            targetDb = NOTION_SOCIAL_DB_FALLBACK;
            createRes = await fetch("https://api.notion.com/v1/pages", {
              method: "POST",
              headers: {
                "Authorization": `Bearer ${token}`,
                "Notion-Version": NOTION_API_VERSION,
                "Content-Type": "application/json"
              },
              body: JSON.stringify({
                parent: { database_id: targetDb },
                properties
              })
            });
          }

          const createData = await createRes.json();
          if (!createRes.ok) {
            return new Response(
              JSON.stringify({ ok: false, error: createData.message || "Lỗi tạo kênh mới trên Notion" }),
              { status: createRes.status, headers: { ...corsHeaders, "Content-Type": "application/json" } }
            );
          }
          return new Response(
            JSON.stringify({ ok: true, created: true, page_id: createData.id, url: createData.url, source_db: targetDb }),
            { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // 3. POST /api/notion/delete-social-channel
    if (url.pathname === "/api/notion/delete-social-channel" && request.method === "POST") {
      try {
        const body = await request.json();
        const { id } = body;
        const token = env.NOTION_TOKEN || NOTION_API_KEY;

        if (!id || id.startsWith("soc-")) {
          return new Response(
            JSON.stringify({ ok: true, deleted: true, note: "Local channel removed" }),
            { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const delRes = await fetch(`https://api.notion.com/v1/pages/${id}`, {
          method: "PATCH",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ archived: true })
        });
        const delData = await delRes.json();
        if (!delRes.ok) {
          return new Response(
            JSON.stringify({ ok: false, error: delData.message || "Lỗi lưu trữ kênh trên Notion" }),
            { status: delRes.status, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }
        return new Response(
          JSON.stringify({ ok: true, deleted: true, page_id: id }),
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

    // API: POST /api/notion/create-marketing-post (Đồng bộ 2 chiều: Tạo bài đăng mới trực tiếp vào Notion BẢNG BÀI ĐĂNG MARKETING)
    if (url.pathname === "/api/notion/create-marketing-post" && request.method === "POST") {
      try {
        const body = await request.json();
        const { title, channel, date, caption, url: postUrl, status, interaction, task_id, topic_id, update_type } = body;

        if (!title || !channel) {
          return new Response(
            JSON.stringify({ ok: false, error: "Thiếu Tiêu đề bài đăng hoặc Kênh xuất bản" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const POSTS_DB_ID = env.MARKETING_POSTS_DB_ID || "3de4b5e7-3d90-81d4-aa43-f800ae1870c7";
        
        let isoDate = date ? String(date).trim() : new Date().toISOString().substring(0, 10);
        if (isoDate.includes("/")) {
          const parts = isoDate.split("/");
          if (parts.length === 3) {
            isoDate = `${parts[2]}-${parts[1].padStart(2, "0")}-${parts[0].padStart(2, "0")}`;
          }
        }

        const channelIdMap = {
          "Fanpage Mô hình kiến trúc Song Anh": "39d4b5e7-3d90-8145-8ff2-e255190d0e6a",
          "Fanpage Architectural Model Org": "3aa4b5e7-3d90-80f2-b98c-c03c4e6f384c",
          "Fanpage Làm mô hình Song Anh": "3aa4b5e7-3d90-80fa-916f-f05294adbd65",
          "Fanpage Vật liệu mô hình": "3af4b5e7-3d90-81da-b761-e2a06944238f",
          "Profile Song Anh": "39d4b5e7-3d90-8131-9be4-c0ee9fea8fb8",
          "Profile Tiến RS": "3af4b5e7-3d90-8142-a4d6-fcb9ad5ce344",
          "Profile Mô hình Song Anh": "3af4b5e7-3d90-812e-b863-cefd7b4f6727",
          "Zalo  0981 169 200": "39d4b5e7-3d90-81ff-9360-f252aebbfc18",
          "Zalo Steven (0981169200)": "39d4b5e7-3d90-81ff-9360-f252aebbfc18",
          "Zalo  0988 080 440": "39d4b5e7-3d90-8132-a289-c10337cc85a8",
          "Zalo CSKH (0988080440)": "39d4b5e7-3d90-8132-a289-c10337cc85a8",
          "Zalo 0376 41 51 31": "39d4b5e7-3d90-81fd-9671-cd411da3b218",
          "Zalo Sale (0376415131)": "39d4b5e7-3d90-81fd-9671-cd411da3b218",
          "Zalo 0386 989 087": "39d4b5e7-3d90-8103-a730-fdcf1280acc3",
          "Zalo CSKH 0386 989 087": "39d4b5e7-3d90-8103-a730-fdcf1280acc3",
          "GBP Sa bàn kiến trúc Song Anh": "39d4b5e7-3d90-81d6-bc82-c9d5644a13ac",
          "GBP Dịch vụ làm mô hình kiến trúc Song Anh": "39d4b5e7-3d90-8104-88f1-df54c99bc328",
          "GBP Mô hình kiến trúc Song Anh": "39d4b5e7-3d90-81b8-8e18-e5ef67a3683e",
          "Google Business Profile (GBP)": "39d4b5e7-3d90-81d6-bc82-c9d5644a13ac",
          "Website mohinhkientruc.org": "3d64b5e7-3d90-8126-bc9c-c16c36b14b39",
          "Website (mohinhkientruc.org)": "3d64b5e7-3d90-8126-bc9c-c16c36b14b39",
          "Website architecturalmodel.org": "3d64b5e7-3d90-8136-ab59-cdd9684764bb",
          "Website (architecturalmodel.org)": "3d64b5e7-3d90-8136-ab59-cdd9684764bb",
          "Website lammohinh.vn": "3d64b5e7-3d90-81d3-8aba-f7c8a6064052",
          "Website vatlieumohinh.com": "3d64b5e7-3d90-8159-b297-e07f1453d135",
          "Website mohinhsonganh.com": "3d64b5e7-3d90-81ad-926a-c99b4f13e039",
          "Website mohinh3d.org": "3e34b5e7-3d90-8180-bb48-d94947406b38",

          "Facebook Fanpage": "39d4b5e7-3d90-8145-8ff2-e255190d0e6a",
          "Facebook Profile Song Anh": "39d4b5e7-3d90-8131-9be4-c0ee9fea8fb8"
        };

        let targetChannelId = (body.channel_id && body.channel_id.trim() !== "") ? body.channel_id.trim() : (channelIdMap[channel] || (channel && channel.length === 36 ? channel : null));

        const properties = {
          "Tiêu đề bài đăng": {
            title: [{ text: { content: title.trim() } }]
          },
          "Ngày đăng": {
            date: { start: isoDate }
          },
          "Nội dung bài đăng": {
            rich_text: [{ text: { content: (caption || title).substring(0, 1900) } }]
          },
          "Trạng thái": {
            select: { name: status || "Đã xuất bản" }
          }
        };

        if (update_type && update_type.trim() !== "") {
          properties["Loại cập nhật"] = { select: { name: update_type.trim() } };
        }

        if (targetChannelId) {
          properties["Kênh xuất bản"] = { relation: [{ id: targetChannelId }] };
        }

        if (postUrl && postUrl.trim() !== "") {
          properties["Link bài viết"] = { url: postUrl.trim() };
        }

        const cleanTaskId = task_id ? task_id.trim() : "";
        const invalidDbIds = ["1b04b5e7-3d90-8034-9672-da62f67a96b3", "19a4b5e73d9080f4a51ef769967547a5", "19a4b5e7-3d90-80f4-a51e-f769967547a5"];
        if (cleanTaskId !== "" && !invalidDbIds.includes(cleanTaskId)) {
          properties["Liên kết Công việc"] = { relation: [{ id: cleanTaskId }] };
        }

        let notionRes = await fetch("https://api.notion.com/v1/pages", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            parent: { database_id: POSTS_DB_ID },
            properties: properties
          })
        });

        let data = await notionRes.json();
        // Fallback retry: nếu bị lỗi object_not_found do task relation không tồn tại / không share quyền, tự động thử lại bỏ qua task relation
        if (!notionRes.ok && data && (data.code === "object_not_found" || data.status === 404) && properties["Liên kết Công việc"]) {
          console.warn("⚠️ Task ID không hợp lệ hoặc không có quyền truy cập, đang tự động retry bỏ qua relation...");
          delete properties["Liên kết Công việc"];
          notionRes = await fetch("https://api.notion.com/v1/pages", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Notion-Version": NOTION_API_VERSION,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              parent: { database_id: POSTS_DB_ID },
              properties: properties
            })
          });
          data = await notionRes.json();
        }

        if (!notionRes.ok) {
          return new Response(
            JSON.stringify({ ok: false, error: data }),
            { status: notionRes.status, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        // 1. Tự động ghi đồng bộ sang NHẬT KÝ THAO TÁC MARKETING SONG ANH (Activity Log)
        const ACTIVITY_LOG_DB_ID = env.MARKETING_ACTIVITY_LOG_DB_ID || "3c24b5e7-3d90-81b4-b505-f85f9c9bfcae";
        try {
          const categoryMap = {
            "Zalo": "19d4b5e7-3d90-80ed-9fda-d01265b18153",
            "Facebook": "19d4b5e7-3d90-8032-8803-d348e22f7d08",
            "Fanpage": "19d4b5e7-3d90-8032-8803-d348e22f7d08",
            "Profile": "19d4b5e7-3d90-8032-8803-d348e22f7d08",
            "Group": "19d4b5e7-3d90-8032-8803-d348e22f7d08",
            "GBP": "2434b5e7-3d90-8058-af4e-d895584b10f3",
            "Google Business": "2434b5e7-3d90-8058-af4e-d895584b10f3",
            "Pinterest": "2174b5e7-3d90-8053-aded-d66bf305a9e5",
            "Website": "19d4b5e7-3d90-801e-b69a-e8078aec40d0"
          };
          
          let catId = null;
          for (const [key, id] of Object.entries(categoryMap)) {
            if ((channel || "").includes(key)) {
              catId = id;
              break;
            }
          }

          const now = new Date();
          const vnTime = new Date(now.getTime() + (7 * 60 * 60 * 1000));
          const dd = String(vnTime.getUTCDate()).padStart(2, "0");
          const mm = String(vnTime.getUTCMonth() + 1).padStart(2, "0");
          const yyyy = vnTime.getUTCFullYear();
          const hh = String(vnTime.getUTCHours()).padStart(2, "0");
          const min = String(vnTime.getUTCMinutes()).padStart(2, "0");
          const ss = String(vnTime.getUTCSeconds()).padStart(2, "0");
          const timestampStr = `${dd}/${mm}/${yyyy} ${hh}:${min}:${ss}`;

          const cleanTitle = (title || "").replace(/^\[.*?\]\s*/, '').trim();
          const cleanChannel = (channel || "").replace(/^Website\s+/i, '');
          const logAction = (update_type && update_type.trim() !== "")
            ? `[Website ${update_type.trim()}] ${cleanChannel}: ${cleanTitle}`
            : `[Post] ${channel}: ${cleanTitle}`;
          const logNotes = (update_type && update_type.trim() !== "")
            ? `- Loại cập nhật: ${update_type.trim()}\n- Website: ${channel}\n- Trạng thái: ${status || 'Đã xuất bản'}\n- Link: ${postUrl ? postUrl.trim() : 'Chưa gắn link'}\n- Ghi chú: ${(caption || title).substring(0, 300)}`
            : `- Post ${channel}\n- Trạng thái: ${status || 'Đã xuất bản'}\n- Link: ${postUrl ? postUrl.trim() : 'Chưa gắn link'}\n- Tóm tắt: ${(caption || title).substring(0, 300)}`;

          const logProperties = {
            "Hành Động": {
              title: [{ text: { content: logAction.substring(0, 190) } }]
            },
            "Thời Gian": {
              rich_text: [{ text: { content: timestampStr } }]
            },
            "Người Thực Hiện": {
              rich_text: [{ text: { content: "Phạm Hoàng Tiến" } }]
            },
            "Trạng Thái": {
              select: { name: "✅ Hoàn Thành" }
            },
            "Mô Tả Ngắn": {
              rich_text: [{ text: { content: logNotes.substring(0, 1900) } }]
            }
          };

          if (update_type && update_type.trim() !== "") {
            logProperties["Loại cập nhật"] = { select: { name: update_type.trim() } };
          }

          if (catId) {
            logProperties["Hạng mục"] = { relation: [{ id: catId }] };
          }

          await fetch("https://api.notion.com/v1/pages", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Notion-Version": NOTION_API_VERSION,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              parent: { database_id: ACTIVITY_LOG_DB_ID },
              properties: logProperties
            })
          });
        } catch (actLogErr) {
          console.warn("Lỗi ghi đồng thời Activity Log Notion:", actLogErr);
        }

        // 2. Tự động cập nhật +1 Đã thực hiện cho Task trên Notion
        if (task_id && task_id.trim() !== "") {
          try {
            const cleanTaskId = task_id.trim();
            const taskGetRes = await fetch(`https://api.notion.com/v1/pages/${cleanTaskId}`, {
              headers: {
                "Authorization": `Bearer ${token}`,
                "Notion-Version": NOTION_API_VERSION
              }
            });
            if (taskGetRes.ok) {
              const taskData = await taskGetRes.json();
              const curDone = (taskData.properties && taskData.properties["Đã thực hiện"] && typeof taskData.properties["Đã thực hiện"].number === "number")
                ? taskData.properties["Đã thực hiện"].number
                : 0;
              await fetch(`https://api.notion.com/v1/pages/${cleanTaskId}`, {
                method: "PATCH",
                headers: {
                  "Authorization": `Bearer ${token}`,
                  "Notion-Version": NOTION_API_VERSION,
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({
                  properties: {
                    "Đã thực hiện": { number: curDone + 1 }
                  }
                })
              });

              // Cập nhật tự động lên Task Cha (mục gốc) nếu có
              const parentRels = (taskData.properties && taskData.properties["mục gốc"] && taskData.properties["mục gốc"].relation) || [];
              for (const pRel of parentRels) {
                if (pRel && pRel.id) {
                  try {
                    const pGet = await fetch(`https://api.notion.com/v1/pages/${pRel.id}`, {
                      headers: { "Authorization": `Bearer ${token}`, "Notion-Version": NOTION_API_VERSION }
                    });
                    if (pGet.ok) {
                      const pData = await pGet.json();
                      const pDone = (pData.properties && pData.properties["Đã thực hiện"] && typeof pData.properties["Đã thực hiện"].number === "number")
                        ? pData.properties["Đã thực hiện"].number
                        : 0;
                      await fetch(`https://api.notion.com/v1/pages/${pRel.id}`, {
                        method: "PATCH",
                        headers: { "Authorization": `Bearer ${token}`, "Notion-Version": NOTION_API_VERSION, "Content-Type": "application/json" },
                        body: JSON.stringify({ properties: { "Đã thực hiện": { number: pDone + 1 } } })
                      });
                    }
                  } catch (pe) {
                    console.warn("Lỗi cập nhật task cha trong create-marketing-post:", pe);
                  }
                }
              }
            }
          } catch (taskUpErr) {
            console.warn("Lỗi cập nhật tiến độ Task Notion:", taskUpErr);
          }
        }

        // 3. Tự động đồng bộ vào Google Sheet Tab "Url" của website tương ứng
        let gsheetSync = null;
        const isWebsiteChannel = (channel && channel.toLowerCase().includes("website")) || (update_type && update_type.trim() !== "");
        if (isWebsiteChannel && postUrl && postUrl.trim() !== "") {
          try {
            gsheetSync = await syncPostToGoogleSheet({
              channel,
              postUrl,
              title,
              status,
              caption,
              update_type
            });
          } catch (gsErr) {
            console.warn("Lỗi đồng bộ tự động Google Sheet:", gsErr);
          }
        }

        return new Response(
          JSON.stringify({ ok: true, id: data.id, url: data.url, gsheet_sync: gsheetSync }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      } catch (err) {
        return new Response(
          JSON.stringify({ ok: false, error: err.message }),
          { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
    }

    // API: POST /api/gsheet/sync-website-post (Đồng bộ trực tiếp bài viết Website vào Tab Url Google Sheet)
    if (url.pathname === "/api/gsheet/sync-website-post" && request.method === "POST") {
      try {
        const body = await request.json();
        const syncResult = await syncPostToGoogleSheet(body);
        return new Response(JSON.stringify(syncResult), {
          status: syncResult && syncResult.ok ? 200 : 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      } catch (err) {
        return new Response(JSON.stringify({ ok: false, error: err.message }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
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

    // API: POST /api/gsheet/update-url (Chỉnh sửa và cập nhật bài viết trực tiếp vào Google Sheet Tab Url)
    if (url.pathname === "/api/gsheet/update-url" && request.method === "POST") {
      try {
        const body = await request.json().catch(() => ({}));
        const {
          code,
          title,
          url: pageUrl,
          category,
          silo,
          keyword,
          related_keywords,
          rankmath,
          todo,
          assignee,
          status,
          deadline,
          meta_desc,
          h1,
          h2
        } = body;

        if (!code) {
          return new Response(
            JSON.stringify({ ok: false, error: "Thiếu mã bài viết (code: URL-xxx)" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const googleToken = await getGoogleSheetsToken();
        const sheetId = env.SPREADSHEET_ID || GOOGLE_SPREADSHEET_ID;

        // 1. Quét Cột B (Mã) để xác định chính xác dòng dữ liệu
        const colBRes = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Url!B2:B250`, {
          headers: { 'Authorization': `Bearer ${googleToken}` }
        });
        const colBData = await colBRes.json();
        const rowsB = colBData.values || [];

        let targetRow = -1;
        for (let i = 0; i < rowsB.length; i++) {
          if (rowsB[i][0] && rowsB[i][0].trim().toUpperCase() === code.trim().toUpperCase()) {
            targetRow = i + 2;
            break;
          }
        }

        if (targetRow === -1) {
          const num = parseInt(code.replace(/[^0-9]/g, ''), 10);
          if (num > 0 && num <= 250) {
            targetRow = num + 1;
          } else {
            return new Response(
              JSON.stringify({ ok: false, error: `Không tìm thấy dòng cho mã ${code}` }),
              { status: 404, headers: { ...corsHeaders, "Content-Type": "application/json" } }
            );
          }
        }

        // 2. Đọc dòng hiện tại (A:W) để giữ nguyên các cột không chỉnh sửa
        const curRowRes = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Url!A${targetRow}:W${targetRow}`, {
          headers: { 'Authorization': `Bearer ${googleToken}` }
        });
        const curRowData = await curRowRes.json();
        const curValues = (curRowData.values && curRowData.values[0]) || [];

        while (curValues.length < 23) {
          curValues.push('');
        }

        // 3. Cập nhật các cột được truyền lên
        if (title !== undefined) curValues[2] = title;
        if (pageUrl !== undefined && pageUrl.trim() !== '') curValues[3] = pageUrl;
        if (category !== undefined) curValues[4] = category;
        if (silo !== undefined) curValues[5] = silo;
        if (keyword !== undefined) curValues[6] = keyword;
        if (related_keywords !== undefined) curValues[7] = related_keywords;
        if (rankmath !== undefined) curValues[8] = String(rankmath);
        if (todo !== undefined) curValues[9] = todo;
        if (assignee !== undefined) curValues[10] = assignee;
        if (status !== undefined) curValues[11] = status;
        if (deadline !== undefined) curValues[12] = deadline;
        if (title !== undefined) curValues[13] = String(title.length);
        if (meta_desc !== undefined) curValues[15] = meta_desc;
        if (meta_desc !== undefined) curValues[16] = String(meta_desc.length);
        if (h1 !== undefined) curValues[18] = h1;
        if (h2 !== undefined) curValues[20] = h2;

        // 4. Ghi đè vào Google Sheet
        const updateRes = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/Url!A${targetRow}:W${targetRow}?valueInputOption=USER_ENTERED`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${googleToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            values: [curValues]
          })
        });

        const updateData = await updateRes.json();
        if (!updateRes.ok) {
          return new Response(
            JSON.stringify({ ok: false, error: updateData }),
            { status: updateRes.status, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        // 5. Cập nhật đồng bộ Notion nếu có Notion link
        let notionUpdated = false;
        const notionLink = curValues[22];
        if (notionLink && token) {
          const idMatch = notionLink.match(/([a-f0-9]{32})/i);
          if (idMatch) {
            const notionPageId = idMatch[1];
            const notionProps = {};
            if (title !== undefined) notionProps["Tiêu đề"] = { title: [{ text: { content: title } }] };
            if (keyword !== undefined) notionProps["Từ khóa chính"] = { rich_text: [{ text: { content: keyword } }] };
            if (related_keywords !== undefined) notionProps["Từ khóa phụ (LSI Keywords)"] = { rich_text: [{ text: { content: related_keywords } }] };
            if (rankmath !== undefined && !isNaN(parseInt(rankmath))) notionProps["Rank Math SEO"] = { number: parseInt(rankmath) };
            if (todo !== undefined) notionProps["Việc cần làm"] = { rich_text: [{ text: { content: todo } }] };
            if (status !== undefined) {
              notionProps["Trạng thái bài viết"] = { select: { name: status } };
            }

            try {
              await fetch(`https://api.notion.com/v1/pages/${notionPageId}`, {
                method: "PATCH",
                headers: {
                  "Authorization": `Bearer ${token}`,
                  "Notion-Version": NOTION_API_VERSION,
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({ properties: notionProps })
              });
              notionUpdated = true;
            } catch (e) {
              console.warn("Notion sync warning:", e);
            }
          }
        }

        return new Response(
          JSON.stringify({
            ok: true,
            message: `Đã cập nhật thành công vào Google Sheet (Dòng ${targetRow})!`,
            row: targetRow,
            code: code,
            notion_synced: notionUpdated,
            updated_data: {
              code,
              title: curValues[2],
              url: curValues[3],
              category: curValues[4],
              silo: curValues[5],
              keyword: curValues[6],
              related_keywords: curValues[7],
              rankmath: curValues[8],
              todo: curValues[9],
              assignee: curValues[10],
              status: curValues[11],
              deadline: curValues[12],
              title_length: curValues[13],
              meta_desc: curValues[15],
              meta_length: curValues[16],
              h1_1: curValues[18],
              h2_1: curValues[20]
            }
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

    // SPA Fallback: Any non-API route without static file extension rewrites to /index.html
    let assetReq = request;
    const isApi = url.pathname.startsWith("/api/");
    const hasExt = url.pathname.includes(".") && !url.pathname.endsWith(".html");
    const isSpaPath = !isApi && (!hasExt || url.pathname === "/login");

    if (isSpaPath && url.pathname !== "/" && url.pathname !== "/index.html") {
      const newUrl = new URL(request.url);
      newUrl.pathname = "/index.html";
      assetReq = new Request(newUrl, request);
    }

    // Default: Fallback to Cloudflare Workers Static Assets with no-cache for HTML
    const assetRes = await env.ASSETS.fetch(assetReq);
    if (isSpaPath || url.pathname === "/" || url.pathname.endsWith(".html")) {
      const freshHeaders = new Headers(assetRes.headers);
      freshHeaders.set("Cache-Control", "no-cache, no-store, must-revalidate");
      freshHeaders.set("Pragma", "no-cache");
      freshHeaders.set("Expires", "0");
      return new Response(assetRes.body, {
        status: assetRes.status,
        statusText: assetRes.statusText,
        headers: freshHeaders
      });
    }
    return assetRes;
  }
};
