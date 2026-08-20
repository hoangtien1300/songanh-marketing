# -*- coding: utf-8 -*-
"""
Update script to add Master Home Dashboard (#panel-home) and Marketing Activity Log Table to index.html & marketing_data.json
Author: song_anh_code_expert (Lead Developer Agent)
"""

import sys
import json
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

INDEX_PATH = r"d:\Song_Anh\marketing_workflow_app\index.html"
DATA_PATH = r"d:\Song_Anh\marketing_workflow_app\marketing_data.json"

# 1. Update marketing_data.json
activity_logs = [
    {
        "id": 1,
        "timestamp": "20/08/2026 16:10:00",
        "module": "Meta API & FB Groups",
        "action": "Đồng bộ 259 Facebook Groups Profile & Fanpage sang Notion Database thành công",
        "executor": "song_anh_code_expert (Lead Developer)",
        "status": "⚡ Real-time Auto Sync"
    },
    {
        "id": 2,
        "timestamp": "20/08/2026 16:09:28",
        "module": "SEO Google (GSC & GA4)",
        "action": "Cập nhật thứ hạng 22 Từ Khóa B2B Real-time GSC (Top 1-3: 13 KWs, Top 4-10: 9 KWs)",
        "executor": "Trợ Lý AI Song Anh (SEO SubAgent)",
        "status": "✅ Hoàn Thành"
    },
    {
        "id": 3,
        "timestamp": "20/08/2026 15:36:07",
        "module": "Facebook Marketing",
        "action": "Đăng bài viết dự án Sa Bàn Cao Tầng vào 15 Groups M&A Kiến Trúc & BĐS",
        "executor": "Trợ Lý AI Song Anh (Facebook SubAgent)",
        "status": "✅ Hoàn Thành"
    },
    {
        "id": 4,
        "timestamp": "20/08/2026 14:20:00",
        "module": "Google Business Profile",
        "action": "Cập nhật hình ảnh dự án mới & Đồng bộ đánh giá 4.9⭐ trên 3 Chi nhánh (TP.HCM, Hà Nội, Cần Thơ)",
        "executor": "Phạm Hoàng Tiến (Master Admin)",
        "status": "✅ Hoàn Thành"
    },
    {
        "id": 5,
        "timestamp": "20/08/2026 11:15:00",
        "module": "Zalo OA & Zalo Personal",
        "action": "Gửi báo giá sa bàn quy hoạch KCN cho 8 Khách hàng B2B Inbox",
        "executor": "Phạm Hoàng Tiến (Master Admin)",
        "status": "✅ Hoàn Thành"
    },
    {
        "id": 6,
        "timestamp": "20/08/2026 09:00:00",
        "module": "Notion Task Management",
        "action": "Khởi tạo & Phân công 15 Active Tasks Marketing Mô hình Kiến trúc Tuần 34",
        "executor": "Trợ Lý AI Song Anh (Master Agent)",
        "status": "⚡ Real-time Auto Sync"
    },
    {
        "id": 7,
        "timestamp": "19/08/2026 17:45:00",
        "module": "Facebook Fanpage",
        "action": "Thu thập Insights Meta API: 1,128 Followers Live, 10 Views, 86 Leads Inbox",
        "executor": "song_anh_code_expert (Lead Developer)",
        "status": "✅ Hoàn Thành"
    },
    {
        "id": 8,
        "timestamp": "19/08/2026 14:30:00",
        "module": "SEO On-Page",
        "action": "Tối ưu Schema JSON-LD Product & LocalBusiness cho website mohinhkientruc.org",
        "executor": "Trợ Lý AI Song Anh (SEO SubAgent)",
        "status": "✅ Hoàn Thành"
    }
]

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

data["marketing_activity_log"] = activity_logs

with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Successfully updated marketing_data.json with marketing_activity_log!")

