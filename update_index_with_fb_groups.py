# -*- coding: utf-8 -*-
"""
Script to update index.html with Facebook Groups Joined Table and JS renderer.
File: update_index_with_fb_groups.py
Author: song_anh_code_expert
"""

import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

INDEX_PATH = r"d:\Song_Anh\marketing_workflow_app\index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Insert HTML card into #panel-facebook
target_html_marker = """                        <div class="p-4 rounded-xl border border-slate-200 bg-slate-50/80 hover:bg-white hover:border-blue-300 transition space-y-3">
                            <span class="text-[10px] font-extrabold px-2.5 py-0.5 rounded bg-purple-100 text-purple-800">RE-CMT GROUPS</span>
                            <h4 class="text-xs font-extrabold text-slate-900 border-b border-slate-200 pb-2">[Re-cmt FB Group] | Fanpage Mô hình kiến trúc Song Anh</h4>
                            <div class="space-y-2 text-xs font-sans">
                                <div><span class="text-[10px] font-bold text-amber-800 uppercase block">🎯 1. Mục Đích:</span><p class="text-slate-700 text-[11px]">Tiếp cận hàng ngàn Chủ đầu tư, Kiến trúc sư &amp; Ban quản lý KCN trong 20+ Facebook Groups B2B.</p></div>
                                <div><span class="text-[10px] font-bold text-blue-800 uppercase block">🛠️ 2. Cách Làm:</span><p class="text-slate-700 text-[11px]">Áp dụng Chiến lược Link-in-Comment (đăng bài Value bằng Chữ + Ảnh thực tế, nhúng link danh mục dưới comment sau 5-10 phút chống bóp Reach).</p></div>
                                <div><span class="text-[10px] font-bold text-emerald-800 uppercase block">🚀 3. Mục Tiêu Cần Đạt:</span><p class="text-slate-700 text-[11px] font-semibold text-emerald-700">Rải 20 Groups/tuần, tỷ lệ duy trì bài đăng sống 100%, kéo traffic về mohinhkientruc.org.</p></div>
                            </div>
                        </div>
                    </div>
                </div>"""

