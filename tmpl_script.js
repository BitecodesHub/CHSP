// ===== CONSTANTS =====
const DK = [
    { key: 'Initial Assessment - Allied Health', sh: 'Assessment', co: '#5b6cf7' },
    { key: 'Care Plan Allied Health', sh: 'Care Plan', co: '#22c9b0' },
    { key: 'Support Plan From My Aged Care Portal - Allied Health - CHSP', sh: 'Support Plan', co: '#10b981' },
    { key: 'Site Inspection Report', sh: 'Site Report', co: '#f59e0b' }
];
const PK = 'Person Responsible For CHSP - AH Physiotherapy KPIs';
const AC = ['#5b6cf7', '#22c9b0', '#ec4899', '#10b981', '#f59e0b', '#3b82f6', '#e17055', '#a855f7', '#06b6d4', '#f472b6'];

// ===== HELPERS =====
function has(r, k) { var v = r[k]; return v !== '' && v !== null && v !== undefined }
function dc(r) { var c = 0; for (var i = 0; i < DK.length; i++) { if (has(r, DK[i].key)) c++ } return c }
function mc(r) { return 4 - dc(r) }
function gp(r) { return has(r, PK) ? r[PK] : '' }
function fn(r) { return ((r['Legal First Name'] || '') + ' ' + (r['Last Name'] || '')).trim() }
function riskLvl(r) { var m = mc(r), u = !gp(r); if (m >= 3 || (m >= 2 && u)) return 'high'; if (m >= 1) return 'medium'; return 'low' }

// ===== COMPUTED =====
var N = DATA.length;
var compl = 0, totalDocs = 0, unasn = 0;
var dCounts = [0, 0, 0, 0];
var pMap = {};
for (var i = 0; i < N; i++) {
    var r = DATA[i], d = dc(r);
    totalDocs += d;
    if (d === 4) compl++;
    if (!gp(r)) unasn++;
    for (var j = 0; j < 4; j++) { if (has(r, DK[j].key)) dCounts[j]++ }
    var p = gp(r) || 'Unassigned';
    if (!pMap[p]) pMap[p] = [];
    pMap[p].push(r);
}
var pend = N - compl;
var asgn = N - unasn;
var dS = DK.map(function (d, i) { return { sh: d.sh, key: d.key, co: d.co, f: dCounts[i], e: N - dCounts[i] } });
var pNames = Object.keys(pMap).filter(function (p) { return p !== 'Unassigned' }).sort();

// ===== NAV =====
function go(n, b) {
    var secs = document.querySelectorAll('.sec'); for (var i = 0; i < secs.length; i++)secs[i].classList.remove('active');
    document.getElementById('s-' + n).classList.add('active');
    if (b) { var bs = document.querySelectorAll('.nbtn'); for (var i = 0; i < bs.length; i++)bs[i].classList.remove('active'); b.classList.add('active') }
    if (n === 'pending') rPnd(); if (n === 'complete') rCmp(); if (n === 'alldata') rAll();
    if (n === 'risk') initRisk(); if (n === 'heatmap') initHM(); if (n === 'gaps') initGaps();
    if (n === 'workload') initWL(); if (n === 'trends') initTrends();
    document.querySelector('.sidebar').classList.remove('open');
}

// ===== KPIs =====
function renderKPIs() {
    var crit = 0; for (var i = 0; i < N; i++) { if (mc(DATA[i]) >= 3) crit++ }
    var avgPct = ((totalDocs / (N * 4)) * 100).toFixed(1);
    var ks = [
        { lb: 'Total Records', v: N.toLocaleString(), s: 'In dataset', dot: '#5b6cf7' },
        { lb: 'Fully Complete', v: compl.toLocaleString(), s: '<span class="tag tg">' + (compl / N * 100).toFixed(1) + '%</span>', dot: '#10b981' },
        { lb: 'Pending', v: pend.toLocaleString(), s: '<span class="tag ' + (pend > N * .3 ? 'tr' : 'tw') + '">' + (pend / N * 100).toFixed(1) + '% need action</span>', dot: '#f59e0b' },
        { lb: 'Assigned', v: asgn.toLocaleString(), s: pNames.length + ' people', dot: '#22c9b0' },
        { lb: 'Unassigned', v: unasn.toLocaleString(), s: '<span class="tag ' + (unasn > 100 ? 'tr' : 'tw') + '">' + (unasn / N * 100).toFixed(1) + '%</span>', dot: '#ef4444' },
        { lb: 'Critical (3+ missing)', v: crit.toLocaleString(), s: '<span class="tag tr">Needs review</span>', dot: '#ef4444' },
        { lb: 'Avg Completion', v: avgPct + '%', s: '<span class="tag ' + (avgPct >= 80 ? 'tg' : avgPct >= 50 ? 'tw' : 'tr') + '">Per record avg</span>', dot: '#3b82f6' },
        { lb: 'Documents Filed', v: totalDocs.toLocaleString(), s: 'of ' + (N * 4).toLocaleString() + ' required', dot: '#a855f7' }
    ];
    document.getElementById('kG').innerHTML = ks.map(function (k) { return '<div class="kpi"><div class="kpi-top"><span class="kpi-lb">' + k.lb + '</span><span class="kpi-dot" style="background:' + k.dot + '"></span></div><div class="kpi-v">' + k.v + '</div><div class="kpi-s">' + k.s + '</div></div>' }).join('');
}

