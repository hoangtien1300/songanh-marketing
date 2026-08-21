# -*- coding: utf-8 -*-
"""
Script to apply 'Update' status badge and notice banner to Facebook Automation tools.
Follows ULTRA-STRICT PRESERVATION RULE.
"""

import sys
from pathlib import Path

INDEX_FILE = Path(r"d:\Song_Anh\marketing_workflow_app\index.html")

BANNER_HTML = """                <!-- Status Notice Banner: Update Phase -->
                <div class="p-4 rounded-2xl bg-gradient-to-r from-amber-500/15 via-amber-500/10 to-orange-500/15 border border-amber-400/40 bg-white/90 backdrop-blur-sm flex items-start md:items-center justify-between gap-4 shadow-sm">
                    <div class="flex items-start md:items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center text-lg font-black shrink-0 shadow-md shadow-amber-500/20">
                            <i class="fa-solid fa-person-digging animate-bounce"></i>
                        </div>
                        <div class="space-y-0.5">
                            <div class="flex items-center gap-2 flex-wrap">
                                <span class="px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-900 text-[11px] font-black uppercase tracking-wider border border-amber-300 flex items-center gap-1.5">
                                    <span class="w-2 h-2 rounded-full bg-amber-500 animate-ping inline-block"></span>
                                    🚧 Trạng Thái: Đang Update (Giao diện &amp; Dàn ý kịch bản)
                                </span>
                            </div>
                            <p class="text-xs font-semibold text-slate-700 leading-relaxed">
                                Hệ thống đang hoàn thiện Backend Stealth Automation Engine. Giao diện hiện tại đóng vai trò là khung điều khiển và cấu hình kịch bản chuẩn B2B.
                            </p>
                        </div>
                    </div>
                    <span class="hidden sm:inline-flex px-3 py-1 rounded-xl bg-amber-200/80 text-amber-900 text-xs font-black shrink-0 border border-amber-300 items-center gap-1.5">
                        <i class="fa-solid fa-code text-amber-700"></i> Backend In-Progress
                    </span>
                </div>
"""