# 2. Update index.html
with open(INDEX_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Update Sidebar: Add Home Dashboard button at top
sidebar_target = '<div class="space-y-1 text-xs">'
home_button_html = '''<div class="space-y-1 text-xs">
                    
                    <!-- 0. TRANG CHỦ MASTER HOME DASHBOARD -->
                    <div class="accordion-group rounded-xl border border-blue-200 bg-blue-50/70 overflow-hidden mb-2">
                        <button onclick="selectModule('home')" id="sub-home" class="sub-link active w-full flex items-center justify-between p-2.5 font-bold text-brand-navy hover:bg-blue-100/80 transition">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-house text-blue-600 w-4"></i>
                                <span>🏠 Trang Chủ (Master Home Dashboard)</span>
                            </div>
                            <span class="text-[9px] px-1.5 py-0.2 rounded bg-blue-600 text-white font-extrabold">LIVE</span>
                        </button>
                    </div>'''

if 'id="sub-home"' not in html and sidebar_target in html:
    # Remove active class from sub-keywords if sub-home is active
    html = html.replace('id="sub-keywords" class="sub-link active', 'id="sub-keywords" class="sub-link')
    html = html.replace(sidebar_target, home_button_html)
    print("✅ Inserted Home Dashboard button at top of Sidebar!")

# Update Main Area: Add panel-home and hide panel-keywords by default
panel_keywords_target = '<div id="panel-keywords" class="module-panel space-y-5">'

panel_home_html = '''<!-- 0. MASTER HOME DASHBOARD PANEL (#panel-home) -->
            <div id="panel-home" class="module-panel space-y-6">
                <!-- Header Section for Home Dashboard -->
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-brand-navy to-slate-800 p-6 rounded-2xl text-white shadow-lg border border-slate-700">
                    <div class="space-y-1">
                        <div class="flex items-center gap-2">
                            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-black uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30 flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                                Master Home Dashboard Live
                            </span>
                            <span class="text-xs text-slate-300 font-medium">Song Anh Architecture Marketing Suite</span>
                        </div>
                        <h2 class="text-xl font-heading font-black text-white flex items-center gap-2.5">
                            <span>🏠 TRANG CHỦ TỔNG QUAN HỆ THỐNG MARKETING</span>
                        </h2>
                        <p class="text-xs text-slate-300">Báo cáo chỉ số KPI đa kênh Real-time &amp; Bảng nhật ký thao tác Marketing hệ thống</p>
                    </div>
                    <div class="flex items-center gap-3 shrink-0">
                        <button onclick="fetchData()" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-md hover:shadow-blue-500/20 border border-blue-400/30">
                            <i class="fa-solid fa-rotate text-xs"></i>
                            <span>Đồng Bộ Real-time</span>
                        </button>
                    </div>
                </div>

                <!-- 4 KPI SUMMARY CARDS -->
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <!-- 1. SEO Master Overview -->
                    <div class="bg-white p-5 rounded-2xl border border-sky-100 shadow-sm hover:shadow-md transition relative overflow-hidden group">
                        <div class="absolute top-0 right-0 w-24 h-24 bg-sky-50 rounded-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                        <div class="relative z-10 space-y-3">
                            <div class="flex items-center justify-between">
                                <div class="w-10 h-10 rounded-xl bg-sky-100 text-sky-600 flex items-center justify-center font-bold text-lg border border-sky-200">
                                    <i class="fa-solid fa-globe"></i>
                                </div>
                                <span class="px-2 py-0.5 text-[10px] font-extrabold bg-sky-100 text-sky-800 rounded-md border border-sky-200 uppercase">GSC Real-time</span>
                            </div>
                            <div>
                                <p class="text-xs font-bold text-slate-500 uppercase tracking-wider">SEO Master Overview</p>
                                <div class="flex items-baseline gap-2 mt-1">
                                    <h3 id="home-kpi-seo-total" class="text-2xl font-black text-brand-navy">22 KWs</h3>
                                    <span class="text-xs font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">B2B Core</span>
                                </div>
                            </div>
                            <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                                <span class="font-bold text-emerald-700 bg-emerald-100/80 px-2 py-0.5 rounded-lg border border-emerald-200">🏆 Top 1-3: <strong id="home-kpi-seo-top13">13 KWs</strong></span>
                                <span class="font-bold text-blue-700 bg-blue-100/80 px-2 py-0.5 rounded-lg border border-blue-200">🎯 Top 4-10: <strong id="home-kpi-seo-top410">9 KWs</strong></span>
                            </div>
                        </div>
                    </div>

                    <!-- 2. Meta Facebook Channel -->
                    <div class="bg-white p-5 rounded-2xl border border-blue-100 shadow-sm hover:shadow-md transition relative overflow-hidden group">
                        <div class="absolute top-0 right-0 w-24 h-24 bg-blue-50 rounded-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                        <div class="relative z-10 space-y-3">
                            <div class="flex items-center justify-between">
                                <div class="w-10 h-10 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-lg border border-blue-200">
                                    <i class="fa-brands fa-facebook-f"></i>
                                </div>
                                <span class="px-2 py-0.5 text-[10px] font-extrabold bg-blue-100 text-blue-800 rounded-md border border-blue-200 uppercase flex items-center gap-1">
                                    <span class="w-1.5 h-1.5 rounded-full bg-blue-600 animate-ping"></span> Live Meta API
                                </span>
                            </div>
                            <div>
                                <p class="text-xs font-bold text-slate-500 uppercase tracking-wider">Meta Facebook Channel</p>
                                <div class="flex items-baseline gap-2 mt-1">
                                    <h3 id="home-kpi-fb-followers" class="text-2xl font-black text-blue-900">1,128</h3>
                                    <span class="text-xs font-bold text-slate-600">Followers Live</span>
                                </div>
                            </div>
                            <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                                <span class="font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-lg border border-slate-200">👁️ Views: <strong id="home-kpi-fb-views">10</strong></span>
                                <span class="font-bold text-blue-800 bg-blue-100 px-2 py-0.5 rounded-lg border border-blue-200">💬 Leads Inbox: <strong id="home-kpi-fb-leads">86</strong></span>
                            </div>
                        </div>
                    </div>

                    <!-- 3. Google Business Profile -->
                    <div class="bg-white p-5 rounded-2xl border border-rose-100 shadow-sm hover:shadow-md transition relative overflow-hidden group">
                        <div class="absolute top-0 right-0 w-24 h-24 bg-rose-50 rounded-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                        <div class="relative z-10 space-y-3">
                            <div class="flex items-center justify-between">
                                <div class="w-10 h-10 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center font-bold text-lg border border-rose-200">
                                    <i class="fa-solid fa-location-dot"></i>
                                </div>
                                <span class="px-2 py-0.5 text-[10px] font-extrabold bg-amber-100 text-amber-900 rounded-md border border-amber-300 flex items-center gap-1">
                                    <i class="fa-solid fa-star text-amber-500 text-[10px]"></i> Avg 4.9 ⭐
                                </span>
                            </div>
                            <div>
                                <p class="text-xs font-bold text-slate-500 uppercase tracking-wider">Google Business Profile</p>
                                <div class="flex items-baseline gap-2 mt-1">
                                    <h3 id="home-kpi-gbp-branches" class="text-2xl font-black text-rose-950">3 Chi Nhánh</h3>
                                </div>
                            </div>
                            <div class="pt-2 border-t border-slate-100 flex items-center gap-1.5 flex-wrap text-[11px] font-bold">
                                <span class="px-2 py-0.5 bg-slate-100 text-slate-700 rounded-md border border-slate-200">📍 TP.HCM</span>
                                <span class="px-2 py-0.5 bg-slate-100 text-slate-700 rounded-md border border-slate-200">📍 Hà Nội</span>
                                <span class="px-2 py-0.5 bg-slate-100 text-slate-700 rounded-md border border-slate-200">📍 Cần Thơ</span>
                            </div>
                        </div>
                    </div>

                    <!-- 4. Task Management Notion Sync -->
                    <div class="bg-white p-5 rounded-2xl border border-purple-100 shadow-sm hover:shadow-md transition relative overflow-hidden group">
                        <div class="absolute top-0 right-0 w-24 h-24 bg-purple-50 rounded-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                        <div class="relative z-10 space-y-3">
                            <div class="flex items-center justify-between">
                                <div class="w-10 h-10 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center font-bold text-lg border border-purple-200">
                                    <i class="fa-solid fa-list-check"></i>
                                </div>
                                <span class="px-2 py-0.5 text-[10px] font-extrabold bg-purple-100 text-purple-800 rounded-md border border-purple-200 uppercase">Notion API</span>
                            </div>
                            <div>
                                <p class="text-xs font-bold text-slate-500 uppercase tracking-wider">Task &amp; Groups Sync</p>
                                <div class="flex items-baseline gap-2 mt-1">
                                    <h3 id="home-kpi-notion-tasks" class="text-2xl font-black text-purple-950">15 Active Tasks</h3>
                                </div>
                            </div>
                            <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-xs font-bold">
                                <span class="text-purple-800 bg-purple-100 px-2.5 py-0.5 rounded-lg border border-purple-200 flex items-center gap-1">
                                    <i class="fa-solid fa-users text-[10px]"></i> 259 FB Groups
                                </span>
                                <span class="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 text-[10px]">Sync DB</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- MARKETING AUDIT & ACTIVITY LOG TABLE -->
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden space-y-4 p-5">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
                        <div>
                            <h3 class="text-base font-heading font-extrabold text-brand-navy flex items-center gap-2">
                                <span>📋 Bảng Lịch Sử Cập Nhật &amp; Thao Tác Marketing</span>
                                <span class="text-xs font-semibold text-slate-500">(System Real-Time Activity Log)</span>
                            </h3>
                            <p class="text-xs text-slate-500 mt-0.5">Theo dõi lịch sử nhật ký tác vụ tự động và thao tác marketing của nhân sự &amp; Trợ lý AI</p>
                        </div>
                        
                        <!-- Filters & Actions -->
                        <div class="flex flex-wrap items-center gap-2">
                            <div class="relative">
                                <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                                <input type="text" id="activity-log-search-input" onkeyup="filterActivityLogTable()" placeholder="Tìm kiếm nhật ký..." class="pl-8 pr-3 py-1.5 text-xs font-semibold border border-slate-300 rounded-xl bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-48 transition shadow-xs">
                            </div>
                            
                            <select id="activity-log-module-filter" onchange="filterActivityLogTable()" class="px-3 py-1.5 text-xs font-bold border border-slate-300 rounded-xl bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700 cursor-pointer shadow-xs">
                                <option value="">🎯 Tất cả Hạng Mục</option>
                                <option value="Facebook">Facebook / Meta API</option>
                                <option value="SEO">SEO Website</option>
                                <option value="Notion">Notion Sync</option>
                                <option value="GBP">Google Business Profile</option>
                                <option value="Zalo">Zalo Marketing</option>
                            </select>

                            <span id="activity-log-count-badge" class="px-3 py-1.5 text-xs font-extrabold bg-blue-50 text-blue-700 rounded-xl border border-blue-200">
                                8 Nhật Ký
                            </span>
                        </div>
                    </div>

                    <!-- Table Container -->
                    <div class="overflow-x-auto rounded-xl border border-slate-200">
                        <table class="w-full text-left text-xs border-collapse">
                            <thead class="bg-slate-100 text-brand-navy font-bold uppercase tracking-wider border-b border-slate-200">
                                <tr>
                                    <th class="p-3.5 w-44">⏰ Thời Gian</th>
                                    <th class="p-3.5 w-44">🎯 Hạng Mục</th>
                                    <th class="p-3.5">📝 Thao Tác / Hành Động Marketing</th>
                                    <th class="p-3.5 w-48">👤 Người Thực Hiện</th>
                                    <th class="p-3.5 w-40 text-center">🟢 Trạng Thái</th>
                                </tr>
                            </thead>
                            <tbody id="activity-log-table-body" class="divide-y divide-slate-200">
                                <!-- Dynamic Rows -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="panel-keywords" class="module-panel hidden space-y-5">'''

if 'id="panel-home"' not in html and panel_keywords_target in html:
    html = html.replace(panel_keywords_target, panel_home_html)
    print("✅ Inserted #panel-home before #panel-keywords!")

# Update JS Variables
js_vars_target = "        let currentFbGroupChannel = 'fanpage';"
js_vars_addition = '''        let marketingActivityLog = [];
        let currentFbGroupChannel = 'fanpage';'''

if 'let marketingActivityLog' not in html and js_vars_target in html:
    html = html.replace(js_vars_target, js_vars_addition)
    print("✅ Added JS variable marketingActivityLog!")

# Update fetchData() logic
fetch_data_target = "                if (data.zalo_data && data.zalo_data.length > 0) {"
fetch_data_addition = '''                if (data.marketing_activity_log && data.marketing_activity_log.length > 0) {
                    marketingActivityLog = data.marketing_activity_log;
                    renderActivityLogTable();
                }
                if (data.zalo_data && data.zalo_data.length > 0) {'''

if 'marketing_activity_log' not in html and fetch_data_target in html:
    html = html.replace(fetch_data_target, fetch_data_addition)
    print("✅ Added marketing_activity_log handling to fetchData()!")

# Update selectModule() function
select_module_target = "            if (moduleId === 'keywords') {"
select_module_replacement = '''            if (moduleId === 'home') {
                document.getElementById('panel-home').classList.remove('hidden');
                showToast("🏠 Đã mở Trang Chủ: Master Home Dashboard");
            } else if (moduleId === 'keywords') {'''

if "if (moduleId === 'home')" not in html and select_module_target in html:
    html = html.replace(select_module_target, select_module_replacement)
    print("✅ Updated selectModule() to handle 'home' panel!")

# Insert renderActivityLogTable and filterActivityLogTable JS functions
activity_log_js_funcs = '''        function renderActivityLogTable(items) {
            const tbody = document.getElementById('activity-log-table-body');
            const badge = document.getElementById('activity-log-count-badge');
            if (!tbody) return;

            const list = items || marketingActivityLog || [];
            if (badge) badge.innerText = list.length + " Nhật Ký";

            if (list.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="p-6 text-center text-slate-400 font-medium">Không tìm thấy nhật ký thao tác phù hợp.</td></tr>`;
                return;
            }

            let html = '';
            list.forEach(item => {
                const time = item.timestamp || 'N/A';
                const mod = item.module || 'Hệ thống';
                const action = item.action || 'N/A';
                const exec = item.executor || 'Tự động';
                const status = item.status || '✅ Hoàn Thành';

                let modBadge = 'bg-slate-100 text-slate-800 border-slate-200';
                if (mod.toLowerCase().includes('facebook') || mod.toLowerCase().includes('meta')) {
                    modBadge = 'bg-blue-100 text-blue-800 border-blue-200';
                } else if (mod.toLowerCase().includes('seo')) {
                    modBadge = 'bg-sky-100 text-sky-800 border-sky-200';
                } else if (mod.toLowerCase().includes('notion')) {
                    modBadge = 'bg-purple-100 text-purple-800 border-purple-200';
                } else if (mod.toLowerCase().includes('google') || mod.toLowerCase().includes('gbp')) {
                    modBadge = 'bg-rose-100 text-rose-800 border-rose-200';
                } else if (mod.toLowerCase().includes('zalo')) {
                    modBadge = 'bg-indigo-100 text-indigo-800 border-indigo-200';
                }

                let statusBadge = 'bg-emerald-100 text-emerald-800 border-emerald-200';
                if (status.includes('Sync') || status.includes('Auto')) {
                    statusBadge = 'bg-blue-100 text-blue-800 border-blue-200';
                }

                let execIcon = 'fa-user-tie text-brand-navy';
                if (exec.includes('AI') || exec.includes('Agent') || exec.includes('expert')) {
                    execIcon = 'fa-robot text-purple-600';
                } else if (exec.includes('Tiến')) {
                    execIcon = 'fa-user-gear text-amber-600';
                }

                html += `
                    <tr class="hover:bg-slate-50 transition font-medium">
                        <td class="p-3.5 font-mono text-slate-600 font-bold whitespace-nowrap">${time}</td>
                        <td class="p-3.5">
                            <span class="px-2.5 py-1 text-[11px] font-bold rounded-lg border ${modBadge}">${mod}</span>
                        </td>
                        <td class="p-3.5 font-bold text-slate-900 leading-relaxed">${action}</td>
                        <td class="p-3.5 text-slate-800 font-bold whitespace-nowrap">
                            <div class="flex items-center gap-1.5">
                                <i class="fa-solid ${execIcon}"></i>
                                <span>${exec}</span>
                            </div>
                        </td>
                        <td class="p-3.5 text-center whitespace-nowrap">
                            <span class="px-2.5 py-1 text-[11px] font-extrabold rounded-full border ${statusBadge} inline-flex items-center gap-1">
                                ${status}
                            </span>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        }

        function filterActivityLogTable() {
            const query = (document.getElementById('activity-log-search-input')?.value || '').toLowerCase().trim();
            const modFilter = (document.getElementById('activity-log-module-filter')?.value || '').toLowerCase().trim();

            const filtered = marketingActivityLog.filter(item => {
                const time = (item.timestamp || '').toLowerCase();
                const mod = (item.module || '').toLowerCase();
                const action = (item.action || '').toLowerCase();
                const exec = (item.executor || '').toLowerCase();
                const status = (item.status || '').toLowerCase();

                const matchesQuery = !query || (
                    time.includes(query) ||
                    mod.includes(query) ||
                    action.includes(query) ||
                    exec.includes(query) ||
                    status.includes(query)
                );

                const matchesMod = !modFilter || mod.includes(modFilter);

                return matchesQuery && matchesMod;
            });

            renderActivityLogTable(filtered);
        }

'''

if 'function renderActivityLogTable' not in html:
    target_place = '        function switchFbGroupChannel(channelKey) {'
    if target_place in html:
        html = html.replace(target_place, activity_log_js_funcs + target_place)
        print("✅ Added renderActivityLogTable and filterActivityLogTable JS functions!")

# Update DOMContentLoaded listener to render activity log table
dom_content_target = "            updateHeaderCurrentDate();"
dom_content_replacement = '''            updateHeaderCurrentDate();
            renderActivityLogTable();'''

if 'renderActivityLogTable()' not in html and dom_content_target in html:
    html = html.replace(dom_content_target, dom_content_replacement)
    print("✅ Added renderActivityLogTable() to DOMContentLoaded listener!")

# Save index.html
with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("🚀 Finished updating index.html!")