// ===== STATUS BARS =====
function renderSBars() {
    document.getElementById('sBars').innerHTML = dS.map(function (d) {
        var p = (d.f / N * 100).toFixed(1); var c = p >= 80 ? 'var(--green)' : p >= 50 ? 'var(--amber)' : 'var(--red)';
        return '<div class="sbi"><span class="sb-l">' + d.sh + '</span><div class="sb-t"><div class="sb-f" style="width:' + p + '%;background:' + c + '"></div></div><span class="sb-p" style="color:' + c + '">' + p + '%</span><span class="sb-c">' + d.f + '/' + N + '</span></div>';
    }).join('');
}

// ===== CHARTS =====
Chart.defaults.color = '#8b90a5'; Chart.defaults.borderColor = 'rgba(255,255,255,0.04)'; Chart.defaults.font.family = 'Inter';
var _ch = {};
function mkCh(id, cfg) { if (_ch[id]) _ch[id].destroy(); _ch[id] = new Chart(document.getElementById(id), cfg) }

function renderOvCharts() {
    mkCh('ch1', { type: 'bar', data: { labels: dS.map(function (d) { return d.sh }), datasets: [{ label: 'Filed', data: dS.map(function (d) { return d.f }), backgroundColor: dS.map(function (d) { return d.co + 'cc' }), borderRadius: 6, borderSkipped: false }, { label: 'Missing', data: dS.map(function (d) { return d.e }), backgroundColor: 'rgba(239,68,68,0.3)', borderRadius: 6, borderSkipped: false }] }, options: { responsive: true, plugins: { legend: { labels: { boxWidth: 12, padding: 14 } } }, scales: { x: { stacked: true, grid: { display: false } }, y: { stacked: true, beginAtZero: true } } } });

    var partial = 0, critical = 0;
    for (var i = 0; i < N; i++) { var m = mc(DATA[i]); if (m >= 3) critical++; else if (m >= 1) partial++ }
    mkCh('ch2', { type: 'doughnut', data: { labels: ['Complete (4/4)', 'Partial (1-2 missing)', 'Critical (3+ missing)'], datasets: [{ data: [compl, partial, critical], backgroundColor: ['rgba(16,185,129,0.7)', 'rgba(245,158,11,0.7)', 'rgba(239,68,68,0.7)'], borderWidth: 0, hoverOffset: 6 }] }, options: { responsive: true, cutout: '55%', plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 12 } } } } });

    var allP = pNames.slice(); if (pMap['Unassigned']) allP.push('Unassigned');
    mkCh('ch3', { type: 'bar', data: { labels: allP.map(function (l) { return l.length > 18 ? l.substring(0, 16) + '…' : l }), datasets: [{ label: 'Records', data: allP.map(function (p) { return (pMap[p] || []).length }), backgroundColor: allP.map(function (_, i) { return AC[i % AC.length] + 'cc' }), borderRadius: 6, borderSkipped: false }] }, options: { responsive: true, indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } } } } });

    mkCh('ch4', { type: 'polarArea', data: { labels: DK.map(function (d) { return d.sh }), datasets: [{ data: DK.map(function (d) { var c = 0; for (var i = 0; i < N; i++) { if (!has(DATA[i], d.key)) c++ } return c }), backgroundColor: ['rgba(91,108,247,0.4)', 'rgba(34,201,176,0.4)', 'rgba(16,185,129,0.4)', 'rgba(245,158,11,0.4)'] }] }, options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { boxWidth: 10 } } } } });
}

