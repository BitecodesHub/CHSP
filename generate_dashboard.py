import openpyxl
import json

wb = openpyxl.load_workbook('Report.xlsx', data_only=True)
ws = wb['data']

headers = [cell.value for cell in ws[1]]
data = []
for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
    record = {}
    for j, val in enumerate(headers):
        cell_val = row[j]
        if cell_val is None:
            record[val] = ""
        else:
            record[val] = cell_val if not isinstance(cell_val, float) else int(cell_val) if cell_val == int(cell_val) else round(cell_val, 2)
    data.append(record)

json_data = json.dumps(data)

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CHSP Allied Health — Report Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --bg-0: #0a0a14;
    --bg-1: #10101e;
    --bg-2: #171730;
    --bg-card: #1a1a36;
    --bg-card-hover: #222248;
    --accent: #6c5ce7;
    --accent-light: #a29bfe;
    --cyan: #00cec9;
    --green: #00b894;
    --red: #ff6b6b;
    --orange: #fdcb6e;
    --pink: #fd79a8;
    --blue: #74b9ff;
    --text-1: #eaeaff;
    --text-2: #9d9dbf;
    --text-3: #5c5c80;
    --border: rgba(255,255,255,0.06);
    --glow-accent: rgba(108,92,231,0.25);
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: 'Inter', sans-serif;
    background: var(--bg-0);
    color: var(--text-1);
    min-height: 100vh;
  }}
  body::before {{
    content: '';
    position: fixed; inset: 0;
    background: radial-gradient(ellipse at 20% 0%, rgba(108,92,231,0.08), transparent 60%),
                radial-gradient(ellipse at 80% 100%, rgba(0,206,201,0.06), transparent 60%);
    pointer-events: none; z-index: 0;
  }}
  .app {{ position: relative; z-index: 1; }}

  /* Sidebar */
  .sidebar {{
    position: fixed; top: 0; left: 0; bottom: 0; width: 260px;
    background: var(--bg-1); border-right: 1px solid var(--border);
    display: flex; flex-direction: column; z-index: 10;
    transition: transform 0.3s;
  }}
  .sidebar-header {{
    padding: 28px 22px 20px;
    border-bottom: 1px solid var(--border);
  }}
  .sidebar-header h2 {{
    font-size: 1.15rem; font-weight: 800;
    background: linear-gradient(135deg, var(--accent-light), var(--cyan));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }}
  .sidebar-header p {{ font-size: 0.75rem; color: var(--text-3); margin-top: 4px; }}
  .sidebar-nav {{ padding: 16px 12px; flex: 1; overflow-y: auto; }}
  .nav-label {{
    font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.5px; color: var(--text-3); padding: 12px 10px 8px; margin-top: 8px;
  }}
  .nav-btn {{
    display: flex; align-items: center; gap: 10px; width: 100%;
    padding: 11px 14px; border: none; background: transparent;
    color: var(--text-2); font-family: inherit; font-size: 0.88rem;
    border-radius: 10px; cursor: pointer; transition: all 0.2s; text-align: left;
  }}
  .nav-btn:hover {{ background: rgba(108,92,231,0.08); color: var(--text-1); }}
  .nav-btn.active {{ background: rgba(108,92,231,0.15); color: var(--accent-light); font-weight: 600; }}
  .nav-btn .icon {{ font-size: 1.1rem; width: 24px; text-align: center; }}
  .nav-btn .badge-count {{
    margin-left: auto; padding: 2px 8px; border-radius: 10px;
    font-size: 0.72rem; font-weight: 700; background: rgba(108,92,231,0.2); color: var(--accent-light);
  }}

  /* Main Content */
  .main {{ margin-left: 260px; padding: 28px 32px; }}

  /* Page Header */
  .page-header {{
    display: flex; justify-content: space-between; align-items: flex-start;
    margin-bottom: 28px; flex-wrap: wrap; gap: 16px;
  }}
  .page-header h1 {{ font-size: 1.9rem; font-weight: 800; letter-spacing: -0.5px; }}
  .page-header h1 span {{
    background: linear-gradient(135deg, var(--accent-light), var(--cyan));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }}
  .page-header p {{ font-size: 0.9rem; color: var(--text-2); margin-top: 4px; }}
  .header-actions {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}

  /* Filter Bar */
  .filter-bar {{
    display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 24px; align-items: center;
  }}
  .filter-bar input, .filter-bar select {{
    padding: 10px 16px; background: var(--bg-2); border: 1px solid var(--border);
    border-radius: 10px; color: var(--text-1); font-family: inherit; font-size: 0.88rem;
    transition: border-color 0.3s; -webkit-appearance: none;
  }}
  .filter-bar input:focus, .filter-bar select:focus {{ outline: none; border-color: var(--accent); }}
  .filter-bar input {{ width: 280px; }}
  .filter-bar input::placeholder {{ color: var(--text-3); }}
  .filter-tag {{
    display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px;
    background: rgba(108,92,231,0.12); border: 1px solid rgba(108,92,231,0.25);
    border-radius: 8px; font-size: 0.82rem; color: var(--accent-light); cursor: pointer;
  }}
  .filter-tag:hover {{ background: rgba(108,92,231,0.2); }}
  .filter-tag .x {{ font-weight: 700; }}

  /* KPI Cards */
  .kpi-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(195px, 1fr));
    gap: 14px; margin-bottom: 28px;
  }}
  .kpi-card {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 14px; padding: 20px; position: relative; overflow: hidden;
    transition: all 0.3s;
  }}
  .kpi-card:hover {{ transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,0,0,0.25); }}
  .kpi-card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  }}
  .kpi-card:nth-child(1)::before {{ background: linear-gradient(90deg, var(--accent), var(--accent-light)); }}
  .kpi-card:nth-child(2)::before {{ background: linear-gradient(90deg, var(--green), #55efc4); }}
  .kpi-card:nth-child(3)::before {{ background: linear-gradient(90deg, var(--red), var(--pink)); }}
  .kpi-card:nth-child(4)::before {{ background: linear-gradient(90deg, var(--orange), #ffeaa7); }}
  .kpi-card:nth-child(5)::before {{ background: linear-gradient(90deg, var(--cyan), var(--blue)); }}
  .kpi-card:nth-child(6)::before {{ background: linear-gradient(90deg, var(--pink), var(--accent)); }}
  .kpi-icon {{ font-size: 1.5rem; margin-bottom: 10px; }}
  .kpi-label {{ font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--text-3); }}
  .kpi-value {{ font-size: 1.9rem; font-weight: 800; margin: 4px 0; letter-spacing: -0.5px; }}
  .kpi-sub {{ font-size: 0.78rem; color: var(--text-2); }}
  .kpi-pct {{ display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }}
  .kpi-pct.good {{ background: rgba(0,184,148,0.15); color: var(--green); }}
  .kpi-pct.warn {{ background: rgba(253,203,110,0.15); color: var(--orange); }}
  .kpi-pct.bad {{ background: rgba(255,107,107,0.15); color: var(--red); }}

  /* Charts */
  .charts-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 18px; margin-bottom: 28px;
  }}
  .chart-card {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 14px; padding: 22px; transition: all 0.3s;
  }}
  .chart-card:hover {{ border-color: rgba(255,255,255,0.1); }}
  .chart-card h3 {{ font-size: 0.95rem; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }}
  .chart-card canvas {{ max-height: 300px; }}

  /* Status Bars */
  .status-bars {{ margin-bottom: 28px; }}
  .status-bar-item {{
    display: flex; align-items: center; gap: 16px; padding: 14px 0;
    border-bottom: 1px solid var(--border);
  }}
  .status-bar-item:last-child {{ border-bottom: none; }}
  .sb-label {{ width: 220px; font-size: 0.88rem; font-weight: 500; flex-shrink: 0; }}
  .sb-track {{
    flex: 1; height: 10px; background: rgba(255,255,255,0.04);
    border-radius: 6px; overflow: hidden; position: relative;
  }}
  .sb-fill {{ height: 100%; border-radius: 6px; transition: width 0.6s ease; }}
  .sb-pct {{ width: 60px; text-align: right; font-size: 0.88rem; font-weight: 700; }}
  .sb-counts {{ width: 100px; text-align: right; font-size: 0.82rem; color: var(--text-2); }}

  /* Person Cards */
  .person-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 16px; margin-bottom: 28px;
  }}
  .person-card {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 14px; padding: 22px; transition: all 0.3s; cursor: pointer;
  }}
  .person-card:hover {{ transform: translateY(-3px); border-color: var(--accent); box-shadow: 0 8px 30px var(--glow-accent); }}
  .person-card.active {{ border-color: var(--accent); background: rgba(108,92,231,0.07); }}
  .pc-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }}
  .pc-avatar {{
    width: 42px; height: 42px; border-radius: 12px; display: flex;
    align-items: center; justify-content: center; font-weight: 800;
    font-size: 1rem; flex-shrink: 0;
  }}
  .pc-name {{ font-size: 1rem; font-weight: 700; }}
  .pc-count {{ font-size: 0.82rem; color: var(--text-2); }}
  .pc-stats {{ display: flex; gap: 10px; flex-wrap: wrap; }}
  .pc-stat {{
    flex: 1; min-width: 70px; text-align: center; padding: 10px 6px;
    background: rgba(255,255,255,0.02); border-radius: 8px;
  }}
  .pc-stat-val {{ font-size: 1.1rem; font-weight: 700; }}
  .pc-stat-label {{ font-size: 0.68rem; color: var(--text-3); margin-top: 2px; }}

  /* Data Table */
  .table-card {{
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 14px; overflow: hidden;
  }}
  .table-top {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 18px 22px; border-bottom: 1px solid var(--border); flex-wrap: wrap; gap: 10px;
  }}
  .table-top h3 {{ font-size: 1rem; font-weight: 600; }}
  .table-top .result-count {{ font-size: 0.82rem; color: var(--text-2); }}
  .table-scroll {{ overflow-x: auto; max-height: 540px; overflow-y: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.84rem; }}
  thead {{ position: sticky; top: 0; z-index: 2; }}
  thead th {{
    background: var(--bg-2); padding: 12px 16px; text-align: left;
    font-weight: 600; font-size: 0.74rem; text-transform: uppercase;
    letter-spacing: 0.8px; color: var(--text-3); white-space: nowrap;
    cursor: pointer; user-select: none; border-bottom: 2px solid var(--border);
    transition: color 0.2s;
  }}
  thead th:hover {{ color: var(--accent-light); }}
  tbody tr {{ transition: background 0.2s; }}
  tbody tr:hover {{ background: var(--bg-card-hover); }}
  tbody td {{
    padding: 11px 16px; border-bottom: 1px solid var(--border); white-space: nowrap;
  }}
  .uid-cell {{ font-weight: 700; color: var(--accent-light); font-size: 0.88rem; }}
  .name-cell {{ font-weight: 500; }}
  .person-cell {{ font-weight: 500; color: var(--cyan); }}
  .person-cell.unassigned {{ color: var(--text-3); font-style: italic; }}

  /* Status Pills */
  .status-pill {{
    display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px;
    border-radius: 6px; font-size: 0.76rem; font-weight: 600;
  }}
  .status-pill.done {{ background: rgba(0,184,148,0.12); color: var(--green); }}
  .status-pill.pending {{ background: rgba(255,107,107,0.12); color: var(--red); }}
  .status-pill .dot {{
    width: 6px; height: 6px; border-radius: 50%;
  }}
  .status-pill.done .dot {{ background: var(--green); }}
  .status-pill.pending .dot {{ background: var(--red); }}

  /* Pagination */
  .pagination {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 16px 22px; border-top: 1px solid var(--border); flex-wrap: wrap; gap: 10px;
  }}
  .pg-info {{ font-size: 0.82rem; color: var(--text-3); }}
  .pg-btns {{ display: flex; gap: 6px; }}
  .pg-btn {{
    padding: 7px 13px; background: var(--bg-2); border: 1px solid var(--border);
    border-radius: 8px; color: var(--text-2); font-family: inherit; font-size: 0.82rem;
    cursor: pointer; transition: all 0.2s;
  }}
  .pg-btn:hover {{ background: var(--bg-card-hover); color: var(--text-1); }}
  .pg-btn.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
  .pg-btn:disabled {{ opacity: 0.3; cursor: not-allowed; }}

  /* Sections */
  .section {{ display: none; }}
  .section.active {{ display: block; animation: fadeIn 0.35s ease; }}
  @keyframes fadeIn {{ from {{ opacity:0; transform: translateY(8px); }} to {{ opacity:1; transform: none; }} }}

  /* export button */
  .btn-export {{
    padding: 9px 18px; background: var(--accent); color: #fff;
    border: none; border-radius: 10px; font-family: inherit; font-size: 0.85rem;
    font-weight: 600; cursor: pointer; transition: all 0.2s;
    display: inline-flex; align-items: center; gap: 6px;
  }}
  .btn-export:hover {{ background: var(--accent-light); transform: translateY(-1px); }}

  /* Responsive */
  @media (max-width: 900px) {{
    .sidebar {{ transform: translateX(-100%); }}
    .sidebar.open {{ transform: translateX(0); }}
    .main {{ margin-left: 0; }}
    .charts-grid {{ grid-template-columns: 1fr; }}
    .person-grid {{ grid-template-columns: 1fr; }}
    .menu-toggle {{ display: block !important; }}
  }}
  .menu-toggle {{
    display: none; position: fixed; top: 16px; left: 16px; z-index: 20;
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 10px; padding: 10px 13px; cursor: pointer; font-size: 1.2rem;
    color: var(--text-1);
  }}

  /* Scrollbar */
  ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
  ::-webkit-scrollbar-track {{ background: transparent; }}
  ::-webkit-scrollbar-thumb {{ background: var(--bg-card-hover); border-radius: 3px; }}

  /* Pending highlight row */
  tr.row-all-missing {{ background: rgba(255,107,107,0.04); }}
  tr.row-all-done {{ background: rgba(0,184,148,0.03); }}
