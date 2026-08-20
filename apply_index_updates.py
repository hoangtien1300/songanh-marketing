# -*- coding: utf-8 -*-
"""
Script to safely update index.html with Facebook Groups Channel Switcher (Fanpage vs Profile)
File: apply_index_updates.py
Author: song_anh_code_expert
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INDEX_PATH = r"d:\Song_Anh\marketing_workflow_app\index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Target HTML Replacement
old_header_html = """                <!-- 🌟 BẢNG DANH SÁCH FACEBOOK GROUPS ĐÃ THAM GIA (FANPAGE MÔ HÌNH KIẾN TRÚC SONG ANH) -->
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
                            <select id="fb-group-category-filter" onchange="filterFbJoinedGroups()" class="px-3 py-1.5 text-xs font-medium border border-slate-300 rounded-xl bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700 cursor-pointer">
                                <option value="">Tất cả lĩnh vực</option>
                                <option value="📐 Kiến trúc & Quy hoạch">📐 Kiến trúc & Quy hoạch</option>
                                <option value="🏢 Chủ đầu tư & BQL Dự án BĐS">🏢 Chủ đầu tư & BQL Dự án BĐS</option>
                                <option value="🏗️ Thi công & Nhà thầu">🏗️ Thi công & Nhà thầu</option>
                                <option value="🏭 KCN & Kho xưởng">🏭 KCN & Kho xưởng</option>
                                <option value="🧩 Mô hình chuyên ngành">🧩 Mô hình chuyên ngành</option>
                            </select>
                            <input type="text" id="fb-group-search-input" onkeyup="filterFbJoinedGroups()" placeholder="🔍 Tìm tên group, ID, lĩnh vực..." class="px-3 py-1.5 text-xs font-medium border border-slate-300 rounded-xl bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-56">
                            <a href="fanpage_joined_groups.json" target="_blank" download class="px-3 py-1.5 text-xs font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-xl transition flex items-center gap-1">
                                <i class="fa-solid fa-file-code"></i> JSON
                            </a>
                            <a href="fanpage_joined_groups.xlsx" download class="px-3 py-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-xl transition flex items-center gap-1">
                                <i class="fa-solid fa-file-excel"></i> Excel Report
                            </a>
                        </div>
                    </div>"""

new_header_html = """                <!-- 🌟 BẢNG DANH SÁCH FACEBOOK GROUPS ĐÃ THAM GIA (FANPAGE MÔ HÌNH KIẾN TRÚC SONG ANH & PROFILE SONG ANH) -->
                <div class="light-card rounded-2xl p-5 border border-slate-200 space-y-4 shadow-sm">
                    <div class="flex flex-col md:flex-row items-start md:items-center justify-between border-b border-slate-200 pb-3 gap-3">
                        <div class="flex items-center gap-2">
                            <i class="fa-solid fa-users-rectangle text-blue-600 text-base"></i>
                            <div>
                                <h3 id="fb-groups-section-title" class="font-heading font-bold text-sm text-slate-900">Danh Sách Facebook Groups Fanpage Đã Tham Gia</h3>
                                <p id="fb-groups-section-subtitle" class="text-[11px] text-slate-500 font-medium">Báo cáo tự động từ Playwright Stealth &amp; Facebook Graph API Engine (Fanpage Mô hình Song Anh)</p>
                            </div>
                        </div>
                        <div class="flex flex-wrap items-center gap-2 w-full md:w-auto">
                            <!-- 🌟 KÊNH TỰ ĐỘNG BỘ LỌC GROUPS SWITCHER -->
                            <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-inner">
                                <button id="btn-group-channel-fanpage" onclick="switchFbGroupChannel('fanpage')" class="px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-600 text-white transition shadow-sm flex items-center gap-1.5 cursor-pointer">
                                    <i class="fa-solid fa-flag text-[10px]"></i> Fanpage Mô hình Song Anh (170 Groups)
                                </button>
                                <button id="btn-group-channel-profile" onclick="switchFbGroupChannel('profile')" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-blue-700 transition bg-transparent flex items-center gap-1.5 cursor-pointer">
                                    <i class="fa-solid fa-user-gear text-[10px]"></i> Profile Song Anh (<span id="profile-group-count-span">911</span> Groups)
                                </button>
                            </div>

                            <span id="fb-joined-groups-count-badge" class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1.5 rounded-xl border border-emerald-200">170 Groups Active</span>
                            <select id="fb-group-category-filter" onchange="filterFbJoinedGroups()" class="px-3 py-1.5 text-xs font-medium border border-slate-300 rounded-xl bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700 cursor-pointer">
                                <option value="">Tất cả lĩnh vực</option>
                                <option value="📐 Kiến trúc & Quy hoạch">📐 Kiến trúc & Quy hoạch</option>
                                <option value="🏢 Chủ đầu tư & BQL Dự án BĐS">🏢 Chủ đầu tư & BQL Dự án BĐS</option>
                                <option value="🏗️ Thi công & Nhà thầu">🏗️ Thi công & Nhà thầu</option>
                                <option value="🏭 KCN & Kho xưởng">🏭 KCN & Kho xưởng</option>
                                <option value="🧩 Mô hình chuyên ngành">🧩 Mô hình chuyên ngành</option>
                            </select>
                            <input type="text" id="fb-group-search-input" onkeyup="filterFbJoinedGroups()" placeholder="🔍 Tìm tên group, ID, lĩnh vực..." class="px-3 py-1.5 text-xs font-medium border border-slate-300 rounded-xl bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-56">
                            <a id="btn-dl-groups-json" href="fanpage_joined_groups.json" target="_blank" download class="px-3 py-1.5 text-xs font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-xl transition flex items-center gap-1">
                                <i class="fa-solid fa-file-code"></i> JSON
                            </a>
                            <a id="btn-dl-groups-excel" href="fanpage_joined_groups.xlsx" download class="px-3 py-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-xl transition flex items-center gap-1">
                                <i class="fa-solid fa-file-excel"></i> Excel Report
                            </a>
                        </div>
                    </div>"""

if old_header_html in content:
    content = content.replace(old_header_html, new_header_html)
    print("✅ Successfully updated HTML Header with Channel Switcher tab bar!")
else:
    print("[WARN] old_header_html not found!")

# 2. Target JS Variables
old_js_vars = "        let fbJoinedGroupsList = [];"
new_js_vars = """        let currentFbGroupChannel = 'fanpage';
        let fanpageJoinedGroupsList = [];
        let profileJoinedGroupsList = [];
        let fbJoinedGroupsList = [];"""

if old_js_vars in content and "let currentFbGroupChannel" not in content:
    content = content.replace(old_js_vars, new_js_vars)
    print("✅ Successfully updated JS state variables!")

# 3. Target JS Central API Data Load
old_js_load = """                if (data.fanpage_joined_groups && data.fanpage_joined_groups.length > 0) {
                    fbJoinedGroupsList = data.fanpage_joined_groups;
                    renderFbJoinedGroupsTable(fbJoinedGroupsList);
                }"""

new_js_load = """                if (data.fanpage_joined_groups && data.fanpage_joined_groups.length > 0) {
                    fanpageJoinedGroupsList = data.fanpage_joined_groups;
                }
                if (data.profile_joined_groups && data.profile_joined_groups.length > 0) {
                    profileJoinedGroupsList = data.profile_joined_groups;
                    const spanProf = document.getElementById('profile-group-count-span');
                    if (spanProf) spanProf.innerText = profileJoinedGroupsList.length;
                }
                switchFbGroupChannel(currentFbGroupChannel);"""

if old_js_load in content:
    content = content.replace(old_js_load, new_js_load)
    print("✅ Successfully updated Central API Data Load logic!")

# 4. Target JS switchFbGroupChannel function addition
switch_fn_code = """        function switchFbGroupChannel(channelKey) {
            currentFbGroupChannel = channelKey;
            const btnFanpage = document.getElementById('btn-group-channel-fanpage');
            const btnProfile = document.getElementById('btn-group-channel-profile');
            const titleElem = document.getElementById('fb-groups-section-title');
            const subTitleElem = document.getElementById('fb-groups-section-subtitle');
            const jsonBtn = document.getElementById('btn-dl-groups-json');
            const excelBtn = document.getElementById('btn-dl-groups-excel');

            if (channelKey === 'fanpage') {
                if (btnFanpage) btnFanpage.className = "px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-600 text-white transition shadow-sm flex items-center gap-1.5 cursor-pointer";
                if (btnProfile) btnProfile.className = "px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-blue-700 transition bg-transparent flex items-center gap-1.5 cursor-pointer";
                if (titleElem) titleElem.innerText = "Danh Sách Facebook Groups Fanpage Đã Tham Gia";
                if (subTitleElem) subTitleElem.innerText = "Báo cáo tự động từ Playwright Stealth & Facebook Graph API Engine (Fanpage Mô hình Song Anh)";
                if (jsonBtn) jsonBtn.setAttribute('href', 'fanpage_joined_groups.json');
                if (excelBtn) excelBtn.setAttribute('href', 'fanpage_joined_groups.xlsx');
                fbJoinedGroupsList = fanpageJoinedGroupsList.length > 0 ? fanpageJoinedGroupsList : fbJoinedGroupsList;
            } else {
                if (btnProfile) btnProfile.className = "px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-600 text-white transition shadow-sm flex items-center gap-1.5 cursor-pointer";
                if (btnFanpage) btnFanpage.className = "px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-blue-700 transition bg-transparent flex items-center gap-1.5 cursor-pointer";
                if (titleElem) titleElem.innerText = "Danh Sách Facebook Groups Profile Song Anh Đã Tham Gia";
                if (subTitleElem) subTitleElem.innerText = "Báo cáo tự động từ Playwright Stealth & Facebook Profile Song Anh Engine";
                if (jsonBtn) jsonBtn.setAttribute('href', 'profile_joined_groups.json');
                if (excelBtn) excelBtn.setAttribute('href', 'profile_joined_groups.xlsx');
                fbJoinedGroupsList = profileJoinedGroupsList.length > 0 ? profileJoinedGroupsList : fbJoinedGroupsList;
            }

            filterFbJoinedGroups();
        }

"""

if "function switchFbGroupChannel" not in content:
    target_render_fn = "        function renderFbJoinedGroupsTable(groupsData) {"
    if target_render_fn in content:
        content = content.replace(target_render_fn, switch_fn_code + target_render_fn)
        print("✅ Successfully inserted switchFbGroupChannel JS function!")

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 Finished updating index.html!")