// ===== PERSON CARDS =====
function renderPCards() {
    var allP = pNames.slice(); if (pMap['Unassigned']) allP.push('Unassigned');
    document.getElementById('pGrid').innerHTML = allP.map(function (p, i) {
        var recs = pMap[p] || []; var cm = 0; for (var j = 0; j < recs.length; j++) { if (dc(recs[j]) === 4) cm++ } var pd = recs.length - cm;
        var ini = p === 'Unassigned' ? '—' : p.split(' ').map(function (w) { return w[0] }).join('').substring(0, 2).toUpperCase();
        var co = AC[i % AC.length];
        return '<div class="pc" onclick="fperson(\'' + p.replace(/'/g, "\\'") + '\')">'
            + '<div class="pc-h"><div class="pc-av" style="background:' + co + '18;color:' + co + '">' + ini + '</div>'
            + '<div><div class="pc-nm">' + p + '</div><div class="pc-ct">' + recs.length + ' record' + (recs.length !== 1 ? 's' : '') + '</div></div></div>'
            + '<div class="pc-sts">'
            + '<div class="pc-st"><div class="pc-sv" style="color:var(--green)">' + cm + '</div><div class="pc-sl">Complete</div></div>'
            + '<div class="pc-st"><div class="pc-sv" style="color:var(--red)">' + pd + '</div><div class="pc-sl">Pending</div></div>'
            + '<div class="pc-st"><div class="pc-sv" style="color:var(--accentL)">' + (recs.length ? ((cm / recs.length) * 100).toFixed(0) : 0) + '%</div><div class="pc-sl">Rate</div></div>'
            + '</div></div>';
    }).join('');
    document.getElementById('ncPpl').textContent = allP.length;
}
function fperson(n) {
    go('alldata', null);
    document.getElementById('aP').value = n === 'Unassigned' ? '__un__' : n;
    rAll();
    var bs = document.querySelectorAll('.nbtn'); for (var i = 0; i < bs.length; i++)bs[i].classList.remove('active');
    bs[bs.length - 1].classList.add('active');
}

// ===== TABLE BUILDER =====
if (!window._ps) window._ps = {};
function bTbl(recs, cid, pk) {
    if (!window._ps[pk]) window._ps[pk] = { p: 1 }; var st = window._ps[pk]; var pp = 30;
    var tp = Math.max(1, Math.ceil(recs.length / pp)); if (st.p > tp) st.p = 1;
    var s = (st.p - 1) * pp; var pd = recs.slice(s, s + pp);
    var h = '<div class="tc"><div class="tt"><h3>Records</h3><span class="rc">' + recs.length + ' result' + (recs.length !== 1 ? 's' : '') + '</span></div><div class="ts"><table><thead><tr><th>UID</th><th>SID</th><th>Name</th><th>Person Responsible</th><th>Assessment</th><th>Care Plan</th><th>Support Plan</th><th>Site Report</th><th>Missing</th><th>Risk</th></tr></thead><tbody>';
    for (var i = 0; i < pd.length; i++) {
        var r = pd[i]; var m = mc(r); var rl = riskLvl(r); var rc = m === 0 ? 'rok' : m >= 3 ? 'rng' : ''; var pr = gp(r);
        h += '<tr class="' + rc + '"><td class="uid-c">' + r.UID + '</td><td>' + r.SID + '</td><td class="nm-c">' + fn(r) + '</td><td class="' + (pr ? 'pr-c' : 'pr-c un') + '">' + (pr || 'Unassigned') + '</td>';
        for (var j = 0; j < DK.length; j++) { var ok = has(r, DK[j].key); h += '<td><span class="sp ' + (ok ? 'ok' : 'ng') + '"><span class="dt"></span>' + (ok ? 'Filed' : 'Missing') + '</span></td>' }
        h += '<td style="font-weight:600;color:' + (m === 0 ? 'var(--green)' : 'var(--red)') + '">' + (m === 0 ? 'None' : m + '/4') + '</td>';
        h += '<td><span class="risk-badge risk-' + (rl === 'high' ? 'hi' : rl === 'medium' ? 'md' : 'lo') + '">' + (rl === 'high' ? 'High' : rl === 'medium' ? 'Medium' : 'Low') + '</span></td></tr>';
    }
    h += '</tbody></table></div><div class="pn"><span class="pi">' + Math.min(s + 1, recs.length) + '–' + Math.min(s + pp, recs.length) + ' of ' + recs.length + '</span><div class="pbs">';
    h += '<button class="pb" onclick="window._ps[\'' + pk + '\'].p--;' + pk + 'R()" ' + (st.p <= 1 ? 'disabled' : '') + '>Prev</button>';
    var ps = Math.max(1, st.p - 2), pe = Math.min(tp, ps + 4); if (pe - ps < 4) ps = Math.max(1, pe - 4);
    for (var i = ps; i <= pe; i++)h += '<button class="pb ' + (i === st.p ? 'active' : '') + '" onclick="window._ps[\'' + pk + '\'].p=' + i + ';' + pk + 'R()">' + i + '</button>';
    h += '<button class="pb" onclick="window._ps[\'' + pk + '\'].p++;' + pk + 'R()" ' + (st.p >= tp ? 'disabled' : '') + '>Next</button></div></div></div>';
    document.getElementById(cid).innerHTML = h;
}

// ===== ALL DATA =====
function rAll() {
    var f = DATA.slice(); var s = (document.getElementById('aS') || {}).value || ''; s = s.toLowerCase();
    var pf = (document.getElementById('aP') || {}).value || '';
    var sf = (document.getElementById('aSt') || {}).value || '';
    var so = (document.getElementById('aSo') || {}).value || 'uid-d';
    if (s) f = f.filter(function (r) { return fn(r).toLowerCase().indexOf(s) >= 0 || String(r.UID).indexOf(s) >= 0 || String(r.SID).indexOf(s) >= 0 });
    if (pf === '__un__') f = f.filter(function (r) { return !gp(r) }); else if (pf) f = f.filter(function (r) { return gp(r) === pf });
    if (sf === 'c') f = f.filter(function (r) { return dc(r) === 4 }); else if (sf === 'p') f = f.filter(function (r) { var m = mc(r); return m >= 1 && m <= 2 }); else if (sf === 'x') f = f.filter(function (r) { return mc(r) >= 3 });
    var parts = so.split('-'); var sk = parts[0], sd = parts[1];
    f.sort(function (a, b) { var va, vb; if (sk === 'uid') { va = a.UID; vb = b.UID } else if (sk === 'nm') { va = fn(a).toLowerCase(); vb = fn(b).toLowerCase() } else { va = mc(a); vb = mc(b) } if (va < vb) return sd === 'a' ? -1 : 1; if (va > vb) return sd === 'a' ? 1 : -1; return 0 });
    bTbl(f, 'aTbl', 'at');
}
window.atR = rAll;

function rPnd() {
    var f = []; for (var i = 0; i < N; i++) { if (dc(DATA[i]) < 4) f.push(DATA[i]) }
    var s = ((document.getElementById('pnS') || {}).value || '').toLowerCase();
    var df = (document.getElementById('pnD') || {}).value;
    var pf = (document.getElementById('pnP') || {}).value || '';
    if (s) f = f.filter(function (r) { return fn(r).toLowerCase().indexOf(s) >= 0 || String(r.UID).indexOf(s) >= 0 });
    if (df !== '') { var di = parseInt(df); f = f.filter(function (r) { return !has(r, DK[di].key) }) }
    if (pf === '__un__') f = f.filter(function (r) { return !gp(r) }); else if (pf) f = f.filter(function (r) { return gp(r) === pf });
    bTbl(f, 'pnTbl', 'pn');
}
window.pnR = rPnd;

function rCmp() {
    var f = []; for (var i = 0; i < N; i++) { if (dc(DATA[i]) === 4) f.push(DATA[i]) }
    var s = ((document.getElementById('cmS') || {}).value || '').toLowerCase();
    if (s) f = f.filter(function (r) { return fn(r).toLowerCase().indexOf(s) >= 0 || String(r.UID).indexOf(s) >= 0 });
    bTbl(f, 'cmTbl', 'cm');
}
window.cmR = rCmp;

// ===== RISK ASSESSMENT =====
var _riskInit = false;
function initRisk() {
    var hi = [], md = [], lo = [];
    for (var i = 0; i < N; i++) { var rl = riskLvl(DATA[i]); if (rl === 'high') hi.push(DATA[i]); else if (rl === 'medium') md.push(DATA[i]); else lo.push(DATA[i]) }
    var riskScore = ((hi.length * 3 + md.length) / (N * 3) * 100).toFixed(1);
    document.getElementById('riskKpi').innerHTML = [
        { lb: 'High Risk', v: hi.length, s: '<span class="tag tr">' + (hi.length / N * 100).toFixed(1) + '%</span>', dot: '#ef4444' },
        { lb: 'Medium Risk', v: md.length, s: '<span class="tag tw">' + (md.length / N * 100).toFixed(1) + '%</span>', dot: '#f59e0b' },
        { lb: 'Low Risk (Complete)', v: lo.length, s: '<span class="tag tg">' + (lo.length / N * 100).toFixed(1) + '%</span>', dot: '#10b981' },
        { lb: 'Weighted Risk Score', v: riskScore + '%', s: 'Lower is better', dot: '#a855f7' },
    ].map(function (k) { return '<div class="kpi"><div class="kpi-top"><span class="kpi-lb">' + k.lb + '</span><span class="kpi-dot" style="background:' + k.dot + '"></span></div><div class="kpi-v">' + k.v + '</div><div class="kpi-s">' + k.s + '</div></div>' }).join('');

    if (!_riskInit) {
        mkCh('riskCh1', { type: 'doughnut', data: { labels: ['High', 'Medium', 'Low'], datasets: [{ data: [hi.length, md.length, lo.length], backgroundColor: ['rgba(239,68,68,0.7)', 'rgba(245,158,11,0.7)', 'rgba(16,185,129,0.7)'], borderWidth: 0 }] }, options: { responsive: true, cutout: '55%', plugins: { legend: { position: 'bottom', labels: { boxWidth: 10 } } } } });
        var allP = pNames.slice(); allP.push('Unassigned');
        mkCh('riskCh2', {
            type: 'bar', data: {
                labels: allP.map(function (p) { return p.length > 16 ? p.substring(0, 14) + '…' : p }), datasets: [
                    { label: 'High', data: allP.map(function (p) { var c = 0; var recs = pMap[p] || []; for (var i = 0; i < recs.length; i++)if (riskLvl(recs[i]) === 'high') c++; return c }), backgroundColor: 'rgba(239,68,68,0.7)', borderRadius: 3, borderSkipped: false },
                    { label: 'Medium', data: allP.map(function (p) { var c = 0; var recs = pMap[p] || []; for (var i = 0; i < recs.length; i++)if (riskLvl(recs[i]) === 'medium') c++; return c }), backgroundColor: 'rgba(245,158,11,0.7)', borderRadius: 3, borderSkipped: false },
                    { label: 'Low', data: allP.map(function (p) { var c = 0; var recs = pMap[p] || []; for (var i = 0; i < recs.length; i++)if (riskLvl(recs[i]) === 'low') c++; return c }), backgroundColor: 'rgba(16,185,129,0.7)', borderRadius: 3, borderSkipped: false },
                ]
            }, options: { responsive: true, plugins: { legend: { labels: { boxWidth: 10 } } }, scales: { x: { stacked: true, grid: { display: false } }, y: { stacked: true, beginAtZero: true } } }
        });
        _riskInit = true;
    }
    rRisk();
}
function rRisk() {
    var f = DATA.slice(); var rf = (document.getElementById('riskF') || {}).value || '';
    var s = ((document.getElementById('riskS') || {}).value || '').toLowerCase();
    if (rf) f = f.filter(function (r) { return riskLvl(r) === rf });
    if (s) f = f.filter(function (r) { return fn(r).toLowerCase().indexOf(s) >= 0 || String(r.UID).indexOf(s) >= 0 });
    f.sort(function (a, b) { var o = { high: 0, medium: 1, low: 2 }; return o[riskLvl(a)] - o[riskLvl(b)] });
    bTbl(f, 'riskTbl', 'rk');
}
window.rkR = rRisk;

// ===== HEATMAP =====
var _hmInit = false;
function initHM() {
    if (_hmInit) return; _hmInit = true;
    var allP = pNames.slice(); allP.push('Unassigned');
    var g = '<div style="display:grid;grid-template-columns:180px repeat(4,1fr);gap:2px;margin-top:10px">';
    g += '<div style="font-weight:600;font-size:.7rem;color:var(--t3);padding:7px"></div>';
    DK.forEach(function (d) { g += '<div style="font-weight:600;font-size:.7rem;color:var(--t3);padding:7px;text-align:center">' + d.sh + '</div>' });
    allP.forEach(function (p) {
        var recs = pMap[p] || [];
        g += '<div style="font-size:.78rem;font-weight:500;padding:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--t2)">' + p + '</div>';
        DK.forEach(function (d) {
            var cnt = 0; for (var i = 0; i < recs.length; i++) { if (has(recs[i], d.key)) cnt++ }
            var pct = recs.length ? (cnt / recs.length * 100) : 0;
            var bg = pct >= 90 ? 'rgba(16,185,129,.25)' : pct >= 70 ? 'rgba(16,185,129,.12)' : pct >= 50 ? 'rgba(245,158,11,.15)' : pct >= 25 ? 'rgba(245,158,11,.08)' : 'rgba(239,68,68,.12)';
            var tc = pct >= 90 ? 'var(--green)' : pct >= 50 ? 'var(--amber)' : 'var(--red)';
            g += '<div class="hm-cell" style="background:' + bg + ';color:' + tc + '" title="' + p + ': ' + d.sh + ' — ' + cnt + '/' + recs.length + '">' + pct.toFixed(0) + '%</div>';
        });
    });
    g += '</div>';
    document.getElementById('hmGrid').innerHTML = g;

    mkCh('hmCh1', {
        type: 'radar', data: {
            labels: DK.map(function (d) { return d.sh }), datasets: pNames.slice(0, 6).map(function (p, i) {
                return { label: p.split(' ')[0], data: DK.map(function (d) { var recs = pMap[p] || []; if (!recs.length) return 0; var c = 0; for (var j = 0; j < recs.length; j++)if (has(recs[j], d.key)) c++; return +(c / recs.length * 100).toFixed(1) }), borderColor: AC[i], backgroundColor: AC[i] + '18', pointRadius: 3 }
            })
        }, options: { responsive: true, plugins: { legend: { labels: { boxWidth: 10 } } }, scales: { r: { min: 0, max: 100, ticks: { stepSize: 25 } } } }
    });

    mkCh('hmCh2', {
        type: 'bar', data: {
            labels: allP.map(function (p) { return p.length > 16 ? p.substring(0, 14) + '…' : p }), datasets: DK.map(function (d) {
                return { label: d.sh, data: allP.map(function (p) { var c = 0; var recs = pMap[p] || []; for (var i = 0; i < recs.length; i++)if (has(recs[i], d.key)) c++; return c }), backgroundColor: d.co + '99', borderRadius: 2, borderSkipped: false }
            })
        }, options: { responsive: true, plugins: { legend: { labels: { boxWidth: 10 } } }, scales: { x: { stacked: true, grid: { display: false } }, y: { stacked: true, beginAtZero: true } } }
    });
}

// ===== GAP ANALYSIS =====
var _gapInit = false;
function initGaps() {
    if (_gapInit) return; _gapInit = true;
    var combos = {};
    for (var i = 0; i < N; i++) {
        var r = DATA[i]; var missing = [];
        for (var j = 0; j < DK.length; j++) { if (!has(r, DK[j].key)) missing.push(DK[j].sh) }
        if (missing.length === 0) continue;
        missing.sort(); var k = missing.join(' + '); combos[k] = (combos[k] || 0) + 1;
    }
    var sorted = Object.keys(combos).map(function (k) { return [k, combos[k]] }).sort(function (a, b) { return b[1] - a[1] }).slice(0, 10);

    mkCh('gapCh1', { type: 'bar', data: { labels: sorted.map(function (s) { return s[0].length > 32 ? s[0].substring(0, 30) + '…' : s[0] }), datasets: [{ label: 'Records', data: sorted.map(function (s) { return s[1] }), backgroundColor: sorted.map(function (_, i) { return AC[i % AC.length] + '99' }), borderRadius: 5, borderSkipped: false }] }, options: { responsive: true, indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } } } } });

    var cooc = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
    for (var i = 0; i < N; i++) { var ms = []; for (var j = 0; j < 4; j++)ms.push(has(DATA[i], DK[j].key) ? 0 : 1); for (var a = 0; a < 4; a++)for (var b = a; b < 4; b++)if (ms[a] && ms[b]) cooc[a][b]++ }
    var pairs = []; for (var a = 0; a < 4; a++)for (var b = a + 1; b < 4; b++)pairs.push({ a: DK[a].sh, b: DK[b].sh, v: cooc[a][b] });
    pairs.sort(function (a, b) { return b.v - a.v });
    mkCh('gapCh2', { type: 'bar', data: { labels: pairs.map(function (p) { return p.a + ' & ' + p.b }), datasets: [{ label: 'Both missing', data: pairs.map(function (p) { return p.v }), backgroundColor: pairs.map(function (_, i) { return AC[i % AC.length] + '99' }), borderRadius: 5, borderSkipped: false }] }, options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } } } } });

    document.getElementById('gapPatterns').innerHTML = sorted.map(function (s, i) {
        return '<div class="sbi"><span class="sb-l" style="width:auto;flex:1"><strong>#' + (i + 1) + '</strong>&nbsp; ' + s[0] + '</span><span class="sb-p" style="color:var(--red);width:60px">' + s[1] + '</span><span class="sb-c">' + (s[1] / N * 100).toFixed(1) + '%</span></div>';
    }).join('');
}