</style>
</head>
<body>

<button class="menu-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰</button>

<div class="app">
  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2>📋 CHSP Dashboard</h2>
      <p>Allied Health Report Tracker</p>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-label">Main</div>
      <button class="nav-btn active" onclick="showSection('overview', this)">
        <span class="icon">📊</span> Overview
      </button>
      <button class="nav-btn" onclick="showSection('people', this)">
        <span class="icon">👥</span> By Person
        <span class="badge-count" id="peopleCount"></span>
      </button>
      <button class="nav-btn" onclick="showSection('pending', this)">
        <span class="icon">⏳</span> Pending Reports
        <span class="badge-count" id="pendingNavCount"></span>
      </button>
      <button class="nav-btn" onclick="showSection('complete', this)">
        <span class="icon">✅</span> Fully Complete
        <span class="badge-count" id="completeNavCount"></span>
      </button>

      <div class="nav-label">Analysis</div>
      <button class="nav-btn" onclick="showSection('docanalysis', this)">
        <span class="icon">📄</span> Document Analysis
      </button>
      <button class="nav-btn" onclick="showSection('personanalysis', this)">
        <span class="icon">📈</span> Person Performance
      </button>

      <div class="nav-label">Data</div>
      <button class="nav-btn" onclick="showSection('alldata', this)">
        <span class="icon">🗃️</span> Full Data Table
        <span class="badge-count" id="totalNavCount"></span>
      </button>
    </nav>
  </aside>

  <main class="main">
    <!-- SECTION: Overview -->
    <div class="section active" id="sec-overview">
      <div class="page-header">
        <div>
          <h1><span>Overview</span> Dashboard</h1>
          <p>CHSP Allied Health Physiotherapy — Document Compliance Tracker</p>
        </div>
        <div class="header-actions">
          <button class="btn-export" onclick="exportCSV()">📥 Export CSV</button>
        </div>
      </div>

      <div class="kpi-grid" id="kpiGrid"></div>

      <!-- Document Completion Bars -->
      <div class="chart-card" style="margin-bottom: 24px;">
        <h3>📋 Document Completion Status</h3>
        <div class="status-bars" id="statusBars"></div>
      </div>

      <div class="charts-grid">
        <div class="chart-card">
          <h3>📊 Document Completion Overview</h3>
          <canvas id="docCompChart"></canvas>
        </div>
        <div class="chart-card">
          <h3>🎯 Compliance Categories</h3>
          <canvas id="complianceChart"></canvas>
        </div>
        <div class="chart-card">
          <h3>👥 Cases by Person Responsible</h3>
          <canvas id="personChart"></canvas>
        </div>
        <div class="chart-card">
          <h3>📉 Missing Documents Breakdown</h3>
          <canvas id="missingChart"></canvas>
        </div>
      </div>
    </div>

    <!-- SECTION: People -->
    <div class="section" id="sec-people">
      <div class="page-header">
        <div>
          <h1><span>Person</span> Responsible View</h1>
          <p>Click a person card to filter the data table below</p>
        </div>
      </div>
      <div class="person-grid" id="personGrid"></div>
      <div id="personTableArea"></div>
    </div>

    <!-- SECTION: Pending Reports -->
    <div class="section" id="sec-pending">
      <div class="page-header">
        <div>
          <h1>⏳ <span>Pending</span> Reports</h1>
          <p>Records with one or more missing documents</p>
        </div>
      </div>
      <div class="filter-bar">
        <input type="text" placeholder="🔍 Search by name, UID, or SID..." id="pendingSearch" oninput="renderPendingTable()">
        <select id="pendingDocFilter" onchange="renderPendingTable()">
          <option value="">All Missing Docs</option>
          <option value="assess">Missing Initial Assessment</option>
          <option value="care">Missing Care Plan</option>
          <option value="support">Missing Support Plan</option>
          <option value="site">Missing Site Inspection</option>
        </select>
        <select id="pendingPersonFilter" onchange="renderPendingTable()">
          <option value="">All Persons</option>
        </select>
      </div>
      <div id="pendingTableArea"></div>
    </div>

    <!-- SECTION: Complete -->
    <div class="section" id="sec-complete">
      <div class="page-header">
        <div>
          <h1>✅ <span>Fully Complete</span> Records</h1>
          <p>Records with all 4 documents submitted</p>
        </div>
      </div>
      <div class="filter-bar">
        <input type="text" placeholder="🔍 Search by name, UID, or SID..." id="completeSearch" oninput="renderCompleteTable()">
      </div>
      <div id="completeTableArea"></div>
    </div>

    <!-- SECTION: Doc Analysis -->
    <div class="section" id="sec-docanalysis">
      <div class="page-header">
        <div>
          <h1>📄 <span>Document</span> Analysis</h1>
          <p>Deep dive into each document type's completion status</p>
        </div>
      </div>
      <div class="charts-grid" id="docAnalysisCharts"></div>
      <div class="chart-card" style="margin-bottom: 20px;">
        <h3>🔬 Records Missing Multiple Documents</h3>
        <canvas id="multiMissingChart"></canvas>
      </div>
    </div>

    <!-- SECTION: Person Analysis -->
    <div class="section" id="sec-personanalysis">
      <div class="page-header">
        <div>
          <h1>📈 <span>Person</span> Performance</h1>
          <p>Compliance rates by person responsible</p>
        </div>
      </div>
      <div class="charts-grid">
        <div class="chart-card">
          <h3>📊 Completion Rate by Person</h3>
          <canvas id="personCompChart"></canvas>
        </div>
        <div class="chart-card">
          <h3>📋 Document Breakdown per Person</h3>
          <canvas id="personDocBreakdown"></canvas>
        </div>
      </div>
    </div>

    <!-- SECTION: All Data -->
    <div class="section" id="sec-alldata">
      <div class="page-header">
        <div>
          <h1>🗃️ <span>Full</span> Data Table</h1>
          <p>Browse all records with sorting, filtering, and search</p>
        </div>
        <div class="header-actions">
          <button class="btn-export" onclick="exportCSV()">📥 Export CSV</button>
        </div>
      </div>
      <div class="filter-bar">
        <input type="text" placeholder="🔍 Search by name, UID, or SID..." id="allSearch" oninput="renderAllTable()">
        <select id="allPersonFilter" onchange="renderAllTable()">
          <option value="">All Persons</option>
          <option value="__unassigned__">⚠️ Unassigned</option>
        </select>
        <select id="allStatusFilter" onchange="renderAllTable()">
          <option value="">All Statuses</option>
          <option value="complete">✅ Fully Complete</option>
          <option value="partial">⚠️ Partial</option>
          <option value="critical">🔴 3+ Docs Missing</option>
        </select>
        <select id="allSortSelect" onchange="renderAllTable()">
          <option value="uid-desc">UID ↓</option>
          <option value="uid-asc">UID ↑</option>
          <option value="name-asc">Name A-Z</option>
          <option value="name-desc">Name Z-A</option>
          <option value="missing-desc">Most Missing ↓</option>
          <option value="missing-asc">Least Missing ↑</option>
        </select>
        <span class="filter-tag" id="activeFilterTag" style="display:none" onclick="clearPersonFilter()">
          <span id="activeFilterName"></span> <span class="x">✕</span>
        </span>
      </div>
      <div id="allTableArea"></div>
    </div>

  </main>