def main():
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Sidebar Navigation
    old_sidebar = """                    <div class="accordion-group rounded-xl border border-purple-200 bg-purple-50/70 overflow-hidden">
                        <button onclick="toggleAccordion('acc-tool-facebook')" class="w-full flex items-center justify-between p-2.5 font-bold text-brand-navy hover:bg-purple-100/80 transition">
                            <div class="flex items-center gap-2">
                                <i class="fa-brands fa-facebook text-blue-600 w-4"></i>
                                <span>📱 Tool Automation Facebook</span>
                            </div>
                            <div class="flex items-center gap-1.5">
                                <span class="text-[9px] px-1.5 py-0.2 rounded bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-extrabold shadow-sm">PRO</span>
                                <i id="icon-acc-tool-facebook" class="fa-solid fa-chevron-down text-purple-500 text-[10px] transition-transform duration-300"></i>
                            </div>
                        </button>
                        
                        <div id="acc-tool-facebook" class="submenu-container open bg-white border-t border-purple-100">
                            <div class="py-1 pl-2">
                                <button onclick="selectModule('fb-auto-friend')" id="sub-fb-auto-friend" class="sub-link w-full text-left px-3 py-1.5 rounded-r-lg text-[11px] font-medium text-slate-600 hover:text-brand-navy hover:bg-purple-50 transition flex items-center justify-between">
                                    <span class="flex items-center gap-1.5"><span>🤝</span> 1. Kết Bạn Tự Động</span>
                                    <span class="text-[9px] px-1.5 py-0.2 rounded bg-blue-100 text-blue-700 font-bold">7 Tools</span>
                                </button>
                                <button onclick="selectModule('fb-auto-engagement')" id="sub-fb-auto-engagement" class="sub-link w-full text-left px-3 py-1.5 rounded-r-lg text-[11px] font-medium text-slate-600 hover:text-brand-navy hover:bg-purple-50 transition flex items-center justify-between">
                                    <span class="flex items-center gap-1.5"><span>⚡</span> 2. Tương Tác Tự Động</span>
                                    <span class="text-[9px] px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 font-bold">8 Tools</span>
                                </button>
                                <button onclick="selectModule('fb-uid-scraper')" id="sub-fb-uid-scraper" class="sub-link w-full text-left px-3 py-1.5 rounded-r-lg text-[11px] font-medium text-slate-600 hover:text-brand-navy hover:bg-purple-50 transition flex items-center justify-between">
                                    <span class="flex items-center gap-1.5"><span>🔍</span> 3. Quét UID Facebook</span>
                                    <span class="text-[9px] px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 font-bold">8 Tools</span>
                                </button>
                                <button onclick="selectModule('fb-fanpage-manager')" id="sub-fb-fanpage-manager" class="sub-link w-full text-left px-3 py-1.5 rounded-r-lg text-[11px] font-medium text-slate-600 hover:text-brand-navy hover:bg-purple-50 transition flex items-center justify-between">
                                    <span class="flex items-center gap-1.5"><span>🏢</span> 4. Hỗ Trợ Fanpage</span>
                                    <span class="text-[9px] px-1.5 py-0.2 rounded bg-purple-100 text-purple-800 font-bold">4 Tools</span>
                                </button>
                                <button onclick="selectModule('fb-facebook-groups')" id="sub-fb-facebook-groups" class="sub-link w-full text-left px-3 py-1.5 rounded-r-lg text-[11px] font-medium text-slate-600 hover:text-brand-navy hover:bg-purple-50 transition flex items-center justify-between">
                                    <span class="flex items-center gap-1.5"><span>🌐</span> 5. Hỗ Trợ Groups</span>
                                    <span class="text-[9px] px-1.5 py-0.2 rounded bg-indigo-100 text-indigo-800 font-bold">5 Tools</span>
                                </button>
                                <button onclick="selectModule('fb-data-backup')" id="sub-fb-data-backup" class="sub-link w-full text-left px-3 py-1.5 rounded-r-lg text-[11px] font-medium text-slate-600 hover:text-brand-navy hover:bg-purple-50 transition flex items-center justify-between">
                                    <span class="flex items-center gap-1.5"><span>💾</span> 6. Backup Dữ Liệu</span>
                                    <span class="text-[9px] px-1.5 py-0.2 rounded bg-rose-100 text-rose-800 font-bold">2 Tools</span>
                                </button>
                            </div>
                        </div>
                    </div>"""

    new_sidebar = """                    <div class="accordion-group rounded-xl border border-purple-200 bg-purple-50/70 overflow-hidden">
                        <button onclick="toggleAccordion('acc-tool-facebook')" class="w-full flex items-center justify-between p-2.5 font-bold text-brand-navy hover:bg-purple-100/80 transition">
                            <div class="flex items-center gap-2">
                                <i class="fa-brands fa-facebook text-blue-600 w-4"></i>
                                <span>📱 Tool Automation Facebook</span>
                            </div>
                            <div class="flex items-center gap-1.5">
                                <span class="text-[9px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300 font-extrabold shadow-sm">Update</span>
                                <span class="text-[9px] px-1.5 py-0.2 rounded bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-extrabold shadow-sm">PRO</span>
                                <i id="icon-acc-tool-facebook" class="fa-solid fa-chevron-down text-purple-500 text-[10px] transition-transform duration-300"></i>
                            </div>
                        </button>
                        
                        <div id="acc-tool-facebook" class="submenu-container open bg-white border-t border-purple-100">
                            <div class="py-1 pl-2">
                                <button onclick="selectModule('fb-auto-friend')" id="sub-fb-auto-friend" class="sub-link w-full text-left px-3 py-1.5 rounded-r-lg text-[11px] font-medium text-slate-600 hover:text-brand-navy hover:bg-purple-50 transition flex items-center justify-between">
                                    <span class="flex items-center gap-1.5"><span>🤝</span> 1. Kết Bạn Tự Động</span>
                                    <div class="flex items-center gap-1">
                                        <span class="text-[8.5px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300 font-extrabold">Update</span>
                                        <span class="text-[9px] px-1.5 py-0.2 rounded bg-blue-100 text-blue-700 font-bold">7 Tools</span>
                                    </div>
                                </button>
                                <button onclick="selectModule('fb-auto-engagement')" id="sub-fb-auto-engagement" class="sub-link w-full text-left px-3 py-1.5 rounded-r-lg text-[11px] font-medium text-slate-600 hover:text-brand-navy hover:bg-purple-50 transition flex items-center justify-between">
                                    <span class="flex items-center gap-1.5"><span>⚡</span> 2. Tương Tác Tự Động</span>
                                    <div class="flex items-center gap-1">
                                        <span class="text-[8.5px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300 font-extrabold">Update</span>
                                        <span class="text-[9px] px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 font-bold">8 Tools</span>
                                    </div>
                                </button>
                                <button onclick="selectModule('fb-uid-scraper')" id="sub-fb-uid-scraper" class="sub-link w-full text-left px-3 py-1.5 rounded-r-lg text-[11px] font-medium text-slate-600 hover:text-brand-navy hover:bg-purple-50 transition flex items-center justify-between">
                                    <span class="flex items-center gap-1.5"><span>🔍</span> 3. Quét UID Facebook</span>
                                    <div class="flex items-center gap-1">
                                        <span class="text-[8.5px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300 font-extrabold">Update</span>
                                        <span class="text-[9px] px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 font-bold">8 Tools</span>
                                    </div>
                                </button>
                                <button onclick="selectModule('fb-fanpage-manager')" id="sub-fb-fanpage-manager" class="sub-link w-full text-left px-3 py-1.5 rounded-r-lg text-[11px] font-medium text-slate-600 hover:text-brand-navy hover:bg-purple-50 transition flex items-center justify-between">
                                    <span class="flex items-center gap-1.5"><span>🏢</span> 4. Hỗ Trợ Fanpage</span>
                                    <div class="flex items-center gap-1">
                                        <span class="text-[8.5px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300 font-extrabold">Update</span>
                                        <span class="text-[9px] px-1.5 py-0.2 rounded bg-purple-100 text-purple-800 font-bold">4 Tools</span>
                                    </div>
                                </button>
                                <button onclick="selectModule('fb-facebook-groups')" id="sub-fb-facebook-groups" class="sub-link w-full text-left px-3 py-1.5 rounded-r-lg text-[11px] font-medium text-slate-600 hover:text-brand-navy hover:bg-purple-50 transition flex items-center justify-between">
                                    <span class="flex items-center gap-1.5"><span>🌐</span> 5. Hỗ Trợ Groups</span>
                                    <div class="flex items-center gap-1">
                                        <span class="text-[8.5px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300 font-extrabold">Update</span>
                                        <span class="text-[9px] px-1.5 py-0.2 rounded bg-indigo-100 text-indigo-800 font-bold">5 Tools</span>
                                    </div>
                                </button>
                                <button onclick="selectModule('fb-data-backup')" id="sub-fb-data-backup" class="sub-link w-full text-left px-3 py-1.5 rounded-r-lg text-[11px] font-medium text-slate-600 hover:text-brand-navy hover:bg-purple-50 transition flex items-center justify-between">
                                    <span class="flex items-center gap-1.5"><span>💾</span> 6. Backup Dữ Liệu</span>
                                    <div class="flex items-center gap-1">
                                        <span class="text-[8.5px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300 font-extrabold">Update</span>
                                        <span class="text-[9px] px-1.5 py-0.2 rounded bg-rose-100 text-rose-800 font-bold">2 Tools</span>
                                    </div>
                                </button>
                            </div>
                        </div>
                    </div>"""

    assert old_sidebar in content, "Sidebar pattern not matched!"
    content = content.replace(old_sidebar, new_sidebar)
    print("✓ Updated Sidebar Navigation with [Update] Badges")

    # 2. Update Panels with Notice Banner & Header Badges
    panels = [
        ("panel-fb-auto-friend", '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-500 text-white shadow-sm">GIAO DIỆN 1</span>', '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-500 text-white shadow-sm">GIAO DIỆN 1</span>\n                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-500/30 text-amber-300 border border-amber-400/50 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span> 🚧 Trạng Thái: Đang Update (Giao diện &amp; Dàn ý kịch bản)</span>'),
        ("panel-fb-auto-engagement", '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-amber-500 text-slate-900 shadow-sm">GIAO DIỆN 2</span>', '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-amber-500 text-slate-900 shadow-sm">GIAO DIỆN 2</span>\n                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-500/30 text-amber-300 border border-amber-400/50 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span> 🚧 Trạng Thái: Đang Update (Giao diện &amp; Dàn ý kịch bản)</span>'),
        ("panel-fb-uid-scraper", '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-emerald-500 text-slate-900 shadow-sm">GIAO DIỆN 3</span>', '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-emerald-500 text-slate-900 shadow-sm">GIAO DIỆN 3</span>\n                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-500/30 text-amber-300 border border-amber-400/50 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span> 🚧 Trạng Thái: Đang Update (Giao diện &amp; Dàn ý kịch bản)</span>'),
        ("panel-fb-fanpage-manager", '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-purple-500 text-white shadow-sm">GIAO DIỆN 4</span>', '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-purple-500 text-white shadow-sm">GIAO DIỆN 4</span>\n                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-500/30 text-amber-300 border border-amber-400/50 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span> 🚧 Trạng Thái: Đang Update (Giao diện &amp; Dàn ý kịch bản)</span>'),
        ("panel-fb-facebook-groups", '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-indigo-500 text-white shadow-sm">GIAO DIỆN 5</span>', '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-indigo-500 text-white shadow-sm">GIAO DIỆN 5</span>\n                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-500/30 text-amber-300 border border-amber-400/50 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span> 🚧 Trạng Thái: Đang Update (Giao diện &amp; Dàn ý kịch bản)</span>'),
        ("panel-fb-data-backup", '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-rose-500 text-white shadow-sm">GIAO DIỆN 6</span>', '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-rose-500 text-white shadow-sm">GIAO DIỆN 6</span>\n                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-500/30 text-amber-300 border border-amber-400/50 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span> 🚧 Trạng Thái: Đang Update (Giao diện &amp; Dàn ý kịch bản)</span>')
    ]

    # For each panel, insert BANNER_HTML right before "<!-- Header Banner -->"
    for pid, old_badge, new_badge in panels:
        # 1. Update Header Badge
        assert old_badge in content, f"Header badge for {pid} not found!"
        content = content.replace(old_badge, new_badge, 1)

    # Insert Notice Banner into each panel
    # We find `<div id="panel-fb-xxx" class="module-panel hidden space-y-6">` and look for the next `<!-- Header Banner -->`
    for pid, _, _ in panels:
        panel_tag = f'<div id="{pid}" class="module-panel hidden space-y-6">'
        assert panel_tag in content, f"Panel tag {pid} not found!"
        
        # Split at panel_tag and find next <!-- Header Banner -->
        p1, p2 = content.split(panel_tag, 1)
        target = "<!-- Header Banner -->"
        assert target in p2, f"<!-- Header Banner --> not found after {pid}!"
        p2_before_header, p2_after_header = p2.split(target, 1)
        
        # Reconstruct
        p2_new = p2_before_header + BANNER_HTML + "\n                " + target + p2_after_header
        content = p1 + panel_tag + p2_new
        print(f"✓ Added Status Notice Banner & Header Badge to #{pid}")

    # 3. Update JavaScript Toast Notifications on Running Tools
    old_run_friend = """        function runFriendToolAction() {
            const accSelect = document.getElementById('friend-acc-select');
            const accName = accSelect ? accSelect.options[accSelect.selectedIndex].text.split('(')[0].trim() : 'Song Anh Profile';
            const delayMin = document.getElementById('friend-delay-min').value || 30;
            const delayMax = document.getElementById('friend-delay-max').value || 60;
            const maxCount = document.getElementById('friend-max-count').value || 40;

            const nowStr = new Date().toTimeString().split(' ')[0];
            const term = document.getElementById('friend-terminal');
            if (term) {
                const div = document.createElement('div');
                div.className = 'text-emerald-400 font-bold';
                div.innerText = `[${nowStr}] [RUNNING] Kích hoạt kết bạn tự động trên '${accName}' (${maxCount} lượt, delay ${delayMin}-${delayMax}s, Bezier Trajectory).`;
                term.prepend(div);
            }

            const kpiSent = document.getElementById('kpi-friend-sent');
            if (kpiSent) {
                kpiSent.innerText = parseInt(kpiSent.innerText.replace(/,/g, '')) + 1;
            }

            showToast(`🤝 Đã kích hoạt Kết Bạn Tự Động trên ${accName}! Hệ thống đang chạy an toàn.`);
        }"""

    new_run_friend = """        function runFriendToolAction() {
            const accSelect = document.getElementById('friend-acc-select');
            const accName = accSelect ? accSelect.options[accSelect.selectedIndex].text.split('(')[0].trim() : 'Song Anh Profile';
            const delayMin = document.getElementById('friend-delay-min').value || 30;
            const delayMax = document.getElementById('friend-delay-max').value || 60;
            const maxCount = document.getElementById('friend-max-count').value || 40;

            const nowStr = new Date().toTimeString().split(' ')[0];
            const term = document.getElementById('friend-terminal');
            if (term) {
                const div = document.createElement('div');
                div.className = 'text-amber-400 font-bold';
                div.innerText = `[${nowStr}] [UPDATE PHASE] Cấu hình kết bạn '${accName}' (${maxCount} lượt, delay ${delayMin}-${delayMax}s) đã được ghi nhận. Backend Stealth Engine đang được hoàn thiện.`;
                term.prepend(div);
            }

            showToast("🚧 Tính năng đang trong giai đoạn Update & hoàn thiện Backend Stealth Engine!");
        }"""

    assert old_run_friend in content, "old_run_friend not found!"
    content = content.replace(old_run_friend, new_run_friend)

    old_revoke = """        function revokePendingRequests() {
            showToast("🚫 Đang quét và tự động hủy 45 lời mời kết bạn đã treo quá 14 ngày...");
            const kpiPending = document.getElementById('kpi-friend-pending');
            if (kpiPending) kpiPending.innerText = "0";
        }"""
    new_revoke = """        function revokePendingRequests() {
            showToast("🚧 Tính năng đang trong giai đoạn Update & hoàn thiện Backend Stealth Engine!");
        }"""
    assert old_revoke in content, "old_revoke not found!"
    content = content.replace(old_revoke, new_revoke)

    old_accept = """        function acceptAllRequests() {
            showToast("✅ Đã tự động chấp nhận các lời mời kết bạn đủ điều kiện B2B!");
            const kpiAccepted = document.getElementById('kpi-friend-accepted');
            if (kpiAccepted) {
                kpiAccepted.innerText = parseInt(kpiAccepted.innerText.replace(/,/g, '')) + 12;
            }
        }"""
    new_accept = """        function acceptAllRequests() {
            showToast("🚧 Tính năng đang trong giai đoạn Update & hoàn thiện Backend Stealth Engine!");
        }"""
    assert old_accept in content, "old_accept not found!"
    content = content.replace(old_accept, new_accept)

    old_run_engage = """        function runEngageToolAction() {
            const input = document.getElementById('engage-spintax-input');
            const spunSample = parseSpintax(input ? input.value : "Tương tác Song Anh");
            const nowStr = new Date().toTimeString().split(' ')[0];

            const tbody = document.getElementById('table-fb-engage-body');
            if (tbody) {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-50 transition';
                tr.innerHTML = `
                    <td class="p-2 font-mono text-[11px] text-slate-500">${nowStr}</td>
                    <td class="p-2 font-bold text-slate-800">⚡ Auto Comment/React</td>
                    <td class="p-2 text-slate-600 truncate max-w-[120px]">${spunSample.substring(0, 30)}...</td>
                    <td class="p-2"><span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">Thành công</span></td>
                `;
                tbody.prepend(tr);
            }

            const kpiReact = document.getElementById('kpi-engage-react');
            if (kpiReact) kpiReact.innerText = parseInt(kpiReact.innerText.replace(/,/g, '')) + 1;

            showToast("⚡ Đã kích hoạt Tương Tác Tự Động (Spintax Live Engine)!");
        }"""

    new_run_engage = """        function runEngageToolAction() {
            showToast("🚧 Tính năng đang trong giai đoạn Update & hoàn thiện Backend Stealth Engine!");
        }"""
    assert old_run_engage in content, "old_run_engage not found!"
    content = content.replace(old_run_engage, new_run_engage)

    old_run_uid = """        function runUidScraperAction() {
            const target = document.getElementById('uid-scrape-target').value;
            const input = document.getElementById('uid-target-input').value;
            showToast(`🔍 Đang cào dữ liệu UID từ [${target}] '${input}'...`);

            setTimeout(() => {
                const totalElem = document.getElementById('uid-result-total');
                if (totalElem) totalElem.innerText = "18 UIDs Mới";
                showToast("✅ Đã cào thành công 18 UIDs B2B mới nhất!");
            }, 1200);
        }"""

    new_run_uid = """        function runUidScraperAction() {
            showToast("🚧 Tính năng đang trong giai đoạn Update & hoàn thiện Backend Stealth Engine!");
        }"""
    assert old_run_uid in content, "old_run_uid not found!"
    content = content.replace(old_run_uid, new_run_uid)

    old_run_page = """        function runFanpageToolAction() {
            const pageSelect = document.getElementById('fanpage-target-select');
            const pageName = pageSelect ? pageSelect.options[pageSelect.selectedIndex].text.split('(')[0].trim() : 'Fanpage Song Anh';
            showToast(`🏢 Đã kích hoạt chiến dịch trên ${pageName}!`);
        }"""
    new_run_page = """        function runFanpageToolAction() {
            showToast("🚧 Tính năng đang trong giai đoạn Update & hoàn thiện Backend Stealth Engine!");
        }"""
    assert old_run_page in content, "old_run_page not found!"
    content = content.replace(old_run_page, new_run_page)

    old_run_grp = """        function runGroupToolAction() {
            showToast("🌐 Đã kích hoạt chiến dịch Đăng Bài / Seeding Nhóm Facebook!");
        }"""
    new_run_grp = """        function runGroupToolAction() {
            showToast("🚧 Tính năng đang trong giai đoạn Update & hoàn thiện Backend Stealth Engine!");
        }"""
    assert old_run_grp in content, "old_run_grp not found!"
    content = content.replace(old_run_grp, new_run_grp)

    old_run_bak = """        function runBackupToolAction() {
            showToast("💾 Đang tiến hành tạo gói sao lưu dữ liệu toàn diện...");
            setTimeout(() => {
                showToast("🎉 Đã tạo bản Backup an toàn thành công (128 MB)!");
            }, 1500);
        }"""
    new_run_bak = """        function runBackupToolAction() {
            showToast("🚧 Tính năng đang trong giai đoạn Update & hoàn thiện Backend Stealth Engine!");
        }"""
    assert old_run_bak in content, "old_run_bak not found!"
    content = content.replace(old_run_bak, new_run_bak)

    print("✓ Updated Tool Action Functions to trigger Update Phase Toast")

    # Write back to index.html
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✓ All updates applied successfully to {INDEX_FILE}!")

if __name__ == "__main__":
    main()