// ===== WORKLOAD =====
var _wlInit = false;
function initWL() {
    if (_wlInit) return; _wlInit = true;
    var loads = pNames.map(function (p) { return (pMap[p] || []).length });
    var avg = loads.reduce(function (a, b) { return a + b }, 0) / loads.length;
    var max = Math.max.apply(null, loads), min = Math.min.apply(null, loads);
    var maxP = pNames[loads.indexOf(max)], minP = pNames[loads.indexOf(min)];
    var imbalance = ((max - min) / avg * 100).toFixed(0);

    document.getElementById('wlKpi').innerHTML = [
        { lb: 'Avg Caseload', v: avg.toFixed(0), s: 'Per person', dot: '#3b82f6' },
        { lb: 'Max Caseload', v: max, s: (maxP || '').split(' ')[0], dot: '#ef4444' },
        { lb: 'Min Caseload', v: min, s: (minP || '').split(' ')[0], dot: '#10b981' },
        { lb: 'Imbalance', v: imbalance + '%', s: '<span class="tag ' + (imbalance > 100 ? 'tr' : imbalance > 50 ? 'tw' : 'tg') + '">Spread ratio</span>', dot: '#a855f7' },
    ].map(function (k) { return '<div class="kpi"><div class="kpi-top"><span class="kpi-lb">' + k.lb + '</span><span class="kpi-dot" style="background:' + k.dot + '"></span></div><div class="kpi-v">' + k.v + '</div><div class="kpi-s">' + k.s + '</div></div>' }).join('');

    mkCh('wlCh1', { type: 'bar', data: { labels: pNames.map(function (p) { return p.length > 16 ? p.substring(0, 14) + '…' : p }), datasets: [{ label: 'Records', data: loads, backgroundColor: pNames.map(function (_, i) { return AC[i % AC.length] + 'cc' }), borderRadius: 5, borderSkipped: false }] }, options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } } } } });

    var eff = pNames.map(function (p) { var recs = pMap[p] || []; if (!recs.length) return 0; var c = 0; for (var i = 0; i < recs.length; i++)if (dc(recs[i]) === 4) c++; return +((c / recs.length) * 100).toFixed(1) });
    mkCh('wlCh2', { type: 'bar', data: { labels: pNames.map(function (p) { return p.length > 16 ? p.substring(0, 14) + '…' : p }), datasets: [{ label: 'Completion %', data: eff, backgroundColor: eff.map(function (e) { return e >= 80 ? 'rgba(16,185,129,0.7)' : e >= 50 ? 'rgba(245,158,11,0.7)' : 'rgba(239,68,68,0.7)' }), borderRadius: 5, borderSkipped: false }] }, options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { max: 100 } } } });
}