</div>

<script>
const DATA = {json_data};

const DOC_KEYS = [
  {{ key: 'Initial Assessment - Allied Health', short: 'Assessment', color: '#6c5ce7' }},
  {{ key: 'Care Plan Allied Health', short: 'Care Plan', color: '#00cec9' }},
  {{ key: 'Support Plan From My Aged Care Portal - Allied Health - CHSP', short: 'Support Plan', color: '#00b894' }},
  {{ key: 'Site Inspection Report', short: 'Site Report', color: '#fdcb6e' }},
];
const PERSON_KEY = 'Person Responsible For CHSP - AH Physiotherapy KPIs';

// ========== Helpers ==========
function has(row, key) {{ return row[key] !== '' && row[key] !== null && row[key] !== undefined; }}
function docCount(row) {{ return DOC_KEYS.filter(d => has(row, d.key)).length; }}
function missingCount(row) {{ return 4 - docCount(row); }}
function getPerson(row) {{ return has(row, PERSON_KEY) ? row[PERSON_KEY] : ''; }}
function fullName(row) {{ return (row['Legal First Name'] + ' ' + row['Last Name']).trim(); }}

// ========== Stats ==========
const totalRecords = DATA.length;
const fullyComplete = DATA.filter(r => docCount(r) === 4).length;
const anyPending = DATA.filter(r => docCount(r) < 4).length;
const unassigned = DATA.filter(r => !getPerson(r)).length;
const assigned = totalRecords - unassigned;