new_fb_groups_html_card = """                        <div class="p-4 rounded-xl border border-slate-200 bg-slate-50/80 hover:bg-white hover:border-blue-300 transition space-y-3">
                            <span class="text-[10px] font-extrabold px-2.5 py-0.5 rounded bg-purple-100 text-purple-800">RE-CMT GROUPS</span>
                            <h4 class="text-xs font-extrabold text-slate-900 border-b border-slate-200 pb-2">[Re-cmt FB Group] | Fanpage Mô hình kiến trúc Song Anh</h4>
                            <div class="space-y-2 text-xs font-sans">
                                <div><span class="text-[10px] font-bold text-amber-800 uppercase block">🎯 1. Mục Đích:</span><p class="text-slate-700 text-[11px]">Tiếp cận hàng ngàn Chủ đầu tư, Kiến trúc sư &amp; Ban quản lý KCN trong 20+ Facebook Groups B2B.</p></div>
                                <div><span class="text-[10px] font-bold text-blue-800 uppercase block">🛠️ 2. Cách Làm:</span><p class="text-slate-700 text-[11px]">Áp dụng Chiến lược Link-in-Comment (đăng bài Value bằng Chữ + Ảnh thực tế, nhúng link danh mục dưới comment sau 5-10 phút chống bóp Reach).</p></div>
                                <div><span class="text-[10px] font-bold text-emerald-800 uppercase block">🚀 3. Mục Tiêu Cần Đạt:</span><p class="text-slate-700 text-[11px] font-semibold text-emerald-700">Rải 20 Groups/tuần, tỷ lệ duy trì bài đăng sống 100%, kéo traffic về mohinhkientruc.org.</p></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 🌟 BẢNG DANH SÁCH FACEBOOK GROUPS ĐÃ THAM GIA (FANPAGE MÔ HÌNH KIẾN TRÚC SONG ANH) -->
                <div class="light-card rounded-2xl p-5 border border-slate-200 space-y-4 shadow-sm">
                    <div class="flex flex-col md:flex-row items-start md:items-center justify-between border-b border-slate-200 pb-3 gap-3">
                        <div class="flex items-center gap-2">
                            <i class="fa-solid fa-users-rectangle text-blue-600 text-base"></i>
                            <div>
                                <h3 class="font-heading font-bold text-sm text-slate-900">Danh Sách Facebook Groups Fanpage Đã Tham Gia</h3>
                                <p class="text-[11px] text-slate-500 font-medium">Báo cáo tự động từ Playwright Stealth &amp; Facebook Graph API Engine</p>
                            </div>
                        </div>
                        <div class="flex flex-wrap items-center gap-2 w-full md:w-auto">
                            <span id="fb-joined-groups-count-badge" class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1.5 rounded-xl border border-emerald-200">170 Groups Active</span>
                            <input type="text" id="fb-group-search-input" onkeyup="filterFbJoinedGroups()" placeholder="🔍 Tìm tên group, ID, lĩnh vực..." class="px-3 py-1.5 text-xs font-medium border border-slate-300 rounded-xl bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-56">
                            <a href="fanpage_joined_groups.json" target="_blank" download class="px-3 py-1.5 text-xs font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-xl transition flex items-center gap-1">
                                <i class="fa-solid fa-file-code"></i> JSON
                            </a>
                            <a href="fanpage_joined_groups.xlsx" download class="px-3 py-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-xl transition flex items-center gap-1">
                                <i class="fa-solid fa-file-excel"></i> Excel Report
                            </a>
                        </div>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs border-collapse">
                            <thead>
                                <tr class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                                    <th class="p-3.5 w-12 text-center">STT</th>
                                    <th class="p-3.5">1. Tên Facebook Group &amp; Link Direct</th>
                                    <th class="p-3.5">2. Group ID</th>
                                    <th class="p-3.5">3. Số Thành Viên</th>
                                    <th class="p-3.5">4. Quyền Đăng Bài</th>
                                    <th class="p-3.5">5. Phân Loại Lĩnh Vực</th>
                                    <th class="p-3.5 text-center">6. Trạng Thái</th>
                                </tr>
                            </thead>
                            <tbody id="fb-joined-groups-table-body" class="divide-y divide-slate-200"></tbody>
                        </table>
                    </div>
                </div>"""

if target_html_marker in content:
    content = content.replace(target_html_marker, new_fb_groups_html_card)
    print("✅ Successfully inserted Facebook Groups HTML Card into #panel-facebook!")
else:
    print("[WARN] HTML marker not found!")

# 2. Add JS variable and functions
target_js_marker = "        let fbTaskList = ["

new_js_variable = """        let fbJoinedGroupsList = [];
        let fbTaskList = ["""

if target_js_marker in content and "let fbJoinedGroupsList" not in content:
    content = content.replace(target_js_marker, new_js_variable)
    print("✅ Added fbJoinedGroupsList JS variable!")

# 3. Add fetchData handling
target_fetch_marker = """                if (data.facebook_tasks && data.facebook_tasks.length > 0) {
                    fbTaskList = data.facebook_tasks;
                    renderFbTable();
                }"""

new_fetch_code = """                if (data.facebook_tasks && data.facebook_tasks.length > 0) {
                    fbTaskList = data.facebook_tasks;
                    renderFbTable();
                }
                if (data.fanpage_joined_groups && data.fanpage_joined_groups.length > 0) {
                    fbJoinedGroupsList = data.fanpage_joined_groups;
                    renderFbJoinedGroupsTable(fbJoinedGroupsList);
                }"""

if target_fetch_marker in content and "renderFbJoinedGroupsTable" not in content:
    content = content.replace(target_fetch_marker, new_fetch_code)
    print("✅ Added fanpage_joined_groups handling in fetchData()!")

# 4. Add renderFbJoinedGroupsTable and filterFbJoinedGroups functions
target_renderfb_marker = "        function renderFbTable() {"