// ===== INSIGHTS =====
var _trInit = false;
function initTrends() {
    if (_trInit) return; _trInit = true;
    var bestDoc = dS[0], worstDoc = dS[0];
    for (var i = 1; i < dS.length; i++) { if (dS[i].f > bestDoc.f) bestDoc = dS[i]; if (dS[i].f < worstDoc.f) worstDoc = dS[i] }
    var hiCount = 0; for (var i = 0; i < N; i++)if (riskLvl(DATA[i]) === 'high') hiCount++;

    var bestPerson = '', bestRate = 0;
    pNames.forEach(function (p) { var recs = pMap[p] || []; if (!recs.length) return; var c = 0; for (var i = 0; i < recs.length; i++)if (dc(recs[i]) === 4) c++; var r = c / recs.length * 100; if (r > bestRate) { bestRate = r; bestPerson = p } });

    var insights = [
        { t: 'Document Gap', p: '<strong>' + bestDoc.sh + '</strong> has the highest filing rate at <span class="tag tg">' + (bestDoc.f / N * 100).toFixed(1) + '%</span> (' + bestDoc.f + '/' + N + '). <strong>' + worstDoc.sh + '</strong> is lowest at <span class="tag tr">' + (worstDoc.f / N * 100).toFixed(1) + '%</span> (' + worstDoc.f + '/' + N + '). Improving ' + worstDoc.sh + ' submissions would have the largest impact.' },
        { t: 'High Risk Records', p: '<span class="tag tr">' + hiCount + '</span> records are high risk (3+ docs missing or 2+ missing and unassigned). This is ' + (hiCount / N * 100).toFixed(1) + '% of all records.' },
        { t: 'Top Performer', p: '<strong>' + (bestPerson || 'N/A') + '</strong> has the highest full completion rate at <span class="tag tg">' + bestRate.toFixed(0) + '%</span> with ' + (pMap[bestPerson] || []).length + ' assigned records.' },
        { t: 'Assignment Coverage', p: '<span class="tag tr">' + unasn.toLocaleString() + '</span> records (' + (unasn / N * 100).toFixed(1) + '%) have no person responsible. Assigning these is critical for accountability.' },
        { t: 'Overall Status', p: 'Filing rate is <span class="tag tb">' + ((totalDocs / (N * 4)) * 100).toFixed(1) + '%</span> overall. ' + compl.toLocaleString() + ' records are fully compliant, ' + pend.toLocaleString() + ' require action.' },
    ];
    document.getElementById('insightsArea').innerHTML = insights.map(function (ins) { return '<div class="insight-card"><h4>' + ins.t + '</h4><p>' + ins.p + '</p></div>' }).join('');

    mkCh('fnlCh', { type: 'bar', data: { labels: ['Total', 'Has Support Plan', 'Has Assessment', 'Has Care Plan', 'Has Site Report', 'Fully Complete'], datasets: [{ label: 'Records', data: [N, dS[2].f, dS[0].f, dS[1].f, dS[3].f, compl], backgroundColor: ['rgba(91,108,247,0.7)', 'rgba(16,185,129,0.7)', 'rgba(34,201,176,0.7)', 'rgba(59,130,246,0.7)', 'rgba(245,158,11,0.7)', 'rgba(16,185,129,0.9)'], borderRadius: 5, borderSkipped: false }] }, options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } } } } });

    mkCh('radarCh', { type: 'radar', data: { labels: ['Assessment', 'Care Plan', 'Support Plan', 'Site Report', 'Assignment'], datasets: [{ label: 'Completion %', data: [dS[0].f / N * 100, dS[1].f / N * 100, dS[2].f / N * 100, dS[3].f / N * 100, asgn / N * 100].map(function (v) { return +v.toFixed(1) }), borderColor: '#5b6cf7', backgroundColor: 'rgba(91,108,247,0.12)', pointBackgroundColor: '#5b6cf7', pointRadius: 4 }] }, options: { responsive: true, scales: { r: { min: 0, max: 100, ticks: { stepSize: 25 } } } } });
}