const docStats = DOC_KEYS.map(d => ({{
  short: d.short,
  key: d.key,
  color: d.color,
  filled: DATA.filter(r => has(r, d.key)).length,
  empty: DATA.filter(r => !has(r, d.key)).length,
}}));

// Persons
const personMap = {{}};
DATA.forEach(r => {{
  const p = getPerson(r) || 'Unassigned';
  if (!personMap[p]) personMap[p] = [];
  personMap[p].push(r);
}});
const personNames = Object.keys(personMap).filter(p => p !== 'Unassigned').sort();
const AVATAR_COLORS = ['#6c5ce7','#00cec9','#fd79a8','#00b894','#fdcb6e','#74b9ff','#e17055','#a29bfe','#ffeaa7'];

// ========== KPIs ==========
function renderKPIs() {{
  const grid = document.getElementById('kpiGrid');
  const kpis = [
    {{ icon: '📋', label: 'Total Records', value: totalRecords, sub: 'In the dataset', pctClass: '' }},
    {{ icon: '✅', label: 'Fully Complete', value: fullyComplete, sub: ((fullyComplete/totalRecords)*100).toFixed(1) + '% of total', pctClass: 'good' }},
    {{ icon: '⏳', label: 'Pending Reports', value: anyPending, sub: ((anyPending/totalRecords)*100).toFixed(1) + '% need action', pctClass: anyPending > totalRecords*0.3 ? 'bad' : 'warn' }},
    {{ icon: '👤', label: 'Assigned', value: assigned, sub: personNames.length + ' people responsible', pctClass: '' }},
    {{ icon: '⚠️', label: 'Unassigned', value: unassigned, sub: ((unassigned/totalRecords)*100).toFixed(1) + '% without a person', pctClass: unassigned > 100 ? 'bad' : 'warn' }},
    {{ icon: '🔴', label: '3+ Docs Missing', value: DATA.filter(r => missingCount(r) >= 3).length, sub: 'Critical — needs attention', pctClass: 'bad' }},
  ];
  grid.innerHTML = kpis.map(k => `
    <div class="kpi-card">
      <div class="kpi-icon">${{k.icon}}</div>
      <div class="kpi-label">${{k.label}}</div>
      <div class="kpi-value">${{k.value.toLocaleString()}}</div>
      <div class="kpi-sub">${{k.pctClass ? `<span class="kpi-pct ${{k.pctClass}}">${{k.sub}}</span>` : k.sub}}</div>
    </div>
  `).join('');
}}