new_render_functions = """        function renderFbJoinedGroupsTable(groupsData) {
            const tbody = document.getElementById('fb-joined-groups-table-body');
            const badge = document.getElementById('fb-joined-groups-count-badge');
            if (!tbody) return;

            const list = groupsData || fbJoinedGroupsList || [];
            if (badge) badge.innerText = list.length + " Groups Active";

            if (list.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="p-6 text-center text-slate-400 font-medium">Đang tải dữ liệu danh sách Facebook Groups...</td></tr>`;
                return;
            }

            let html = '';
            list.forEach((g, idx) => {
                const stt = g.stt || (idx + 1);
                const name = g.group_name || 'N/A';
                const url = g.group_url || '#';
                const gid = g.group_id || 'N/A';
                const mem = g.members_count || 'N/A';
                const perm = g.posting_permission || 'Công khai';
                const cat = g.category || '📐 Kiến trúc & Quy hoạch';

                const permColor = perm.includes('Kiểm duyệt') ? 'bg-amber-100 text-amber-800 border-amber-200' : 'bg-emerald-100 text-emerald-800 border-emerald-200';

                html += `
                    <tr class="hover:bg-slate-50 transition font-medium">
                        <td class="p-3.5 text-center font-mono text-slate-500 font-bold">${stt}</td>
                        <td class="p-3.5 font-bold text-slate-900 leading-relaxed">
                            <a href="${url}" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1.5 font-bold">
                                <span>${name}</span>
                                <i class="fa-solid fa-arrow-up-right-from-square text-[10px] shrink-0 text-blue-500"></i>
                            </a>
                        </td>
                        <td class="p-3.5 font-mono text-slate-600 font-semibold"><code>${gid}</code></td>
                        <td class="p-3.5 font-extrabold text-blue-700">${mem}</td>
                        <td class="p-3.5">
                            <span class="px-2.5 py-0.5 text-[11px] font-bold rounded-lg border ${permColor}">${perm}</span>
                        </td>
                        <td class="p-3.5 font-bold text-slate-700"><span class="px-2 py-0.5 bg-slate-100 text-slate-800 rounded-md border border-slate-200">${cat}</span></td>
                        <td class="p-3.5 text-center">
                            <span class="px-2.5 py-1 text-[11px] font-extrabold bg-emerald-100 text-emerald-800 rounded-full border border-emerald-200 shadow-xs flex items-center justify-center gap-1 mx-auto w-max">
                                <i class="fa-solid fa-circle-check text-emerald-600 text-[10px]"></i>
                                <span>Đã Tham Gia</span>
                            </span>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        }

        function filterFbJoinedGroups() {
            const query = (document.getElementById('fb-group-search-input')?.value || '').toLowerCase().trim();
            if (!query) {
                renderFbJoinedGroupsTable(fbJoinedGroupsList);
                return;
            }

            const filtered = fbJoinedGroupsList.filter(g => {
                const name = (g.group_name || '').toLowerCase();
                const gid = (g.group_id || '').toLowerCase();
                const cat = (g.category || '').toLowerCase();
                const perm = (g.posting_permission || '').toLowerCase();
                return name.includes(query) || gid.includes(query) || cat.includes(query) || perm.includes(query);
            });

            renderFbJoinedGroupsTable(filtered);
        }

        function renderFbTable() {"""

if target_renderfb_marker in content and "function renderFbJoinedGroupsTable" not in content:
    content = content.replace(target_renderfb_marker, new_render_functions)
    print("✅ Added renderFbJoinedGroupsTable and filterFbJoinedGroups JS functions!")

# 5. Add call in DOMContentLoaded
target_dom_marker = "            renderFbTable();"
new_dom_code = """            renderFbTable();
            if (typeof fbJoinedGroupsList !== 'undefined' && fbJoinedGroupsList.length > 0) {
                renderFbJoinedGroupsTable(fbJoinedGroupsList);
            }"""

if target_dom_marker in content and "renderFbJoinedGroupsTable(fbJoinedGroupsList)" not in content:
    content = content.replace(target_dom_marker, new_dom_code, 1)
    print("✅ Added initial call to renderFbJoinedGroupsTable in DOMContentLoaded!")

# Write updated content back to index.html
with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"🎉 Updated {INDEX_PATH} successfully!")