// ===== EXPORT =====
function exportCSV() {
    var c = 'UID,SID,First Name,Last Name,Person Responsible,Assessment,Care Plan,Support Plan,Site Report,Missing Count,Risk Level\n';
    for (var i = 0; i < N; i++) {
        var r = DATA[i];
        c += [r.UID, r.SID, '"' + (r['Legal First Name'] || '') + '"', '"' + (r['Last Name'] || '') + '"', '"' + (gp(r) || 'Unassigned') + '"',
        has(r, DK[0].key) ? 'Filed' : 'Missing', has(r, DK[1].key) ? 'Filed' : 'Missing', has(r, DK[2].key) ? 'Filed' : 'Missing', has(r, DK[3].key) ? 'Filed' : 'Missing', mc(r), riskLvl(r)].join(',') + '\n';
    }
    var b = new Blob([c], { type: 'text/csv' }); var u = URL.createObjectURL(b); var a = document.createElement('a'); a.href = u; a.download = 'chsp_report_export.csv'; a.click(); URL.revokeObjectURL(u);
}

// ===== POPULATE FILTERS =====
function popFilters() {
    var opts = pNames.map(function (p) { return '<option value="' + p + '">' + p + '</option>' }).join('');
    var un = '<option value="__un__">Unassigned</option>';
    ['aP', 'pnP'].forEach(function (id) { var el = document.getElementById(id); if (el) el.innerHTML = '<option value="">All Persons</option>' + un + opts });
}

// ===== INIT =====
renderKPIs(); renderSBars(); renderOvCharts(); renderPCards(); popFilters(); rAll();
document.getElementById('ncPnd').textContent = pend;
document.getElementById('ncCmp').textContent = compl;
document.getElementById('ncAll').textContent = N;