// ========== Status Bars ==========
function renderStatusBars() {{
  const container = document.getElementById('statusBars');
  container.innerHTML = docStats.map(d => {{
    const pct = ((d.filled / totalRecords) * 100).toFixed(1);
    const barColor = parseFloat(pct) >= 80 ? 'var(--green)' : parseFloat(pct) >= 50 ? 'var(--orange)' : 'var(--red)';
    return `<div class="status-bar-item">
      <span class="sb-label">${{d.short}}</span>
      <div class="sb-track"><div class="sb-fill" style="width:${{pct}}%;background:${{barColor}}"></div></div>
      <span class="sb-pct" style="color:${{barColor}}">${{pct}}%</span>
      <span class="sb-counts">${{d.filled}} / ${{totalRecords}}</span>
    </div>`;
  }}).join('');
}}

// ========== Charts ==========
Chart.defaults.color = '#9d9dbf';
Chart.defaults.borderColor = 'rgba(255,255,255,0.04)';
Chart.defaults.font.family = 'Inter';

function renderOverviewCharts() {{
  // Doc Completion Bar
  new Chart(document.getElementById('docCompChart'), {{
    type: 'bar',
    data: {{
      labels: docStats.map(d => d.short),
      datasets: [
        {{ label: 'Complete', data: docStats.map(d => d.filled), backgroundColor: docStats.map(d => d.color + 'cc'), borderRadius: 8, borderSkipped: false }},
        {{ label: 'Missing', data: docStats.map(d => d.empty), backgroundColor: '#ff6b6b55', borderRadius: 8, borderSkipped: false }},
      ]
    }},
    options: {{ responsive: true, plugins: {{ legend: {{ position: 'top' }} }}, scales: {{ x: {{ stacked: true }}, y: {{ stacked: true, beginAtZero: true }} }} }}
  }});

  // Compliance Doughnut
  const compCats = {{
    'Fully Complete': fullyComplete,
    'Partial (1-2 missing)': DATA.filter(r => {{ const m = missingCount(r); return m >= 1 && m <= 2; }}).length,
    'Critical (3+ missing)': DATA.filter(r => missingCount(r) >= 3).length,
  }};
  new Chart(document.getElementById('complianceChart'), {{
    type: 'doughnut',
    data: {{
      labels: Object.keys(compCats),
      datasets: [{{ data: Object.values(compCats), backgroundColor: ['#00b89499','#fdcb6e99','#ff6b6b99'], borderWidth: 0, hoverOffset: 8 }}]
    }},
    options: {{ responsive: true, cutout: '58%', plugins: {{ legend: {{ position: 'bottom' }} }} }}
  }});

  // Person bar chart
  const pLabels = personNames.length > 0 ? [...personNames, 'Unassigned'] : ['Unassigned'];
  const pCounts = pLabels.map(p => (personMap[p] || []).length);
  new Chart(document.getElementById('personChart'), {{
    type: 'bar',
    data: {{
      labels: pLabels.map(l => l.length > 18 ? l.substring(0,16) + '…' : l),
      datasets: [{{ label: 'Cases', data: pCounts, backgroundColor: pLabels.map((_,i) => AVATAR_COLORS[i % AVATAR_COLORS.length] + 'cc'), borderRadius: 8, borderSkipped: false }}]
    }},
    options: {{ responsive: true, indexAxis: 'y', plugins: {{ legend: {{ display: false }} }} }}
  }});

  // Missing docs pie
  const missingCounts = DOC_KEYS.map(d => DATA.filter(r => !has(r, d.key)).length);
  new Chart(document.getElementById('missingChart'), {{
    type: 'polarArea',
    data: {{
      labels: DOC_KEYS.map(d => d.short),
      datasets: [{{ data: missingCounts, backgroundColor: ['#6c5ce766','#00cec966','#00b89466','#fdcb6e66'] }}]
    }},
    options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
  }});
}}

// ========== Person Cards ==========
function renderPersonCards() {{
  const grid = document.getElementById('personGrid');
  const allPersons = [...personNames];
  if (personMap['Unassigned']) allPersons.push('Unassigned');

  grid.innerHTML = allPersons.map((p, i) => {{
    const records = personMap[p] || [];
    const complete = records.filter(r => docCount(r) === 4).length;
    const pending = records.length - complete;
    const initials = p === 'Unassigned' ? '?' : p.split(' ').map(w => w[0]).join('').substring(0,2).toUpperCase();
    const color = AVATAR_COLORS[i % AVATAR_COLORS.length];
    return `<div class="person-card" onclick="filterByPerson('${{p.replace(/'/g, "\\\\'")}}')">
      <div class="pc-header">
        <div style="display:flex;align-items:center;gap:12px;">
          <div class="pc-avatar" style="background:${{color}}22;color:${{color}}">${{initials}}</div>
          <div>
            <div class="pc-name">${{p}}</div>
            <div class="pc-count">${{records.length}} record${{records.length !== 1 ? 's' : ''}}</div>
          </div>
        </div>
      </div>
      <div class="pc-stats">
        <div class="pc-stat"><div class="pc-stat-val" style="color:var(--green)">${{complete}}</div><div class="pc-stat-label">Complete</div></div>
        <div class="pc-stat"><div class="pc-stat-val" style="color:var(--red)">${{pending}}</div><div class="pc-stat-label">Pending</div></div>
        <div class="pc-stat"><div class="pc-stat-val" style="color:var(--accent-light)">${{records.length ? ((complete/records.length)*100).toFixed(0) : 0}}%</div><div class="pc-stat-label">Rate</div></div>
      </div>
    </div>`;
  }}).join('');
  document.getElementById('peopleCount').textContent = allPersons.length;
}}

function filterByPerson(name) {{
  showSection('alldata', null);
  document.getElementById('allPersonFilter').value = name === 'Unassigned' ? '__unassigned__' : name;
  document.getElementById('activeFilterTag').style.display = 'inline-flex';
  document.getElementById('activeFilterName').textContent = name;
  renderAllTable();
  // Highlight nav
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.nav-btn')[6].classList.add('active');
}}

function clearPersonFilter() {{
  document.getElementById('allPersonFilter').value = '';
  document.getElementById('activeFilterTag').style.display = 'none';
  renderAllTable();
}}

// ========== Table Builder ==========
function buildTable(records, containerId, pageStateKey) {{
  if (!window._pageStates) window._pageStates = {{}};
  if (!window._pageStates[pageStateKey]) window._pageStates[pageStateKey] = {{ page: 1 }};
  const state = window._pageStates[pageStateKey];
  const perPage = 30;
  const totalPages = Math.max(1, Math.ceil(records.length / perPage));
  if (state.page > totalPages) state.page = 1;
  const start = (state.page - 1) * perPage;
  const pageData = records.slice(start, start + perPage);

  let html = `<div class="table-card">
    <div class="table-top"><h3>Records</h3><span class="result-count">${{records.length}} result${{records.length !== 1 ? 's' : ''}}</span></div>
    <div class="table-scroll"><table>
    <thead><tr>
      <th>UID</th><th>SID</th><th>Name</th><th>Person Responsible</th>
      <th>Assessment</th><th>Care Plan</th><th>Support Plan</th><th>Site Report</th><th>Status</th>
    </tr></thead><tbody>`;

  pageData.forEach(r => {{
    const mc = missingCount(r);
    const rowClass = mc === 0 ? 'row-all-done' : mc >= 3 ? 'row-all-missing' : '';
    const person = getPerson(r);
    html += `<tr class="${{rowClass}}">
      <td class="uid-cell">${{r.UID}}</td>
      <td>${{r.SID}}</td>
      <td class="name-cell">${{fullName(r)}}</td>
      <td class="${{person ? 'person-cell' : 'person-cell unassigned'}}">${{person || 'Unassigned'}}</td>`;
    DOC_KEYS.forEach(d => {{
      const ok = has(r, d.key);
      html += `<td><span class="status-pill ${{ok ? 'done' : 'pending'}}"><span class="dot"></span>${{ok ? 'Done' : 'Pending'}}</span></td>`;
    }});
    html += `<td><span class="status-pill ${{mc === 0 ? 'done' : 'pending'}}">${{mc === 0 ? '✅ Complete' : `⚠️ ${{mc}} missing`}}</span></td></tr>`;
  }});

  html += `</tbody></table></div>
    <div class="pagination">
      <span class="pg-info">Showing ${{start+1}}-${{Math.min(start+perPage, records.length)}} of ${{records.length}}</span>
      <div class="pg-btns">
        <button class="pg-btn" onclick="window._pageStates['${{pageStateKey}}'].page--;${{pageStateKey}}Refresh()" ${{state.page <= 1 ? 'disabled' : ''}}>← Prev</button>`;
  const maxShow = 5;
  let pStart = Math.max(1, state.page - 2);
  let pEnd = Math.min(totalPages, pStart + maxShow - 1);
  if (pEnd - pStart < maxShow - 1) pStart = Math.max(1, pEnd - maxShow + 1);
  for (let i = pStart; i <= pEnd; i++) {{
    html += `<button class="pg-btn ${{i === state.page ? 'active' : ''}}" onclick="window._pageStates['${{pageStateKey}}'].page=${{i}};${{pageStateKey}}Refresh()">${{i}}</button>`;
  }}
  html += `<button class="pg-btn" onclick="window._pageStates['${{pageStateKey}}'].page++;${{pageStateKey}}Refresh()" ${{state.page >= totalPages ? 'disabled' : ''}}>Next →</button>
      </div></div></div>`;
  document.getElementById(containerId).innerHTML = html;
}}

// ========== All Data ==========
function renderAllTable() {{
  let filtered = [...DATA];
  const search = (document.getElementById('allSearch')?.value || '').toLowerCase();
  const personF = document.getElementById('allPersonFilter')?.value || '';
  const statusF = document.getElementById('allStatusFilter')?.value || '';
  const sortF = document.getElementById('allSortSelect')?.value || 'uid-desc';

  if (search) filtered = filtered.filter(r => fullName(r).toLowerCase().includes(search) || String(r.UID).includes(search) || String(r.SID).includes(search));
  if (personF === '__unassigned__') filtered = filtered.filter(r => !getPerson(r));
  else if (personF) filtered = filtered.filter(r => getPerson(r) === personF);
  if (statusF === 'complete') filtered = filtered.filter(r => docCount(r) === 4);
  else if (statusF === 'partial') filtered = filtered.filter(r => {{ const m = missingCount(r); return m >= 1 && m <= 2; }});
  else if (statusF === 'critical') filtered = filtered.filter(r => missingCount(r) >= 3);

  const [sKey, sDir] = sortF.split('-');
  filtered.sort((a, b) => {{
    let va, vb;
    if (sKey === 'uid') {{ va = a.UID; vb = b.UID; }}
    else if (sKey === 'name') {{ va = fullName(a).toLowerCase(); vb = fullName(b).toLowerCase(); }}
    else if (sKey === 'missing') {{ va = missingCount(a); vb = missingCount(b); }}
    if (va < vb) return sDir === 'asc' ? -1 : 1;
    if (va > vb) return sDir === 'asc' ? 1 : -1;
    return 0;
  }});

  buildTable(filtered, 'allTableArea', 'allTable');
}}
window.allTableRefresh = renderAllTable;

// ========== Pending ==========
function renderPendingTable() {{
  let filtered = DATA.filter(r => docCount(r) < 4);
  const search = (document.getElementById('pendingSearch')?.value || '').toLowerCase();
  const docF = document.getElementById('pendingDocFilter')?.value || '';
  const personF = document.getElementById('pendingPersonFilter')?.value || '';

  if (search) filtered = filtered.filter(r => fullName(r).toLowerCase().includes(search) || String(r.UID).includes(search));
  if (docF === 'assess') filtered = filtered.filter(r => !has(r, DOC_KEYS[0].key));
  else if (docF === 'care') filtered = filtered.filter(r => !has(r, DOC_KEYS[1].key));
  else if (docF === 'support') filtered = filtered.filter(r => !has(r, DOC_KEYS[2].key));
  else if (docF === 'site') filtered = filtered.filter(r => !has(r, DOC_KEYS[3].key));
  if (personF === '__unassigned__') filtered = filtered.filter(r => !getPerson(r));
  else if (personF) filtered = filtered.filter(r => getPerson(r) === personF);

  buildTable(filtered, 'pendingTableArea', 'pendingTable');
}}
window.pendingTableRefresh = renderPendingTable;

// ========== Complete ==========
function renderCompleteTable() {{
  let filtered = DATA.filter(r => docCount(r) === 4);
  const search = (document.getElementById('completeSearch')?.value || '').toLowerCase();
  if (search) filtered = filtered.filter(r => fullName(r).toLowerCase().includes(search) || String(r.UID).includes(search));
  buildTable(filtered, 'completeTableArea', 'completeTable');
}}
window.completeTableRefresh = renderCompleteTable;

// ========== Doc Analysis ==========
function renderDocAnalysis() {{
  const container = document.getElementById('docAnalysisCharts');
  container.innerHTML = DOC_KEYS.map((d, i) => `
    <div class="chart-card">
      <h3 style="color:${{d.color}}">${{d.short}} Status</h3>
      <canvas id="docAn${{i}}"></canvas>
    </div>
  `).join('');

  DOC_KEYS.forEach((d, i) => {{
    const filled = DATA.filter(r => has(r, d.key)).length;
    const empty = totalRecords - filled;
    new Chart(document.getElementById('docAn' + i), {{
      type: 'doughnut',
      data: {{
        labels: ['Complete', 'Missing'],
        datasets: [{{ data: [filled, empty], backgroundColor: [d.color + 'cc', '#ff6b6b55'], borderWidth: 0 }}]
      }},
      options: {{ responsive: true, cutout: '62%', plugins: {{
        legend: {{ position: 'bottom' }},
        title: {{ display: true, text: `${{filled}} of ${{totalRecords}} (${{((filled/totalRecords)*100).toFixed(1)}}%)`, font: {{ size: 14 }} }}
      }} }}
    }});
  }});

  // Multi-missing
  const missingBins = [0,1,2,3,4];
  const missingBinCounts = missingBins.map(m => DATA.filter(r => missingCount(r) === m).length);
  new Chart(document.getElementById('multiMissingChart'), {{
    type: 'bar',
    data: {{
      labels: missingBins.map(m => m === 0 ? '0 (Complete)' : m + ' missing'),
      datasets: [{{ label: 'Records', data: missingBinCounts,
        backgroundColor: ['#00b89499','#74b9ff99','#fdcb6e99','#e1705599','#ff6b6b99'],
        borderRadius: 8, borderSkipped: false,
      }}]
    }},
    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true }} }} }}
  }});
}}

// ========== Person Analysis ==========
function renderPersonAnalysis() {{
  const allPersons = [...personNames];
  if (personMap['Unassigned']) allPersons.push('Unassigned');

  // Completion rate per person
  const rates = allPersons.map(p => {{
    const recs = personMap[p] || [];
    if (recs.length === 0) return 0;
    const totalDocs = recs.length * 4;
    const filledDocs = recs.reduce((s, r) => s + docCount(r), 0);
    return +((filledDocs / totalDocs) * 100).toFixed(1);
  }});

  new Chart(document.getElementById('personCompChart'), {{
    type: 'bar',
    data: {{
      labels: allPersons.map(p => p.length > 18 ? p.substring(0,16) + '…' : p),
      datasets: [{{ label: 'Completion %', data: rates,
        backgroundColor: allPersons.map((_,i) => AVATAR_COLORS[i % AVATAR_COLORS.length] + 'cc'),
        borderRadius: 8, borderSkipped: false,
      }}]
    }},
    options: {{ responsive: true, indexAxis: 'y', plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ max: 100 }} }} }}
  }});

  // Stacked doc breakdown per person
  const datasets = DOC_KEYS.map((d, di) => ({{
    label: d.short,
    data: allPersons.map(p => (personMap[p] || []).filter(r => has(r, d.key)).length),
    backgroundColor: d.color + '99',
    borderRadius: 4,
    borderSkipped: false,
  }}));
  new Chart(document.getElementById('personDocBreakdown'), {{
    type: 'bar',
    data: {{
      labels: allPersons.map(p => p.length > 18 ? p.substring(0,16) + '…' : p),
      datasets,
    }},
    options: {{ responsive: true, scales: {{ x: {{ stacked: true }}, y: {{ stacked: true, beginAtZero: true }} }} }}
  }});
}}

// ========== Navigation ==========
function showSection(name, btn) {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.getElementById('sec-' + name).classList.add('active');
  if (btn) {{
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }}
  // Lazy render
  if (name === 'pending') renderPendingTable();
  if (name === 'complete') renderCompleteTable();
  if (name === 'alldata') renderAllTable();
}}

// ========== Export CSV ==========
function exportCSV() {{
  let csv = 'UID,SID,First Name,Last Name,Person Responsible,Initial Assessment,Care Plan,Support Plan,Site Report,Missing Count\\n';
  DATA.forEach(r => {{
    csv += [r.UID, r.SID, r['Legal First Name'], r['Last Name'],
      getPerson(r) || 'Unassigned',
      has(r, DOC_KEYS[0].key) ? 'Done' : 'Pending',
      has(r, DOC_KEYS[1].key) ? 'Done' : 'Pending',
      has(r, DOC_KEYS[2].key) ? 'Done' : 'Pending',
      has(r, DOC_KEYS[3].key) ? 'Done' : 'Pending',
      missingCount(r),
    ].map(v => `"${{v}}"`).join(',') + '\\n';
  }});
  const blob = new Blob([csv], {{ type: 'text/csv' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'chsp_report.csv'; a.click();
  URL.revokeObjectURL(url);
}}

// ========== Populate Person Filters ==========
function populatePersonFilters() {{
  const options = personNames.map(p => `<option value="${{p}}">${{p}}</option>`).join('');
  const unOpt = `<option value="__unassigned__">⚠️ Unassigned</option>`;
  ['allPersonFilter', 'pendingPersonFilter'].forEach(id => {{
    const el = document.getElementById(id);
    if (el) el.innerHTML = `<option value="">All Persons</option>${{unOpt}}${{options}}`;
  }});
}}

// ========== Init ==========
renderKPIs();
renderStatusBars();
renderOverviewCharts();
renderPersonCards();
renderDocAnalysis();
renderPersonAnalysis();
populatePersonFilters();
renderAllTable();

document.getElementById('pendingNavCount').textContent = anyPending;
document.getElementById('completeNavCount').textContent = fullyComplete;
document.getElementById('totalNavCount').textContent = totalRecords;
</script>
</body>
</html>'''

with open('/Users/yashcomputers/Desktop/Test_Dau/index.html', 'w') as f:
    f.write(html)

print("Dashboard HTML generated successfully!")
