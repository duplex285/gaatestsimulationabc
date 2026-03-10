#!/usr/bin/env python3
"""Build a fully dynamic HTML dashboard for ABC Assessment.

All simulation and scoring runs client-side via JavaScript + Chart.js.
The Python script only embeds type/state description JSON and writes the HTML.

Reference: abc-assessment-spec Section 11.4
"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.python_scoring.type_descriptions import DOMAIN_STATE_DESCRIPTIONS, TYPE_DESCRIPTIONS


def main():
    type_desc_json = json.dumps(TYPE_DESCRIPTIONS)
    state_desc_json = json.dumps(DOMAIN_STATE_DESCRIPTIONS)

    html = build_html(type_desc_json, state_desc_json)

    site_dir = project_root / "outputs" / "site"
    site_dir.mkdir(parents=True, exist_ok=True)
    output_path = site_dir / "index.html"
    output_path.write_text(html)

    size_kb = output_path.stat().st_size / 1024
    print(f"Dashboard saved to: {output_path}")
    print(f"File size: {size_kb:.0f} KB")
    print("\nTo deploy on Netlify:")
    print("  1. Drag and drop the outputs/site/ folder to netlify.com/drop")
    print("  2. Or connect your repo and set publish directory to: outputs/site")
    return 0


def build_html(type_desc_json, state_desc_json):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>ABC Assessment — Simulation Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.1.0/dist/chartjs-plugin-annotation.min.js"></script>
    <style>
        :root {{
            --bg: #f8f9fa; --card: #ffffff; --text: #1a1a2e; --muted: #6c757d;
            --border: #e9ecef; --ambition: #E8563A; --belonging: #3A8FE8;
            --craft: #3ABF5E; --sidebar-bg: #1a1a2e; --sidebar-w: 240px; --accent: #3A8FE8;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}

        .sidebar {{ position: fixed; left: 0; top: 0; bottom: 0; width: var(--sidebar-w); background: var(--sidebar-bg); display: flex; flex-direction: column; z-index: 100; overflow-y: auto; }}
        .sidebar-title {{ padding: 1.5rem 1.2rem 0.5rem; color: white; font-size: 1.05rem; font-weight: 700; }}
        .sidebar-subtitle {{ padding: 0 1.2rem 0.8rem; color: rgba(255,255,255,0.5); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; }}

        .sim-sidebar {{ padding: 0 1rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 0.5rem; }}
        .sim-sidebar label {{ display: block; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: rgba(255,255,255,0.5); margin-bottom: 0.15rem; margin-top: 0.5rem; }}
        .sim-sidebar input[type="range"] {{ width: 100%; accent-color: var(--accent); }}
        .sim-sidebar .val {{ color: white; font-size: 0.85rem; font-weight: 700; font-variant-numeric: tabular-nums; }}
        .sim-sidebar .sim-row {{ display: flex; justify-content: space-between; align-items: center; }}
        .sim-run-btn {{ width: 100%; padding: 0.5rem; margin-top: 0.6rem; background: var(--accent); color: white; border: none; border-radius: 6px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: background 0.15s; }}
        .sim-run-btn:hover {{ background: #2d7ad6; }}
        .sim-run-btn:disabled {{ background: #555; cursor: not-allowed; }}
        .sim-status {{ display: block; color: rgba(255,255,255,0.5); font-size: 0.72rem; text-align: center; margin-top: 0.3rem; min-height: 1em; }}

        .sidebar nav {{ flex: 1; display: flex; flex-direction: column; gap: 0.2rem; padding: 0 0.8rem; }}
        .nav-item {{ display: block; padding: 0.55rem 0.9rem; border-radius: 8px; color: rgba(255,255,255,0.7); text-decoration: none; font-size: 0.88rem; font-weight: 500; cursor: pointer; transition: background 0.15s, color 0.15s; user-select: none; }}
        .nav-item:hover {{ background: rgba(255,255,255,0.08); color: white; }}
        .nav-item.active {{ background: var(--accent); color: white; }}
        .sidebar-footer {{ padding: 1rem 1.2rem; color: rgba(255,255,255,0.35); font-size: 0.7rem; }}

        .hamburger {{ display: none; position: fixed; top: 0.8rem; left: 0.8rem; z-index: 200; background: var(--sidebar-bg); color: white; border: none; border-radius: 6px; width: 40px; height: 40px; font-size: 1.4rem; cursor: pointer; align-items: center; justify-content: center; }}
        .nav-overlay {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 90; }}

        .main {{ margin-left: var(--sidebar-w); min-height: 100vh; }}
        .tab-content {{ display: none; animation: tabFadeIn 0.25s ease; }}
        .tab-content.active {{ display: block; }}
        @keyframes tabFadeIn {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .tab-inner {{ max-width: 1400px; margin: 0 auto; padding: 2rem 2.5rem; }}
        .tab-header {{ margin-bottom: 1.5rem; }}
        .tab-header h1 {{ font-size: 1.6rem; font-weight: 700; margin-bottom: 0.3rem; }}
        .tab-header p {{ font-size: 0.92rem; color: var(--muted); }}

        @media (max-width: 768px) {{
            .sidebar {{ transform: translateX(-100%); transition: transform 0.25s ease; }}
            .sidebar.open {{ transform: translateX(0); }}
            .hamburger {{ display: flex; }}
            .nav-overlay.open {{ display: block; }}
            .main {{ margin-left: 0; }}
            .tab-inner {{ padding: 3.5rem 1rem 1.5rem; }}
        }}

        .stats-bar {{ display: flex; justify-content: center; gap: 2rem; padding: 1.5rem 2rem; background: white; border-radius: 8px; border: 1px solid var(--border); flex-wrap: wrap; margin-bottom: 1.5rem; }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 1.8rem; font-weight: 700; color: var(--text); }}
        .stat-label {{ font-size: 0.8rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}
        .stat-pass {{ color: #3ABF5E; }}

        .section {{ margin-bottom: 2.5rem; }}
        .section h2 {{ font-size: 1.3rem; font-weight: 600; margin-bottom: 0.3rem; }}
        .section .desc {{ font-size: 0.9rem; color: var(--muted); margin-bottom: 1rem; }}

        .card {{ background: var(--card); border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); overflow: hidden; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
        @media (max-width: 768px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

        table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
        th {{ background: var(--bg); padding: 0.6rem 0.8rem; text-align: left; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.03em; color: var(--muted); border-bottom: 2px solid var(--border); }}
        td {{ padding: 0.5rem 0.8rem; border-bottom: 1px solid var(--border); }}
        td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
        .domain-badge, .state-badge {{ display: inline-block; padding: 0.15rem 0.6rem; border-radius: 12px; color: white; font-size: 0.8rem; font-weight: 500; }}

        .validation-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-top: 1rem; }}
        .gate {{ padding: 1rem; border-radius: 8px; background: #f0fdf4; border-left: 4px solid #3ABF5E; }}
        .gate-label {{ font-size: 0.8rem; color: var(--muted); }}
        .gate-value {{ font-size: 1.2rem; font-weight: 700; }}
        .gate-target {{ font-size: 0.75rem; color: var(--muted); }}

        .controls {{ display: flex; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap; align-items: center; }}
        .controls input[type="text"] {{ flex: 1; min-width: 200px; padding: 0.5rem 0.75rem; border: 1px solid var(--border); border-radius: 6px; font-size: 0.9rem; outline: none; }}
        .controls input[type="text"]:focus {{ border-color: #3A8FE8; box-shadow: 0 0 0 3px rgba(58,143,232,0.15); }}
        .controls select {{ padding: 0.5rem 0.75rem; border: 1px solid var(--border); border-radius: 6px; font-size: 0.9rem; background: white; cursor: pointer; }}
        .controls .count {{ font-size: 0.85rem; color: var(--muted); white-space: nowrap; }}

        #participants-table {{ font-size: 0.82rem; }}
        #participants-table th {{ position: sticky; top: 0; z-index: 2; cursor: pointer; user-select: none; white-space: nowrap; font-size: 0.72rem; }}
        #participants-table th:hover {{ background: #e2e6ea; }}
        #participants-table th .sort-arrow {{ margin-left: 3px; opacity: 0.3; }}
        #participants-table th.sorted .sort-arrow {{ opacity: 1; }}
        #participants-table td {{ padding: 0.35rem 0.5rem; white-space: nowrap; }}
        .participants-wrap {{ max-height: 700px; overflow: auto; border: 1px solid var(--border); border-radius: 8px; }}
        .row-clickable {{ cursor: pointer; }}
        .row-clickable:hover {{ background: #f0f4ff; }}

        .detail-wrap {{ background: #fafbfc; padding: 1.2rem; }}
        .detail-wrap .detail-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
        .detail-section {{ min-width: 0; overflow-wrap: break-word; word-wrap: break-word; }}
        .detail-section h4 {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); margin-bottom: 0.4rem; }}
        .detail-section .items-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.25rem 0.5rem; font-size: 0.82rem; }}
        .detail-section .items-grid .item-val {{ font-variant-numeric: tabular-nums; }}
        .detail-section .items-grid .item-label {{ color: var(--muted); }}

        .score-bar-wrap {{ display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.2rem; font-size: 0.82rem; }}
        .score-bar-label {{ width: 80px; text-align: right; color: var(--muted); flex-shrink: 0; }}
        .score-bar-track {{ flex: 1; height: 14px; background: #eee; border-radius: 7px; overflow: hidden; position: relative; }}
        .score-bar-fill {{ height: 100%; border-radius: 7px; }}
        .score-bar-val {{ width: 36px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; flex-shrink: 0; }}
        .threshold-line {{ position: absolute; left: 55%; top: 0; bottom: 0; width: 1.5px; background: rgba(0,0,0,0.3); }}
        .export-btn {{ padding: 0.5rem 1rem; background: #16213e; color: white; border: none; border-radius: 6px; font-size: 0.85rem; cursor: pointer; }}
        .export-btn:hover {{ background: #1a2a4e; }}

        /* Type Guide: domain index cards */
        .tg-index {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}
        @media (max-width: 900px) {{ .tg-index {{ grid-template-columns: 1fr; }} }}
        .tg-domain-card {{ background: var(--card); border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); overflow: hidden; }}
        .tg-domain-bar {{ height: 5px; }}
        .tg-domain-header {{ padding: 1.2rem 1.5rem 0.8rem; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text); }}
        .tg-type-list {{ list-style: none; padding: 0 1.5rem 1.2rem; }}
        .tg-type-item {{ padding: 0.5rem 0; border-bottom: 1px solid var(--border); cursor: pointer; display: flex; justify-content: space-between; align-items: center; font-size: 0.95rem; color: #1a5c2e; transition: color 0.15s; }}
        .tg-type-item:last-child {{ border-bottom: none; }}
        .tg-type-item:hover {{ color: var(--text); }}
        .tg-type-item .tg-chevron {{ font-size: 0.85rem; color: var(--muted); transition: transform 0.2s; }}
        .tg-type-item.active .tg-chevron {{ transform: rotate(90deg); }}
        .tg-type-item .tg-item-count {{ font-size: 0.75rem; color: var(--muted); margin-left: auto; margin-right: 0.5rem; font-variant-numeric: tabular-nums; }}

        /* Type Guide: expanded detail panel */
        .tg-detail {{ background: var(--card); border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); overflow: hidden; margin-top: 1.5rem; animation: tabFadeIn 0.25s ease; }}
        .tg-detail-header {{ padding: 1.5rem 2rem; position: relative; }}
        .tg-detail-header .tg-domain-label {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.85; margin-bottom: 0.2rem; }}
        .tg-detail-header .tg-name {{ font-size: 1.8rem; font-weight: 700; font-style: italic; font-family: Georgia, "Times New Roman", serif; }}
        .tg-detail-header .tg-tagline {{ font-size: 0.95rem; margin-top: 0.2rem; opacity: 0.9; }}
        .tg-detail-header .tg-count {{ font-size: 0.75rem; opacity: 0.7; margin-top: 0.3rem; }}
        .tg-abc-dots {{ position: absolute; right: 2rem; top: 1.5rem; display: flex; gap: 0.5rem; }}
        .tg-abc-dot {{ width: 36px; height: 36px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; color: white; }}
        .tg-abc-dot.dominant {{ opacity: 1; }}
        .tg-abc-dot.secondary {{ opacity: 0.4; }}
        .tg-detail-close {{ position: absolute; right: 2rem; bottom: 1rem; background: none; border: none; color: rgba(255,255,255,0.7); font-size: 1.2rem; cursor: pointer; padding: 0.2rem 0.5rem; border-radius: 4px; }}
        .tg-detail-close:hover {{ color: white; background: rgba(255,255,255,0.15); }}
        .tg-body {{ padding: 2rem; }}
        .tg-desc {{ font-size: 0.95rem; line-height: 1.7; margin-bottom: 1.5rem; color: var(--text); }}
        .tg-section-label {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 0.6rem; font-weight: 600; }}
        .tg-strengths {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 1.5rem; }}
        .tg-strength-item {{ background: #f8f9fa; padding: 0.7rem 1rem; border-radius: 6px; font-size: 0.88rem; border-left: 3px solid var(--border); }}
        .tg-two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }}
        .tg-two-col > div {{ background: #faf8f0; padding: 1rem 1.2rem; border-radius: 8px; }}
        .tg-two-col .tg-section-label {{ color: #8a7a5a; }}
        .tg-two-col p {{ font-size: 0.88rem; line-height: 1.6; }}
        .tg-growth {{ background: #faf8f0; padding: 1rem 1.2rem; border-radius: 8px; margin-bottom: 1.5rem; }}
        .tg-growth .tg-section-label {{ color: #8a7a5a; }}
        .tg-growth p {{ font-size: 0.88rem; line-height: 1.6; }}
        .tg-subscales {{ margin-bottom: 0.5rem; }}
        .tg-subscales .tg-section-label {{ margin-bottom: 0.8rem; }}
        .tg-sub-row {{ display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.3rem; font-size: 0.82rem; }}
        .tg-sub-label {{ width: 70px; text-align: right; color: var(--muted); flex-shrink: 0; }}
        .tg-sub-track {{ flex: 1; height: 12px; background: #eee; border-radius: 6px; overflow: hidden; position: relative; }}
        .tg-sub-fill {{ height: 100%; border-radius: 6px; }}
        .tg-sub-val {{ width: 32px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; flex-shrink: 0; }}
        .tg-sub-threshold {{ position: absolute; left: 55%; top: 0; bottom: 0; width: 1px; background: rgba(0,0,0,0.2); }}
        .tg-footer {{ padding: 0.8rem 2rem; background: #f5f3ee; font-size: 0.75rem; color: #8a7a5a; border-top: 1px solid #e8e4da; }}
        @media (max-width: 768px) {{
            .tg-strengths, .tg-two-col {{ grid-template-columns: 1fr; }}
            .tg-abc-dots {{ position: static; margin-top: 0.5rem; }}
        }}
        .belbin-badge, .sig-badge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.78rem; font-weight: 500; margin: 0.1rem; }}
        .belbin-badge {{ background: #e8ecf1; color: #333; }}

        /* Belbin Role Guide */
        .bg-role-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 0.5rem; }}
        .bg-role-item {{ padding: 0.65rem 1rem; background: var(--card); border-radius: 8px; border: 1px solid var(--border); cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: border-color 0.15s, box-shadow 0.15s; }}
        .bg-role-item:hover {{ border-color: var(--accent); box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
        .bg-role-item.active {{ border-color: var(--accent); box-shadow: 0 0 0 2px rgba(58,143,232,0.2); }}
        .bg-role-item .bg-role-name {{ font-size: 0.92rem; font-weight: 600; }}
        .bg-role-item .bg-role-qual {{ font-size: 0.78rem; color: var(--muted); }}
        .bg-role-item .bg-role-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
        .bg-detail {{ background: var(--card); border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); overflow: hidden; margin-top: 1.5rem; animation: tabFadeIn 0.25s ease; }}
        .bg-detail-header {{ padding: 1.2rem 1.5rem; display: flex; justify-content: space-between; align-items: flex-start; }}
        .bg-detail-header h3 {{ font-size: 1.3rem; font-weight: 700; }}
        .bg-detail-header .bg-qualifier {{ font-size: 0.85rem; color: var(--muted); font-weight: 400; }}
        .bg-detail-close {{ background: none; border: 1px solid var(--border); border-radius: 6px; color: var(--muted); font-size: 1rem; cursor: pointer; padding: 0.2rem 0.6rem; }}
        .bg-detail-close:hover {{ background: var(--bg); }}
        .bg-detail-body {{ padding: 0 1.5rem 1.5rem; }}
        .bg-detail-body .bg-section {{ margin-bottom: 1.2rem; }}
        .bg-detail-body .bg-label {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 600; margin-bottom: 0.4rem; }}
        .bg-detail-body p {{ font-size: 0.92rem; line-height: 1.65; }}
        .bg-condition {{ display: inline-block; background: #f0f4ff; border: 1px solid #d0daf0; border-radius: 6px; padding: 0.4rem 0.8rem; font-family: "SF Mono", Menlo, monospace; font-size: 0.82rem; color: #2d5aa0; }}
        .bg-type-links {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
        .bg-type-link {{ display: inline-block; padding: 0.25rem 0.7rem; border-radius: 14px; font-size: 0.82rem; font-weight: 500; cursor: pointer; transition: background 0.15s; text-decoration: none; }}
        .bg-type-link:hover {{ opacity: 0.85; }}
        .bg-type-link[data-domain="ambition"] {{ background: #fde8e4; color: #a33825; }}
        .bg-type-link[data-domain="belonging"] {{ background: #e4effd; color: #2563a3; }}
        .bg-type-link[data-domain="craft"] {{ background: #e4fde8; color: #1f7a35; }}
        .bg-type-link[data-domain="any"] {{ background: #f0f0f0; color: #555; }}
        .sig-badge-medium {{ background: #FFF3E0; color: #E65100; border: 1px solid #F5A623; }}
        .sig-badge-high {{ background: #FFEBEE; color: #C62828; border: 1px solid #E8563A; }}
        .type-desc-block {{ background: #f8f9fa; border-radius: 6px; padding: 0.75rem; margin-top: 0.5rem; font-size: 0.85rem; overflow-wrap: break-word; word-wrap: break-word; overflow: hidden; }}
        .type-desc-block .tagline {{ font-weight: 600; font-size: 0.9rem; margin-bottom: 0.3rem; }}
        .type-desc-block .growth {{ font-style: italic; color: var(--muted); margin-top: 0.3rem; }}

        /* Domain States 2x2 quadrant */
        .ds-quadrant {{ display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: auto auto; gap: 0; position: relative; }}
        .ds-quadrant-cell {{ padding: 1.5rem; border: 1px solid var(--border); min-height: 180px; cursor: pointer; transition: background 0.15s; }}
        .ds-quadrant-cell:hover {{ filter: brightness(0.97); }}
        .ds-quadrant-cell.active {{ box-shadow: inset 0 0 0 2px var(--accent); z-index: 1; }}
        .ds-quadrant-cell:nth-child(1) {{ border-radius: 12px 0 0 0; }}
        .ds-quadrant-cell:nth-child(2) {{ border-radius: 0 12px 0 0; }}
        .ds-quadrant-cell:nth-child(3) {{ border-radius: 0 0 0 12px; }}
        .ds-quadrant-cell:nth-child(4) {{ border-radius: 0 0 12px 0; }}
        .ds-cell-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem; }}
        .ds-cell-label {{ font-size: 1.1rem; font-weight: 700; }}
        .ds-cell-pct {{ font-size: 1.4rem; font-weight: 700; font-variant-numeric: tabular-nums; }}
        .ds-cell-condition {{ font-size: 0.75rem; color: var(--muted); margin-bottom: 0.5rem; font-family: "SF Mono", Menlo, monospace; }}
        .ds-cell-summary {{ font-size: 0.88rem; line-height: 1.5; }}
        .ds-axis-label {{ text-align: center; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 600; padding: 0.5rem; }}
        .ds-axis-y {{ writing-mode: vertical-rl; text-orientation: mixed; transform: rotate(180deg); padding: 0; display: flex; align-items: center; justify-content: center; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 600; }}
        .ds-quadrant-wrap {{ display: grid; grid-template-columns: 30px 1fr; gap: 0; align-items: center; }}
        .ds-detail {{ background: var(--card); border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); overflow: hidden; margin-top: 1.5rem; animation: tabFadeIn 0.25s ease; }}
        .ds-detail-header {{ padding: 1.2rem 1.5rem; display: flex; justify-content: space-between; align-items: center; }}
        .ds-detail-header h3 {{ font-size: 1.2rem; font-weight: 700; }}
        .ds-detail-close {{ background: none; border: 1px solid var(--border); border-radius: 6px; color: var(--muted); font-size: 1rem; cursor: pointer; padding: 0.2rem 0.6rem; }}
        .ds-detail-close:hover {{ background: var(--bg); }}
        .ds-detail-body {{ padding: 0 1.5rem 1.5rem; }}
        .ds-detail-body .ds-section {{ margin-bottom: 1.2rem; }}
        .ds-detail-body .ds-label {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 600; margin-bottom: 0.4rem; }}
        .ds-detail-body p {{ font-size: 0.92rem; line-height: 1.65; }}
        .ds-fatigue-indicator {{ display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }}
        .ds-fatigue-bar {{ flex: 1; height: 8px; background: #eee; border-radius: 4px; overflow: hidden; max-width: 200px; }}
        .ds-fatigue-fill {{ height: 100%; border-radius: 4px; }}
        .ds-fatigue-label {{ font-size: 0.82rem; font-weight: 600; }}
        @media (max-width: 768px) {{ .ds-quadrant {{ grid-template-columns: 1fr; }} }}

        .pipeline-steps {{ counter-reset: step; list-style: none; padding: 0; }}
        .pipeline-steps li {{ counter-increment: step; padding: 0.75rem 0.75rem 0.75rem 3rem; margin-bottom: 0.5rem; background: var(--card); border-radius: 8px; border-left: 3px solid var(--accent); position: relative; font-size: 0.9rem; }}
        .pipeline-steps li::before {{ content: counter(step); position: absolute; left: 0.75rem; top: 0.75rem; width: 1.5rem; height: 1.5rem; background: var(--accent); color: white; border-radius: 50%; font-size: 0.75rem; font-weight: 700; display: flex; align-items: center; justify-content: center; }}
        .ref-list {{ list-style: none; padding: 0; }}
        .ref-list li {{ padding: 0.5rem 0; border-bottom: 1px solid var(--border); font-size: 0.9rem; }}
        .ref-list li:last-child {{ border-bottom: none; }}
        .limitations-list {{ padding-left: 1.2rem; }}
        .limitations-list li {{ margin-bottom: 0.4rem; font-size: 0.9rem; }}

        .chart-wrap {{ position: relative; width: 100%; }}
        .chart-wrap canvas {{ width: 100% !important; }}

        /* Assessment questionnaire */
        .assess-tier-picker {{ display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }}
        .assess-tier-card {{ flex: 1; min-width: 220px; padding: 1.5rem; background: var(--card); border: 2px solid var(--border); border-radius: 12px; cursor: pointer; transition: border-color 0.2s, box-shadow 0.2s; }}
        .assess-tier-card:hover {{ border-color: var(--accent); box-shadow: 0 2px 8px rgba(58,143,232,0.15); }}
        .assess-tier-card.selected {{ border-color: var(--accent); box-shadow: 0 0 0 3px rgba(58,143,232,0.2); }}
        .assess-tier-card h3 {{ font-size: 1.05rem; font-weight: 700; margin-bottom: 0.3rem; }}
        .assess-tier-card .tier-meta {{ font-size: 0.8rem; color: var(--muted); margin-bottom: 0.5rem; }}
        .assess-tier-card p {{ font-size: 0.88rem; line-height: 1.5; }}

        .assess-progress {{ display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1.5rem; }}
        .assess-progress-bar {{ flex: 1; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; }}
        .assess-progress-fill {{ height: 100%; background: var(--accent); border-radius: 3px; transition: width 0.3s ease; }}
        .assess-progress-text {{ font-size: 0.82rem; color: var(--muted); white-space: nowrap; font-variant-numeric: tabular-nums; }}

        .assess-question {{ background: var(--card); border-radius: 12px; border: 1px solid var(--border); padding: 1.5rem 2rem; margin-bottom: 1rem; transition: border-color 0.2s; }}
        .assess-question.answered {{ border-color: #3ABF5E; }}
        .assess-question .q-domain {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; margin-bottom: 0.4rem; }}
        .assess-question .q-text {{ font-size: 1rem; font-weight: 500; margin-bottom: 1rem; line-height: 1.5; }}
        .assess-likert {{ display: flex; justify-content: space-between; gap: 0.4rem; }}
        .assess-likert label {{ flex: 1; text-align: center; cursor: pointer; }}
        .assess-likert input[type="radio"] {{ display: none; }}
        .assess-likert .likert-btn {{ display: block; padding: 0.5rem 0; border: 2px solid var(--border); border-radius: 8px; font-size: 0.95rem; font-weight: 600; transition: all 0.15s; user-select: none; }}
        .assess-likert .likert-btn:hover {{ border-color: var(--accent); background: rgba(58,143,232,0.05); }}
        .assess-likert input[type="radio"]:checked + .likert-btn {{ border-color: var(--accent); background: var(--accent); color: white; }}
        .assess-likert-labels {{ display: flex; justify-content: space-between; font-size: 0.72rem; color: var(--muted); margin-top: 0.3rem; padding: 0 0.5rem; }}

        .assess-submit {{ display: inline-block; padding: 0.75rem 2rem; background: var(--accent); color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background 0.15s; }}
        .assess-submit:hover {{ background: #2d7ad6; }}
        .assess-submit:disabled {{ background: #aaa; cursor: not-allowed; }}
        .assess-back {{ display: inline-block; padding: 0.75rem 1.5rem; background: transparent; color: var(--muted); border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; cursor: pointer; margin-right: 0.75rem; }}
        .assess-back:hover {{ background: var(--bg); }}

        .assess-results {{ animation: tabFadeIn 0.3s ease; }}
        .assess-results .result-type-card {{ background: var(--card); border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; margin-bottom: 1.5rem; }}
        .assess-results .result-type-header {{ padding: 1.5rem 2rem; color: white; }}
        .assess-results .result-type-name {{ font-size: 1.6rem; font-weight: 700; font-style: italic; font-family: Georgia, "Times New Roman", serif; }}
        .assess-results .result-type-tagline {{ font-size: 0.95rem; margin-top: 0.3rem; opacity: 0.9; }}
        .assess-results .result-type-profile {{ font-size: 0.82rem; margin-top: 0.4rem; opacity: 0.7; }}
        .assess-results .result-body {{ padding: 1.5rem 2rem; }}
        .assess-results .result-domains {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; }}
        @media (max-width: 768px) {{ .assess-results .result-domains {{ grid-template-columns: 1fr; }} }}
        .assess-results .result-domain {{ padding: 1rem; border-radius: 8px; border: 1px solid var(--border); }}
        .assess-results .result-domain h4 {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.3rem; }}
        .assess-results .result-domain .domain-scores {{ font-size: 0.88rem; margin-bottom: 0.4rem; }}
        .assess-results .result-strengths {{ margin-bottom: 1.5rem; }}
        .assess-results .result-strengths h4 {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin-bottom: 0.5rem; }}
        .assess-results .result-strengths ul {{ list-style: none; padding: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem; }}
        .assess-results .result-strengths li {{ background: #f8f9fa; padding: 0.6rem 1rem; border-radius: 6px; font-size: 0.88rem; border-left: 3px solid var(--accent); }}
        .assess-results .result-growth {{ background: #faf8f0; padding: 1rem 1.2rem; border-radius: 8px; margin-bottom: 1.5rem; }}
        .assess-results .result-growth h4 {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; color: #8a7a5a; margin-bottom: 0.4rem; }}
        .assess-results .result-growth p {{ font-size: 0.88rem; line-height: 1.6; }}
        .assess-results .result-sigs {{ margin-bottom: 1.5rem; }}
        .assess-results .result-sigs h4 {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin-bottom: 0.5rem; }}
    </style>
</head>
<body>

    <button class="hamburger" id="hamburger" aria-label="Toggle navigation">&#9776;</button>
    <div class="nav-overlay" id="nav-overlay"></div>

    <aside class="sidebar" id="sidebar">
        <div class="sidebar-title">ABC Assessment</div>
        <div class="sidebar-subtitle">Simulation Dashboard</div>

        <div class="sim-sidebar">
            <label>Participants</label>
            <div class="sim-row">
                <input type="range" id="sim-n" min="50" max="10000" step="50" value="1000">
                <span class="val" id="sim-n-val">1,000</span>
            </div>
            <label>Noise (SD)</label>
            <div class="sim-row">
                <input type="range" id="sim-noise" min="0.3" max="2.0" step="0.1" value="1.0">
                <span class="val" id="sim-noise-val">1.0</span>
            </div>
            <button class="sim-run-btn" id="sim-run-btn" onclick="runSimulation()">Run Simulation</button>
            <span class="sim-status" id="sim-status"></span>
        </div>

        <nav>
            <a class="nav-item active" data-tab="overview">Overview</a>
            <a class="nav-item" data-tab="types">Types</a>
            <a class="nav-item" data-tab="states">Domain States</a>
            <a class="nav-item" data-tab="belbin">Belbin Roles</a>
            <a class="nav-item" data-tab="risk">Risk Signals</a>
            <a class="nav-item" data-tab="assessment">Assessment</a>
            <a class="nav-item" data-tab="participants">Participants</a>
            <a class="nav-item" data-tab="methodology">Methodology</a>
        </nav>
        <div class="sidebar-footer" id="sidebar-footer">Ready</div>
    </aside>

    <div class="main">

        <!-- TAB: Overview -->
        <div class="tab-content active" id="tab-overview">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Overview</h1>
                    <p>The 6-factor model measures satisfaction and frustration across three domains: Ambition, Belonging, and Craft.</p>
                </div>
                <div class="stats-bar" id="overview-stats">
                    <div class="stat"><div class="stat-value" id="ov-n">&mdash;</div><div class="stat-label">Participants</div></div>
                    <div class="stat"><div class="stat-value" id="ov-types">&mdash;</div><div class="stat-label">Types Observed</div></div>
                    <div class="stat"><div class="stat-value" id="ov-vuln">&mdash;</div><div class="stat-label">Vulnerable %</div></div>
                    <div class="stat"><div class="stat-value" id="ov-roles">&mdash;</div><div class="stat-label">Avg Roles / Person</div></div>
                    <div class="stat"><div class="stat-value" id="ov-sigs">&mdash;</div><div class="stat-label">With Risk Signals</div></div>
                </div>
                <div class="section">
                    <h2>Validation Gates</h2>
                    <p class="desc">R/lavaan CFA and Python scoring pipeline verified these thresholds.</p>
                    <div class="validation-grid">
                        <div class="gate"><div class="gate-label">Scoring Correlation</div><div class="gate-value">r = 1.000</div><div class="gate-target">Target: &ge; 0.85 per subscale</div></div>
                        <div class="gate"><div class="gate-label">Domain State Accuracy</div><div class="gate-value">100.0%</div><div class="gate-target">Target: &ge; 80%</div></div>
                        <div class="gate"><div class="gate-label">Vulnerable Sensitivity</div><div class="gate-value">100.0%</div><div class="gate-target">Target: &ge; 75%</div></div>
                        <div class="gate"><div class="gate-label">Max Type Frequency</div><div class="gate-value" id="ov-max-type">&mdash;</div><div class="gate-target">Target: &le; 15%</div></div>
                        <div class="gate"><div class="gate-label">CFA Model Fit (CFI)</div><div class="gate-value">1.000</div><div class="gate-target">Target: &ge; 0.95</div></div>
                        <div class="gate"><div class="gate-label">Code Coverage</div><div class="gate-value">97.5%</div><div class="gate-target">Target: &ge; 85%</div></div>
                    </div>
                </div>
                <div class="section">
                    <h2>Subscale Summary</h2>
                    <p class="desc">Mean scores on the 0-10 normalised scale. Error bars show &pm;1 SD.</p>
                    <div class="card" style="padding:1rem;"><div class="chart-wrap"><canvas id="chart-ov-subscales"></canvas></div></div>
                </div>
            </div>
        </div>

        <!-- TAB: Types -->
        <div class="tab-content" id="tab-types">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Types</h1>
                    <p>The scoring pipeline assigns each participant one of 24 motivational types — 6 base types (from primary and secondary satisfaction domains) combined with 4 state modifiers (from the primary domain's satisfaction-frustration balance).</p>
                </div>
                <div class="section">
                    <h2>Type Distribution</h2>
                    <p class="desc">Bar colour marks the dominant domain: red for Ambition, blue for Belonging, green for Craft.</p>
                    <div class="card" style="padding:1rem;"><div class="chart-wrap" style="height:480px;"><canvas id="chart-types"></canvas></div></div>
                </div>
                <div class="section">
                    <h2>Type Guide</h2>
                    <p class="desc">Click a type to see its profile, strengths, typical subscale pattern, and growth edge.</p>
                    <div id="type-guide-index"></div>
                    <div id="type-guide-detail"></div>
                </div>
            </div>
        </div>

        <!-- TAB: Domain States -->
        <div class="tab-content" id="tab-states">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Domain States</h1>
                    <p>Crossing satisfaction and frustration at 5.5 classifies each domain into one of four states: Thriving, Vulnerable, Mild, or Distressed.</p>
                </div>
                <div class="section">
                    <h2>State Distribution</h2>
                    <div class="grid-2">
                        <div class="card" style="padding:1rem;"><div class="chart-wrap"><canvas id="chart-states"></canvas></div></div>
                        <div class="card" style="padding:0;"><table><thead><tr><th>Domain</th><th>State</th><th>Count</th><th>%</th></tr></thead><tbody id="states-table-body"></tbody></table></div>
                    </div>
                </div>
                <div class="section">
                    <h2>Satisfaction vs Frustration</h2>
                    <p class="desc">Each dot represents one participant. Dashed lines at 5.5 divide the four state quadrants.</p>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;">
                        <div class="card" style="padding:1rem;"><div class="chart-wrap"><canvas id="chart-scatter-ambition"></canvas></div></div>
                        <div class="card" style="padding:1rem;"><div class="chart-wrap"><canvas id="chart-scatter-belonging"></canvas></div></div>
                        <div class="card" style="padding:1rem;"><div class="chart-wrap"><canvas id="chart-scatter-craft"></canvas></div></div>
                    </div>
                </div>
                <div class="section">
                    <h2>The Four States</h2>
                    <p class="desc">Satisfaction (horizontal) and frustration (vertical) cross at 5.5 to form four quadrants. Click any cell for the full profile including mental fatigue risk.</p>
                    <div class="ds-quadrant-wrap">
                        <div class="ds-axis-y">Satisfaction &uarr;</div>
                        <div>
                            <div style="display:flex;justify-content:space-between;padding:0 0.5rem;margin-bottom:0.3rem;">
                                <span class="ds-axis-label">High Frustration</span>
                                <span class="ds-axis-label">Low Frustration</span>
                            </div>
                            <div id="states-quadrant"></div>
                        </div>
                    </div>
                    <div id="states-detail-container"></div>
                </div>
            </div>
        </div>

        <!-- TAB: Belbin Roles -->
        <div class="tab-content" id="tab-belbin">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Belbin Roles</h1>
                    <p>Subscale score patterns map each participant to one or more Belbin team roles.</p>
                </div>
                <div class="section">
                    <h2>Role Distribution</h2>
                    <p class="desc">One participant can hold several roles. Percentages sum to more than 100%.</p>
                    <div class="grid-2">
                        <div class="card" style="padding:1rem;"><div class="chart-wrap"><canvas id="chart-belbin"></canvas></div></div>
                        <div class="card" style="padding:0;"><table><thead><tr><th>Role (Qualifier)</th><th>Count</th><th>% of Participants</th></tr></thead><tbody id="belbin-table-body"></tbody></table></div>
                    </div>
                </div>
                <div class="section">
                    <h2>Role Guide</h2>
                    <p class="desc">Click a role to see its definition, ABC alignment, and the types most likely to hold it.</p>
                    <div id="belbin-guide-index"></div>
                    <div id="belbin-guide-detail"></div>
                </div>
            </div>
        </div>

        <!-- TAB: Risk Signals -->
        <div class="tab-content" id="tab-risk">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Risk Signals</h1>
                    <p>Frustration signatures flag participants whose score patterns signal psychological strain.</p>
                </div>
                <div class="section">
                    <h2>Frustration Signatures</h2>
                    <p class="desc">High frustration paired with extreme satisfaction scores reveals six distinct strain patterns.</p>
                    <div class="card" style="padding:0;"><table><thead><tr><th>Signature</th><th>Risk</th><th>Count</th><th>% of Participants</th></tr></thead><tbody id="frust-table-body"></tbody></table></div>
                </div>
                <div class="section">
                    <h2>Score Distributions</h2>
                    <p class="desc">How subscale scores (0-10) and Big Five percentiles spread across the population.</p>
                    <div class="grid-2">
                        <div class="card" style="padding:1rem;"><div class="chart-wrap"><canvas id="chart-subscales"></canvas></div></div>
                        <div class="card" style="padding:1rem;"><div class="chart-wrap"><canvas id="chart-bigfive"></canvas></div></div>
                    </div>
                </div>
                <div class="section">
                    <h2>Subscale Statistics</h2>
                    <div class="card" style="padding:0;"><table><thead><tr><th>Subscale</th><th>Mean</th><th>SD</th><th>Min</th><th>Max</th></tr></thead><tbody id="subscale-stats-body"></tbody></table></div>
                </div>
            </div>
        </div>

        <!-- TAB: Participants -->
        <div class="tab-content" id="tab-participants">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Individual Participants</h1>
                    <p>Click a row to see the full profile. Search, filter, or click column headers to sort.</p>
                </div>
                <div class="controls">
                    <input type="text" id="search-input" placeholder="Search by ID, type, domain, or state...">
                    <select id="type-filter"><option value="">All Types</option></select>
                    <select id="domain-filter"><option value="">All Domains</option><option value="Ambition">Ambition</option><option value="Belonging">Belonging</option><option value="Craft">Craft</option></select>
                    <select id="state-filter"><option value="">All States</option><option value="Thriving">Thriving</option><option value="Vulnerable">Vulnerable</option><option value="Mild">Mild</option><option value="Distressed">Distressed</option></select>
                    <span class="count" id="row-count"></span>
                    <button class="export-btn" onclick="exportCSV()">Export CSV</button>
                </div>
                <div class="card participants-wrap">
                    <table id="participants-table">
                        <thead><tr>
                            <th data-key="id"># <span class="sort-arrow">&#9650;</span></th>
                            <th data-key="type">Type <span class="sort-arrow">&#9650;</span></th>
                            <th data-key="domain">Domain <span class="sort-arrow">&#9650;</span></th>
                            <th data-key="a_state">A-State <span class="sort-arrow">&#9650;</span></th>
                            <th data-key="b_state">B-State <span class="sort-arrow">&#9650;</span></th>
                            <th data-key="c_state">C-State <span class="sort-arrow">&#9650;</span></th>
                            <th data-key="a_sat">A-Sat <span class="sort-arrow">&#9650;</span></th>
                            <th data-key="a_frust">A-Frust <span class="sort-arrow">&#9650;</span></th>
                            <th data-key="b_sat">B-Sat <span class="sort-arrow">&#9650;</span></th>
                            <th data-key="b_frust">B-Frust <span class="sort-arrow">&#9650;</span></th>
                            <th data-key="c_sat">C-Sat <span class="sort-arrow">&#9650;</span></th>
                            <th data-key="c_frust">C-Frust <span class="sort-arrow">&#9650;</span></th>
                        </tr></thead>
                        <tbody id="participants-body"></tbody>
                    </table>
                </div>
                <div id="participant-detail" class="card detail-wrap" style="display:none;margin-top:1rem;"></div>
            </div>
        </div>

        <!-- TAB: Assessment -->
        <div class="tab-content" id="tab-assessment">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Take an Assessment</h1>
                    <p>Experience the ABC Assessment as a user would. Choose a tier, answer the questions, and see your motivational profile.</p>
                </div>

                <!-- Tier picker -->
                <div id="assess-picker">
                    <div class="assess-tier-picker">
                        <div class="assess-tier-card" data-tier="onboarding" onclick="selectTier('onboarding')">
                            <h3>Onboarding</h3>
                            <div class="tier-meta">6 items &middot; ~2 minutes</div>
                            <p>Quick first impression. One satisfaction and one frustration item per domain gives an early signal of your motivational shape.</p>
                        </div>
                        <div class="assess-tier-card" data-tier="standard" onclick="selectTier('standard')">
                            <h3>Standard</h3>
                            <div class="tier-meta">12 items &middot; ~4 minutes</div>
                            <p>Stronger signal within the first two weeks. Two items per subscale sharpens the profile and adds confidence to the archetype.</p>
                        </div>
                        <div class="assess-tier-card" data-tier="full" onclick="selectTier('full')">
                            <h3>Full Assessment</h3>
                            <div class="tier-meta">24 items &middot; ~8 minutes</div>
                            <p>The complete validated instrument. Four items per subscale produces reliable subscale means, type assignment, and risk signals.</p>
                        </div>
                    </div>
                </div>

                <!-- Questions area -->
                <div id="assess-questions" style="display:none;">
                    <div class="assess-progress">
                        <button class="assess-back" onclick="backToTierPicker()">Back</button>
                        <div class="assess-progress-bar"><div class="assess-progress-fill" id="assess-progress-fill"></div></div>
                        <span class="assess-progress-text" id="assess-progress-text">0 / 6</span>
                    </div>
                    <div id="assess-items-container"></div>
                    <div style="text-align:center;margin-top:1.5rem;">
                        <button class="assess-submit" id="assess-submit-btn" onclick="submitAssessment()" disabled>See Your Results</button>
                    </div>
                </div>

                <!-- Results area -->
                <div id="assess-results" class="assess-results" style="display:none;"></div>
            </div>
        </div>

        <!-- TAB: Methodology -->
        <div class="tab-content" id="tab-methodology">
            <div class="tab-inner">
                <div class="tab-header"><h1>Methodology</h1><p>Ten steps turn raw Likert responses into typed profiles. This section explains the pipeline, its validation, and its limits.</p></div>
                <div class="section">
                    <h2>How the Simulation Generates Data</h2>
                    <p class="desc">The dashboard generates synthetic participants in your browser using fixed statistical parameters. Graphs will show a consistent spread across runs. This is deliberate: the simulation validates the scoring pipeline under controlled conditions, not the variance of a real population.</p>
                    <ul class="limitations-list">
                        <li><strong>Fixed distribution parameters.</strong> Six subscale scores are drawn from independent normal distributions with tuned means. These offsets ensure no single type exceeds 15% of the population.</li>
                        <li><strong>Independent subscales.</strong> The simulation uses an identity correlation matrix (zero inter-subscale correlation). Real respondent data will introduce natural correlations between domains.</li>
                        <li><strong>Convergence at scale.</strong> With hundreds or thousands of participants, every run converges to the same shape. The noise slider controls item-level variance, but the population-level distribution stays stable.</li>
                    </ul>
                    <p class="desc">Empirical data will replace these fixed parameters and introduce the natural skews, correlations, and variance that real populations produce.</p>
                </div>
                <div class="section">
                    <h2>Scoring Pipeline</h2>
                    <p class="desc">From raw responses to typed profiles with team roles and risk flags.</p>
                    <ol class="pipeline-steps">
                        <li><strong>Ingest raw responses</strong> &mdash; Collect 24 items on a 1-7 Likert scale across three domains (Ambition, Belonging, Craft), each split into satisfaction and frustration subscales.</li>
                        <li><strong>Reverse-score frustration items</strong> &mdash; Recode items AS4, AF4, BS4, BF4, CS4, CF4 as (8 &minus; raw).</li>
                        <li><strong>Compute subscale means</strong> &mdash; Average four items per subscale to produce six raw means.</li>
                        <li><strong>Normalise to 0-10</strong> &mdash; Convert each subscale mean from the 1-7 range: score = (mean &minus; 1) &times; 10 / 6.</li>
                        <li><strong>Classify domain states</strong> &mdash; Cross satisfaction (threshold&nbsp;6.46) and frustration (threshold&nbsp;4.38) to assign Thriving, Vulnerable, Mild, or Distressed per domain.</li>
                        <li><strong>Find the dominant domain</strong> &mdash; Select the domain with the highest satisfaction score. Ties break by domain order. Dominance orients which need is strongest — it does not imply the other domains matter less. Satisfaction and frustration across all three domains tell the full story.</li>
                        <li><strong>Infer Big Five percentiles</strong> &mdash; Centre each subscale ((score&nbsp;&minus;&nbsp;5)&nbsp;/&nbsp;5), then dot-product with a covariance-aware, domain-anchored weight matrix. Convert to percentiles: 50&nbsp;+&nbsp;z&nbsp;&times;&nbsp;30, clamped to [1,&nbsp;99]. Weights are optimised against the input covariance structure to produce near-zero inter-trait correlations (&lt;&nbsp;0.02) and balanced primary-trait distribution (~20% each), validated against Gosling&nbsp;et&nbsp;al.&nbsp;(2003) empirical benchmarks. Big Five is internal only — used for validation and Belbin inference, not displayed to end users.</li>
                        <li><strong>Assign type</strong> &mdash; Two-layer system: (1)&nbsp;125 profile combinations classify each domain's satisfaction into 5 levels (Very High, High, Medium, Low, Very Low). (2)&nbsp;24 named archetypes from 8 binary base patterns (sat&nbsp;&ge;&nbsp;5.5 = Strong per domain, 2&sup3;&nbsp;=&nbsp;8) &times; 3 frustration modifiers (count of domains with frust&nbsp;&ge;&nbsp;5.0: Steady/Striving/Resolute). All three domains are always represented.</li>
                        <li><strong>Map Belbin roles</strong> &mdash; Domain satisfaction ranking selects top two clusters (Thinking/People/Action, per Aranzabal&nbsp;et&nbsp;al.&nbsp;2022; tertiary excluded). Big Five percentiles differentiate roles within each cluster. Role score = domain affinity &times; trait percentile. Affinity: primary&nbsp;1.0, secondary&nbsp;0.5, tertiary&nbsp;0.0. Roles above 0.30 fire; the top role always fires.</li>
                        <li><strong>Flag frustration signatures</strong> &mdash; Detect strain patterns where frustration&nbsp;&ge;&nbsp;4.38. High satisfaction (≥&nbsp;6.46) + high frustration = medium risk. Low satisfaction (&lt;&nbsp;6.46) + high frustration = high risk. No gap zone.</li>
                    </ol>
                </div>
                <div class="section">
                    <h2>Limitations</h2>
                    <ul class="limitations-list">
                        <li><strong>Synthetic data only.</strong> Parametric distributions generated every participant. No real respondents contributed data.</li>
                        <li><strong>No empirical validation yet.</strong> The pipeline verifies against its own generative model, not external data.</li>
                        <li><strong>Population assumptions.</strong> The simulation uses independent domains with means centered at type thresholds to produce an unbiased distribution. Real population correlations and skews will emerge from actual respondent data.</li>
                        <li><strong>Big Five estimates are inferential.</strong> The weight matrix approximates Big Five percentiles from subscale patterns using covariance-aware optimisation (inter-trait |r|&nbsp;&lt;&nbsp;0.02, Gosling&nbsp;et&nbsp;al.&nbsp;2003 benchmark). No validated Big Five instrument underpins it. Types are derived from the satisfaction profile directly, not from inferred traits.</li>
                        <li><strong>Belbin roles rest on heuristics.</strong> Domain satisfaction selects a cluster (Thinking/People/Action) and Big Five percentiles differentiate within it — not a Belbin instrument. Role scores are continuous (domain affinity &times; trait percentile), not binary thresholds.</li>
                        <li><strong>Thresholds are calibrated to the simulation.</strong> Domain states use 5.5; type modifiers use split thresholds (sat 6.46, frust 4.38) calibrated to the discrete score distribution. Both may shift with empirical data.</li>
                    </ul>
                </div>
                <div class="section">
                    <h2>References</h2>
                    <ul class="ref-list">
                        <li>Deci, E. L., &amp; Ryan, R. M. (2000). The &ldquo;what&rdquo; and &ldquo;why&rdquo; of goal pursuits. <em>Psychological Inquiry, 11</em>(4), 227-268.</li>
                        <li>Vansteenkiste, M., &amp; Ryan, R. M. (2013). On psychological growth and vulnerability. <em>Journal of Psychotherapy Integration, 23</em>(3), 263-280.</li>
                        <li>Costa, P. T., &amp; McCrae, R. R. (1992). <em>Revised NEO Personality Inventory.</em> Psychological Assessment Resources.</li>
                    </ul>
                </div>
            </div>
        </div>

    </div>

    <script>
    /* ═══════════════════════════════════════════════════
       DATA CONSTANTS
       ═══════════════════════════════════════════════════ */
    const TYPE_DESCS = {type_desc_json};
    const STATE_DESCS = {state_desc_json};

    const DOMAIN_COLOURS = {{Ambition:"#E8563A",Belonging:"#3A8FE8",Craft:"#3ABF5E",ambition:"#E8563A",belonging:"#3A8FE8",craft:"#3ABF5E"}};
    const STATE_COLOURS = {{Thriving:"#3ABF5E",Vulnerable:"#F5A623",Mild:"#A0A0A0",Distressed:"#E8563A"}};
    const ITEM_ORDER = ["AS1","AS2","AS3","AS4","AF1","AF2","AF3","AF4","BS1","BS2","BS3","BS4","BF1","BF2","BF3","BF4","CS1","CS2","CS3","CS4","CF1","CF2","CF3","CF4"];
    const SUB_KEYS = ["a_sat","a_frust","b_sat","b_frust","c_sat","c_frust"];
    const SUB_LABELS = ["A-Sat","A-Frust","B-Sat","B-Frust","C-Sat","C-Frust"];
    const SUB_COLOURS = ["#E8563A","#E8563A","#3A8FE8","#3A8FE8","#3ABF5E","#3ABF5E"];
    const PREFIXES = ["AS","AF","BS","BF","CS","CF"];

    // Unbiased simulation: identity correlation matrix.
    // All 6 subscales are fully independent — no correlations that could
    // favour any type combination. Real data will reveal true correlations.
    const CORR = [
        [ 1.00, 0.00, 0.00, 0.00, 0.00, 0.00],
        [ 0.00, 1.00, 0.00, 0.00, 0.00, 0.00],
        [ 0.00, 0.00, 1.00, 0.00, 0.00, 0.00],
        [ 0.00, 0.00, 0.00, 1.00, 0.00, 0.00],
        [ 0.00, 0.00, 0.00, 0.00, 1.00, 0.00],
        [ 0.00, 0.00, 0.00, 0.00, 0.00, 1.00]
    ];

    const B5_WEIGHTS = {{
        openness:          [ 0.12, 0.16,-0.36,-0.35, 0.52, 0.33],
        conscientiousness: [ 0.03, 0.13, 0.20, 0.30, 0.18,-0.45],
        extraversion:      [ 0.47, 0.02, 0.27, 0.19,-0.12, 0.11],
        agreeableness:     [-0.23, 0.19, 0.43,-0.13, 0.08, 0.18],
        neuroticism:       [ 0.00, 0.24, 0.05, 0.41,-0.03, 0.05]
    }};

    const B5_TRAITS = ["openness","conscientiousness","extraversion","agreeableness","neuroticism"];
    const B5_LABELS = ["Openness","Conscientiousness","Extraversion","Agreeableness","Neuroticism"];
    const B5_COLOURS = ["#9B59B6","#2ECC71","#E67E22","#3498DB","#E74C3C"];

    // Motivational type system: 24 types = 8 base patterns × 3 frustration modifiers
    // Base pattern: binary sat threshold per domain (Strong >= 5.5 / Developing < 5.5)
    // Modifier: count of domains with frust >= 5.0
    const BASE_PATTERNS = {{
        "1,1,1": "Integrator",   // A↑ B↑ C↑
        "1,1,0": "Captain",      // A↑ B↑ C↓
        "1,0,1": "Architect",    // A↑ B↓ C↑
        "0,1,1": "Mentor",       // A↓ B↑ C↑
        "1,0,0": "Pioneer",      // A↑ B↓ C↓
        "0,1,0": "Anchor",       // A↓ B↑ C↓
        "0,0,1": "Artisan",      // A↓ B↓ C↑
        "0,0,0": "Seeker"        // A↓ B↓ C↓
    }};
    const TYPE_SAT_THRESHOLD = 5.5;    // activation threshold for base pattern
    const TYPE_FRUST_THRESHOLD = 5.0;  // frustration count threshold for modifier
    // Domain state thresholds (separate from type thresholds)
    const DOM_SAT_THRESHOLD = 6.46;
    const DOM_FRUST_THRESHOLD = 4.38;
    // Frustration signature thresholds (aligned with domain states)
    const FRUST_SIG_SAT_THRESHOLD = 6.46;
    const FRUST_SIG_FRUST_THRESHOLD = 4.38;

    const FRUST_LABELS = {{
        ambition:  {{ medium: "Blocked Drive", high: "Controlled Motivation" }},
        belonging: {{ medium: "Conditional Belonging", high: "Active Exclusion" }},
        craft:     {{ medium: "Evaluated Mastery", high: "Competence Threat" }}
    }};

    const SUBSCALE_GROUPS = [
        {{label:"Ambition Sat",items:["AS1","AS2","AS3","AS4"],colour:"#E8563A"}},
        {{label:"Ambition Frust",items:["AF1","AF2","AF3","AF4"],colour:"#E8563A"}},
        {{label:"Belonging Sat",items:["BS1","BS2","BS3","BS4"],colour:"#3A8FE8"}},
        {{label:"Belonging Frust",items:["BF1","BF2","BF3","BF4"],colour:"#3A8FE8"}},
        {{label:"Craft Sat",items:["CS1","CS2","CS3","CS4"],colour:"#3ABF5E"}},
        {{label:"Craft Frust",items:["CF1","CF2","CF3","CF4"],colour:"#3ABF5E"}}
    ];

    const BIG_FIVE_KEYS = [
        {{key:"O",label:"Openness",colour:"#9B59B6"}},
        {{key:"C",label:"Conscientiousness",colour:"#2ECC71"}},
        {{key:"E",label:"Extraversion",colour:"#E67E22"}},
        {{key:"A",label:"Agreeableness",colour:"#3498DB"}},
        {{key:"N",label:"Neuroticism",colour:"#E74C3C"}}
    ];

    const BELBIN_COLOURS = {{
        "Plant (Creative)":"#27AE60","Plant (Conceptual)":"#27AE60",
        "Specialist (Deep Mastery)":"#3ABF5E","Specialist (Focused)":"#3ABF5E",
        "Monitor-Evaluator (Vigilant)":"#F5A623","Monitor-Evaluator (Analytical)":"#F5A623",
        "Teamworker (Anchor)":"#3A8FE8","Teamworker (Supportive)":"#3A8FE8",
        "Resource Investigator (Networker)":"#A0A0A0","Resource Investigator (Curious)":"#A0A0A0",
        "Coordinator (Balanced)":"#9B59B6","Coordinator (Structured)":"#9B59B6",
        "Shaper (Inspiring)":"#E8563A","Shaper (Driving)":"#C0392B",
        "Implementer (Systematic)":"#2ECC71","Implementer (Practical)":"#2ECC71",
        "Completer-Finisher (Quality Driven)":"#E67E22","Completer-Finisher (Thorough)":"#E67E22"
    }};

    /* ═══════════════════════════════════════════════════
       MATH UTILITIES
       ═══════════════════════════════════════════════════ */
    function cholesky(A) {{
        const n = A.length;
        const L = Array.from({{length:n}}, () => new Float64Array(n));
        for (let i = 0; i < n; i++)
            for (let j = 0; j <= i; j++) {{
                let s = 0;
                for (let k = 0; k < j; k++) s += L[i][k] * L[j][k];
                L[i][j] = (i === j) ? Math.sqrt(A[i][i] - s) : (A[i][j] - s) / L[j][j];
            }}
        return L;
    }}

    function randn() {{
        let u, v, s;
        do {{ u = Math.random()*2-1; v = Math.random()*2-1; s = u*u+v*v; }} while (s >= 1 || s === 0);
        return u * Math.sqrt(-2 * Math.log(s) / s);
    }}

    function normCDF(x) {{
        const a1=0.254829592, a2=-0.284496736, a3=1.421413741, a4=-1.453152027, a5=1.061405429, p=0.3275911;
        const sign = x < 0 ? -1 : 1;
        x = Math.abs(x);
        const t = 1/(1+p*x);
        const y = 1 - (((((a5*t+a4)*t)+a3)*t+a2)*t+a1)*t*Math.exp(-x*x);
        return 0.5*(1+sign*y);
    }}

    function round2(v) {{ return Math.round(v * 100) / 100; }}

    /* ═══════════════════════════════════════════════════
       SIMULATION ENGINE
       ═══════════════════════════════════════════════════ */
    function simulatePopulation(n, noiseMult) {{
        const L = cholesky(CORR);
        const domainPairs = [["ambition","a_sat","a_frust"],["belonging","b_sat","b_frust"],["craft","c_sat","c_frust"]];
        // Unbiased means: tuned so all 24 types land near ~4% each.
        // Sat z=0.24 compensates for reverse-scoring pulling mean below 5.5.
        // Frust z=-0.31 offsets the Resolute modifier's structural advantage
        // (it covers 2+3 frustrated domains vs 0 or 1 for the others).
        // Empirically validated: max type ~5.7%, all 24 present, no dominant type.
        const Z_MEANS = [0.24, -0.31, 0.24, -0.31, 0.24, -0.31];
        const results = [];

        for (let i = 0; i < n; i++) {{
            const z = new Float64Array(6);
            for (let j = 0; j < 6; j++) z[j] = randn() * noiseMult;

            const corr = new Float64Array(6);
            for (let j = 0; j < 6; j++) {{
                let s2 = 0;
                for (let k = 0; k <= j; k++) s2 += L[j][k] * z[k];
                corr[j] = s2 + Z_MEANS[j];
            }}

            // Generate item-level responses and compute subscale scores
            const responses = {{}};
            const subscales = {{}};
            for (let si = 0; si < 6; si++) {{
                const p = normCDF(corr[si]);
                const items = [];
                for (let item = 0; item < 4; item++) {{
                    const itemNoise = randn() * 0.3 * noiseMult;
                    const itemP = Math.max(0.001, Math.min(0.999, p + itemNoise * 0.15));
                    items.push(Math.max(1, Math.min(7, Math.round(itemP * 6 + 1))));
                }}
                // Store raw responses
                for (let j = 0; j < 4; j++) responses[PREFIXES[si] + (j + 1)] = items[j];
                // Reverse-score item 4
                const rev4 = 8 - items[3];
                const subscaleMean = (items[0] + items[1] + items[2] + rev4) / 4;
                subscales[SUB_KEYS[si]] = Math.max(0, Math.min(10, (subscaleMean - 1) * 10 / 6));
            }}

            // Domain states (split thresholds: sat 6.46, frust 4.38)
            const domainStates = {{}};
            for (const [dom, satK, frustK] of domainPairs) {{
                const sat = subscales[satK], frust = subscales[frustK];
                if (sat >= DOM_SAT_THRESHOLD && frust < DOM_FRUST_THRESHOLD) domainStates[dom] = "Thriving";
                else if (sat >= DOM_SAT_THRESHOLD && frust >= DOM_FRUST_THRESHOLD) domainStates[dom] = "Vulnerable";
                else if (sat < DOM_SAT_THRESHOLD && frust < DOM_FRUST_THRESHOLD) domainStates[dom] = "Mild";
                else domainStates[dom] = "Distressed";
            }}

            // Big Five (normalised z-scores so all traits have equal variance)
            const centred = SUB_KEYS.map(k => (subscales[k] - 5) / 5);
            const bigFive = {{}};
            for (const trait of B5_TRAITS) {{
                const w = B5_WEIGHTS[trait];
                let zz = 0, ssq = 0;
                for (let j = 0; j < 6; j++) {{ zz += w[j] * centred[j]; ssq += w[j] * w[j]; }}
                const sigma = Math.sqrt(ssq);
                const zNorm = sigma > 0 ? zz / sigma : zz;
                bigFive[trait] = Math.max(1, Math.min(99, Math.round(50 + zNorm * 30)));
            }}

            // Motivational type: 8 base patterns × 3 frustration modifiers = 24 types
            // Dominant domain: argmax of sat scores, ties broken by domain order
            const sats = [["ambition", subscales.a_sat],["belonging", subscales.b_sat],["craft", subscales.c_sat]];
            let domDomain = sats[0][0], domMax = sats[0][1];
            for (let si = 1; si < 3; si++) {{ if (sats[si][1] > domMax) {{ domMax = sats[si][1]; domDomain = sats[si][0]; }} }}

            // Base pattern: binary threshold per domain (Strong >= 5.5)
            const aStrong = subscales.a_sat >= TYPE_SAT_THRESHOLD ? 1 : 0;
            const bStrong = subscales.b_sat >= TYPE_SAT_THRESHOLD ? 1 : 0;
            const cStrong = subscales.c_sat >= TYPE_SAT_THRESHOLD ? 1 : 0;
            const baseName = BASE_PATTERNS[aStrong + "," + bStrong + "," + cStrong];

            // Modifier: count of frustrated domains (frust >= 5.0)
            let frustCount = 0;
            if (subscales.a_frust >= TYPE_FRUST_THRESHOLD) frustCount++;
            if (subscales.b_frust >= TYPE_FRUST_THRESHOLD) frustCount++;
            if (subscales.c_frust >= TYPE_FRUST_THRESHOLD) frustCount++;
            const modifier = frustCount === 0 ? "Steady" : frustCount === 1 ? "Striving" : "Resolute";
            const typeName = modifier + " " + baseName;

            // 125-profile code (5 sat levels)
            function satLevel(v) {{ if (v >= 8.0) return 5; if (v >= 6.0) return 4; if (v >= 4.0) return 3; if (v >= 2.0) return 2; return 1; }}
            const profileCode = satLevel(subscales.a_sat) + "-" + satLevel(subscales.b_sat) + "-" + satLevel(subscales.c_sat);

            // Belbin roles (cluster × Big Five architecture)
            const BELBIN_ROLE_DEFS = [
                {{role:"Plant", domain:"craft", trait:"openness", qN:"Creative", qM:"Conceptual"}},
                {{role:"Specialist", domain:"craft", trait:"conscientiousness", qN:"Deep Mastery", qM:"Focused"}},
                {{role:"Monitor-Evaluator", domain:"craft", trait:"neuroticism", qN:"Vigilant", qM:"Analytical"}},
                {{role:"Teamworker", domain:"belonging", trait:"agreeableness", qN:"Anchor", qM:"Supportive"}},
                {{role:"Resource Investigator", domain:"belonging", trait:"extraversion", qN:"Networker", qM:"Curious"}},
                {{role:"Coordinator", domain:"belonging", trait:"conscientiousness", qN:"Balanced", qM:"Structured"}},
                {{role:"Shaper", domain:"ambition", trait:"extraversion", qN:"Inspiring", qM:"Driving"}},
                {{role:"Implementer", domain:"ambition", trait:"conscientiousness", qN:"Systematic", qM:"Practical"}},
                {{role:"Completer-Finisher", domain:"ambition", trait:"neuroticism", qN:"Quality Driven", qM:"Thorough"}},
            ];
            const domSatMap = {{ambition: "a_sat", belonging: "b_sat", craft: "c_sat"}};
            const domOrder = ["ambition", "belonging", "craft"];
            // Tiny jitter breaks ties randomly (discrete items cause frequent ties,
            // and stable sort would otherwise always favour ambition > belonging > craft)
            const satArr = domOrder.map(d => ({{d, v: subscales[domSatMap[d]] + Math.random() * 0.001}}));
            satArr.sort((a,b) => b.v - a.v);
            const domRanks = {{}};
            satArr.forEach((item, i) => domRanks[item.d] = i);
            const affinityW = [1.0, 0.5, 0.0];
            const BELBIN_THRESH = 0.30;
            const scored = BELBIN_ROLE_DEFS.map(rd => {{
                const aff = affinityW[domRanks[rd.domain]];
                const tPct = bigFive[rd.trait];
                const score = aff * tPct / 100;
                const qual = tPct >= 60 ? rd.qN : rd.qM;
                return {{role: rd.role, qualifier: qual, score}};
            }});
            scored.sort((a,b) => b.score - a.score);
            const belbinRoles = [scored[0]];
            for (let i = 1; i < scored.length; i++) {{
                if (scored[i].score >= BELBIN_THRESH) belbinRoles.push(scored[i]);
            }}

            // Frustration signatures (split thresholds, no gap zone)
            const frustSigs = [];
            for (const [dom, satK, frustK] of domainPairs) {{
                const sat = subscales[satK], frust = subscales[frustK];
                if (frust >= FRUST_SIG_FRUST_THRESHOLD) {{
                    if (sat >= FRUST_SIG_SAT_THRESHOLD) frustSigs.push({{label: FRUST_LABELS[dom].medium, domain: dom, risk: "medium"}});
                    else frustSigs.push({{label: FRUST_LABELS[dom].high, domain: dom, risk: "high"}});
                }}
            }}

            results.push({{
                id: i+1, type: typeName, domain: domDomain.charAt(0).toUpperCase()+domDomain.slice(1),
                domDomain, subscales, domainStates, bigFive,
                a_state: domainStates.ambition, b_state: domainStates.belonging, c_state: domainStates.craft,
                a_sat: round2(subscales.a_sat), a_frust: round2(subscales.a_frust),
                b_sat: round2(subscales.b_sat), b_frust: round2(subscales.b_frust),
                c_sat: round2(subscales.c_sat), c_frust: round2(subscales.c_frust),
                O: bigFive.openness, C: bigFive.conscientiousness, E: bigFive.extraversion,
                A: bigFive.agreeableness, N: bigFive.neuroticism,
                profileCode, responses, belbin_roles: belbinRoles, frustration_signatures: frustSigs
            }});
        }}
        return results;
    }}

    /* ═══════════════════════════════════════════════════
       CHART MANAGEMENT
       ═══════════════════════════════════════════════════ */
    const charts = {{}};
    function destroyChart(id) {{ if (charts[id]) {{ charts[id].destroy(); delete charts[id]; }} }}
    function makeChart(id, config) {{ destroyChart(id); charts[id] = new Chart(document.getElementById(id), config); return charts[id]; }}

    /* ═══════════════════════════════════════════════════
       TAB UPDATE FUNCTIONS
       ═══════════════════════════════════════════════════ */
    let DATA = [];

    function updateOverview(results) {{
        const n = results.length;
        const nTypes = new Set(results.map(r => r.type)).size;
        let vulnCount = 0;
        results.forEach(r => {{ if (r.a_state==="Vulnerable"||r.b_state==="Vulnerable"||r.c_state==="Vulnerable") vulnCount++; }});
        const totalRoles = results.reduce((s,r) => s + r.belbin_roles.length, 0);
        const withSigs = results.filter(r => r.frustration_signatures.length > 0).length;

        // Max type frequency
        const tc = {{}};
        results.forEach(r => {{ tc[r.type] = (tc[r.type]||0)+1; }});
        const maxTypePct = Math.max(...Object.values(tc)) / n * 100;

        document.getElementById('ov-n').textContent = n.toLocaleString();
        document.getElementById('ov-types').textContent = nTypes;
        document.getElementById('ov-vuln').textContent = (vulnCount/n*100).toFixed(1) + '%';
        document.getElementById('ov-roles').textContent = (totalRoles/n).toFixed(1);
        document.getElementById('ov-sigs').textContent = (withSigs/n*100).toFixed(1) + '%';
        document.getElementById('ov-max-type').textContent = maxTypePct.toFixed(1) + '%';

        // Subscale summary chart
        const means = SUB_KEYS.map(k => {{ const v = results.map(r => r.subscales[k]); return v.reduce((a,b)=>a+b,0)/v.length; }});
        const sds = SUB_KEYS.map((k,i) => {{ const v = results.map(r => r.subscales[k]); const m = means[i]; return Math.sqrt(v.reduce((s,x)=>s+(x-m)**2,0)/v.length); }});

        makeChart('chart-ov-subscales', {{
            type: 'bar',
            data: {{
                labels: SUB_LABELS,
                datasets: [{{
                    data: means.map(m => +m.toFixed(2)),
                    backgroundColor: SUB_COLOURS.map(c => c + '99'),
                    borderColor: SUB_COLOURS,
                    borderWidth: 1,
                    errorBars: sds
                }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ min: 0, max: 10, title: {{ display: true, text: 'Score (0-10)' }} }} }} }},
            plugins: [{{
                id: 'errorBars',
                afterDraw(chart) {{
                    const ctx = chart.ctx;
                    const meta = chart.getDatasetMeta(0);
                    const ds = chart.data.datasets[0];
                    if (!ds.errorBars) return;
                    ctx.save();
                    ctx.strokeStyle = '#333';
                    ctx.lineWidth = 1.5;
                    meta.data.forEach((bar, i) => {{
                        const sd = ds.errorBars[i];
                        const yScale = chart.scales.y;
                        const mean = ds.data[i];
                        const yTop = yScale.getPixelForValue(mean + sd);
                        const yBot = yScale.getPixelForValue(mean - sd);
                        const x = bar.x;
                        ctx.beginPath(); ctx.moveTo(x, yTop); ctx.lineTo(x, yBot); ctx.stroke();
                        ctx.beginPath(); ctx.moveTo(x-4, yTop); ctx.lineTo(x+4, yTop); ctx.stroke();
                        ctx.beginPath(); ctx.moveTo(x-4, yBot); ctx.lineTo(x+4, yBot); ctx.stroke();
                    }});
                    ctx.restore();
                }}
            }}]
        }});
    }}

    // Store type stats globally for detail panel rendering
    let typeStats = {{ counts: {{}}, domains: {{}}, means: {{}} }};
    let activeTypeName = null;

    function updateTypes(results) {{
        const n = results.length;
        const tc = {{}}, td = {{}};
        results.forEach(r => {{ tc[r.type] = (tc[r.type]||0)+1; td[r.type] = r.domDomain; }});
        const sorted = Object.entries(tc).sort((a,b) => b[1]-a[1]);

        makeChart('chart-types', {{
            type: 'bar',
            data: {{
                labels: sorted.map(t => t[0]),
                datasets: [{{ data: sorted.map(t => t[1]), backgroundColor: sorted.map(t => DOMAIN_COLOURS[td[t[0]]] || '#666') }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, indexAxis: 'y', plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => ctx.raw + ' (' + (ctx.raw/n*100).toFixed(1) + '%)' }} }} }}, scales: {{ x: {{ title: {{ display: true, text: 'Count' }} }} }} }}
        }});

        // Compute mean subscales per type
        const typeSubs = {{}};
        results.forEach(r => {{
            if (!typeSubs[r.type]) typeSubs[r.type] = {{ count: 0, sums: {{a_sat:0,a_frust:0,b_sat:0,b_frust:0,c_sat:0,c_frust:0}} }};
            const t = typeSubs[r.type];
            t.count++;
            SUB_KEYS.forEach(k => {{ t.sums[k] += r.subscales[k]; }});
        }});
        const typeMeans = {{}};
        Object.entries(typeSubs).forEach(([name, t]) => {{
            typeMeans[name] = {{}};
            SUB_KEYS.forEach(k => {{ typeMeans[name][k] = t.sums[k] / t.count; }});
        }});
        typeStats = {{ counts: tc, domains: td, means: typeMeans, total: n }};

        // Build domain index cards
        const indexEl = document.getElementById('type-guide-index');
        const detailEl = document.getElementById('type-guide-detail');
        detailEl.innerHTML = '';
        activeTypeName = null;

        const observed = new Set(results.map(r => r.type));

        // Group types by base pattern (modifier stripped)
        const baseGroups = {{"Integrator":"All Strong","Captain":"A+B Strong","Architect":"A+C Strong","Mentor":"B+C Strong","Pioneer":"A Strong","Anchor":"B Strong","Artisan":"C Strong","Seeker":"All Developing"}};
        const baseColours = {{"Integrator":"#6c757d","Captain":"#C94A2E","Architect":"#5A9E4B","Mentor":"#2E7EC9","Pioneer":"#E8563A","Anchor":"#3A8FE8","Artisan":"#3ABF5E","Seeker":"#A0A0A0"}};
        const baseOrder = ["Integrator","Captain","Architect","Mentor","Pioneer","Anchor","Artisan","Seeker"];

        let indexHTML = '<div class="tg-index">';
        for (const base of baseOrder) {{
            const colour = baseColours[base];
            const baseTypes = ["Steady","Striving","Resolute"].map(m => m + " " + base).filter(n => observed.has(n));
            if (baseTypes.length === 0) continue;

            indexHTML += `<div class="tg-domain-card">`;
            indexHTML += `<div class="tg-domain-bar" style="background:${{colour}}"></div>`;
            indexHTML += `<div class="tg-domain-header">${{base}} <span style="font-size:0.75em;color:#999">${{baseGroups[base]}}</span></div>`;
            indexHTML += `<ul class="tg-type-list">`;
            for (const name of baseTypes) {{
                const count = tc[name] || 0;
                indexHTML += `<li class="tg-type-item" data-type="${{name}}"><span>${{name}}</span><span class="tg-item-count">${{count}}</span><span class="tg-chevron">&#8250;</span></li>`;
            }}
            indexHTML += `</ul></div>`;
        }}
        indexHTML += '</div>';
        indexEl.innerHTML = indexHTML;

        // Attach click handlers
        indexEl.querySelectorAll('.tg-type-item').forEach(item => {{
            item.addEventListener('click', () => {{
                const typeName = item.getAttribute('data-type');
                // Toggle active state
                indexEl.querySelectorAll('.tg-type-item').forEach(el => el.classList.remove('active'));
                if (activeTypeName === typeName) {{
                    detailEl.innerHTML = '';
                    activeTypeName = null;
                    return;
                }}
                item.classList.add('active');
                activeTypeName = typeName;
                renderTypeDetail(typeName);
                detailEl.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }});
        }});
    }}

    function renderTypeDetail(name) {{
        const detailEl = document.getElementById('type-guide-detail');
        const desc = TYPE_DESCS[name];
        if (!desc) {{ detailEl.innerHTML = ''; return; }}

        // Derive display info from pattern field
        const pattern = desc.pattern || {{}};
        const strongDomains = Object.entries(pattern).filter(([d,s]) => s === "strong").map(([d]) => d);
        const patternLabel = strongDomains.length === 3 ? "All Strong" :
            strongDomains.length === 0 ? "All Developing" :
            strongDomains.map(d => d.charAt(0).toUpperCase() + d.slice(1)).join(" + ") + " Strong";
        const domainColours = {{ambition:"#E8563A",belonging:"#3A8FE8",craft:"#3ABF5E"}};
        const colour = strongDomains.length === 1 ? domainColours[strongDomains[0]] :
            strongDomains.length === 0 ? '#A0A0A0' : '#6c757d';
        const count = typeStats.counts[name] || 0;
        const pct = typeStats.total ? (count / typeStats.total * 100).toFixed(1) : '0.0';
        const means = typeStats.means[name] || {{}};

        const subLabelsShort = ["A-Sat","A-Frust","B-Sat","B-Frust","C-Sat","C-Frust"];
        const subColours = ["#E8563A","#E8563A","#3A8FE8","#3A8FE8","#3ABF5E","#3ABF5E"];

        // ABC dots — strong domains are dominant, developing are secondary
        const dots = [
            {{ letter: 'A', colour: '#E8563A', dominant: pattern.ambition === 'strong' }},
            {{ letter: 'B', colour: '#3A8FE8', dominant: pattern.belonging === 'strong' }},
            {{ letter: 'C', colour: '#3ABF5E', dominant: pattern.craft === 'strong' }}
        ];
        const dotsHTML = dots.map(d => `<div class="tg-abc-dot ${{d.dominant ? 'dominant' : 'secondary'}}" style="background:${{d.colour}}">${{d.letter}}</div>`).join('');

        // Subscale bars
        let subsHTML = '';
        SUB_KEYS.forEach((k, i) => {{
            const val = means[k] || 0;
            const pctW = (val / 10 * 100).toFixed(1);
            subsHTML += `<div class="tg-sub-row"><span class="tg-sub-label">${{subLabelsShort[i]}}</span><div class="tg-sub-track"><div class="tg-sub-fill" style="width:${{pctW}}%;background:${{subColours[i]}}"></div><div class="tg-sub-threshold"></div></div><span class="tg-sub-val">${{val.toFixed(1)}}</span></div>`;
        }});

        // Strengths grid
        const strengthsHTML = (desc.strengths || []).map(s => `<div class="tg-strength-item">${{s}}</div>`).join('');

        detailEl.innerHTML = `<div class="tg-detail">
            <div class="tg-detail-header" style="background:${{colour}};color:white;">
                <div class="tg-domain-label">${{patternLabel}}</div>
                <div class="tg-name">${{name}}</div>
                <div class="tg-tagline">${{desc.tagline}}</div>
                <div class="tg-count">${{count}} participants (${{pct}}%)</div>
                <div class="tg-abc-dots">${{dotsHTML}}</div>
                <button class="tg-detail-close" onclick="document.getElementById('type-guide-detail').innerHTML='';activeTypeName=null;document.querySelectorAll('.tg-type-item').forEach(el=>el.classList.remove('active'));" title="Close">&times;</button>
            </div>
            <div class="tg-body">
                <p class="tg-desc">${{desc.description}}</p>

                <div class="tg-section-label">Strengths</div>
                <div class="tg-strengths">${{strengthsHTML}}</div>

                <div class="tg-two-col">
                    <div><div class="tg-section-label">Watch For</div><p>${{desc.watch_for}}</p></div>
                    <div><div class="tg-section-label">Typical Subscale Profile</div><div class="tg-subscales">${{subsHTML}}</div></div>
                </div>

                <div class="tg-growth"><div class="tg-section-label">Growth Edge</div><p>${{desc.growth_edge}}</p></div>
            </div>
            <div class="tg-footer">SDT Foundation &middot; Motivational Profile</div>
        </div>`;
    }}

    function updateDomainStates(results) {{
        const n = results.length;
        const domains = ["ambition","belonging","craft"];
        const stateNames = ["Thriving","Vulnerable","Mild","Distressed"];
        const stateColours = ["#3ABF5E","#F5A623","#A0A0A0","#E8563A"];

        // Stacked bar chart
        const stateData = {{}};
        stateNames.forEach(s => {{ stateData[s] = domains.map(d => results.filter(r => r.domainStates[d]===s).length); }});
        makeChart('chart-states', {{
            type: 'bar',
            data: {{ labels: ["Ambition","Belonging","Craft"], datasets: stateNames.map((s,i) => ({{ label:s, data:stateData[s], backgroundColor:stateColours[i] }})) }},
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'top' }} }}, scales: {{ x: {{ stacked: true }}, y: {{ stacked: true }} }} }}
        }});

        // Table
        let tableHTML = '';
        for (const d of domains) {{
            for (const s of stateNames) {{
                const c = results.filter(r => r.domainStates[d]===s).length;
                tableHTML += `<tr><td>${{d.charAt(0).toUpperCase()+d.slice(1)}}</td><td><span class="state-badge" style="background:${{STATE_COLOURS[s]}}">${{s}}</span></td><td class="num">${{c}}</td><td class="num">${{(c/n*100).toFixed(1)}}%</td></tr>`;
            }}
        }}
        document.getElementById('states-table-body').innerHTML = tableHTML;

        // Scatter plots with annotation plugin for threshold lines and labels
        const thresholdAnnotations = {{
            vLine: {{
                type: 'line', scaleID: 'x', value: DOM_SAT_THRESHOLD,
                borderColor: 'rgba(0,0,0,0.25)', borderWidth: 1, borderDash: [6, 4]
            }},
            hLine: {{
                type: 'line', scaleID: 'y', value: DOM_FRUST_THRESHOLD,
                borderColor: 'rgba(0,0,0,0.25)', borderWidth: 1, borderDash: [6, 4]
            }},
            lblDistressed: {{
                type: 'label', xValue: 1.2, yValue: 9.5,
                content: ['Distressed'], color: '#E8563A',
                font: {{ size: 13, style: 'italic' }}, backgroundColor: 'transparent'
            }},
            lblVulnerable: {{
                type: 'label', xValue: 8.8, yValue: 9.5,
                content: ['Vulnerable'], color: '#F5A623',
                font: {{ size: 13, style: 'italic' }}, backgroundColor: 'transparent'
            }},
            lblMild: {{
                type: 'label', xValue: 1.2, yValue: 0.5,
                content: ['Mild'], color: '#999999',
                font: {{ size: 13, style: 'italic' }}, backgroundColor: 'transparent'
            }},
            lblThriving: {{
                type: 'label', xValue: 8.8, yValue: 0.5,
                content: ['Thriving'], color: '#3ABF5E',
                font: {{ size: 13, style: 'italic' }}, backgroundColor: 'transparent'
            }}
        }};
        const domainInfo = [["ambition","a_sat","a_frust","chart-scatter-ambition","Ambition"],["belonging","b_sat","b_frust","chart-scatter-belonging","Belonging"],["craft","c_sat","c_frust","chart-scatter-craft","Craft"]];
        for (const [dom, satK, frustK, chartId, label] of domainInfo) {{
            // Add small jitter so discrete subscale values spread into a cloud
            const jitter = () => (Math.random() - 0.5) * 0.35;
            const points = results.map(r => ({{ x: r.subscales[satK] + jitter(), y: r.subscales[frustK] + jitter() }}));
            const colours = results.map(r => STATE_COLOURS[r.domainStates[dom]] + '88');
            makeChart(chartId, {{
                type: 'scatter',
                data: {{ datasets: [{{ data: points, backgroundColor: colours, pointRadius: 2.5, pointHoverRadius: 5 }}] }},
                options: {{
                    responsive: true, animation: false,
                    plugins: {{
                        legend: {{ display: false }},
                        title: {{ display: true, text: label }},
                        annotation: {{ annotations: thresholdAnnotations }}
                    }},
                    scales: {{
                        x: {{ min: 0, max: 10, title: {{ display: true, text: 'Satisfaction' }},
                            grid: {{ color: 'rgba(0,0,0,0.05)' }} }},
                        y: {{ min: 0, max: 10, title: {{ display: true, text: 'Frustration' }},
                            grid: {{ color: 'rgba(0,0,0,0.05)' }} }}
                    }}
                }}
            }});
        }}

        // 2x2 Quadrant: [Vulnerable, Distressed, Thriving, Mild]
        // Layout: top-left = high sat + high frust (Vulnerable), top-right = low sat + high frust (Distressed)
        //         bottom-left = high sat + low frust (Thriving), bottom-right = low sat + low frust (Mild)
        const quadOrder = ["Vulnerable","Thriving","Distressed","Mild"];
        const quadBg = {{"Vulnerable":"#FFF8F0","Distressed":"#FFF0F0","Thriving":"#F0FFF4","Mild":"#F5F5F5"}};
        const fatigueLevel = {{"Thriving":15,"Mild":45,"Vulnerable":75,"Distressed":95}};

        // Compute overall state percentages (across all 3 domains)
        const stateTotals = {{}};
        stateNames.forEach(s => {{ stateTotals[s] = 0; }});
        for (const d of domains) {{
            results.forEach(r => {{ stateTotals[r.domainStates[d]]++; }});
        }}
        const totalSlots = n * 3;

        const quadEl = document.getElementById('states-quadrant');
        let quadHTML = '<div class="ds-quadrant">';
        for (const sn of quadOrder) {{
            const desc = STATE_DESCS[sn];
            if (!desc) continue;
            const pct = (stateTotals[sn] / totalSlots * 100).toFixed(1);
            quadHTML += `<div class="ds-quadrant-cell" data-state="${{sn}}" style="background:${{quadBg[sn]}}">
                <div class="ds-cell-header">
                    <span class="ds-cell-label" style="color:${{desc.colour}}">${{sn}}</span>
                    <span class="ds-cell-pct" style="color:${{desc.colour}}">${{pct}}%</span>
                </div>
                <div class="ds-cell-condition">${{desc.condition}}</div>
                <div class="ds-cell-summary">${{desc.summary}}</div>
            </div>`;
        }}
        quadHTML += '</div>';
        quadEl.innerHTML = quadHTML;

        // Detail panel
        const detailContainer = document.getElementById('states-detail-container');
        detailContainer.innerHTML = '';
        let activeState = null;

        quadEl.querySelectorAll('.ds-quadrant-cell').forEach(cell => {{
            cell.addEventListener('click', () => {{
                const sn = cell.getAttribute('data-state');
                quadEl.querySelectorAll('.ds-quadrant-cell').forEach(c => c.classList.remove('active'));
                if (activeState === sn) {{
                    detailContainer.innerHTML = '';
                    activeState = null;
                    return;
                }}
                cell.classList.add('active');
                activeState = sn;

                const desc = STATE_DESCS[sn];
                const fl = fatigueLevel[sn];
                const flColour = fl < 30 ? '#3ABF5E' : fl < 60 ? '#F5A623' : '#E8563A';
                const flLabel = fl < 30 ? 'Low' : fl < 60 ? 'Moderate' : fl < 80 ? 'High' : 'Severe';

                detailContainer.innerHTML = `<div class="ds-detail">
                    <div class="ds-detail-header">
                        <h3 style="color:${{desc.colour}}">${{sn}}</h3>
                        <button class="ds-detail-close" onclick="document.getElementById('states-detail-container').innerHTML='';document.querySelectorAll('.ds-quadrant-cell').forEach(c=>c.classList.remove('active'));" title="Close">&times;</button>
                    </div>
                    <div style="height:3px;background:${{desc.colour}};"></div>
                    <div class="ds-detail-body">
                        <div class="ds-section">
                            <div class="ds-label">Summary</div>
                            <p>${{desc.summary}}</p>
                        </div>
                        <div class="ds-section">
                            <div class="ds-label">Science</div>
                            <p>${{desc.science}}</p>
                        </div>
                        <div class="ds-section">
                            <div class="ds-label">Mental Fatigue Risk</div>
                            <div class="ds-fatigue-indicator">
                                <div class="ds-fatigue-bar"><div class="ds-fatigue-fill" style="width:${{fl}}%;background:${{flColour}}"></div></div>
                                <span class="ds-fatigue-label" style="color:${{flColour}}">${{flLabel}}</span>
                            </div>
                            <p>${{desc.fatigue || ''}}</p>
                        </div>
                        <div class="ds-section">
                            <div class="ds-label">Implication</div>
                            <p style="font-style:italic;color:var(--muted);">${{desc.implication}}</p>
                        </div>
                    </div>
                </div>`;
                detailContainer.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }});
        }});
    }}

    const BELBIN_DESCS = {{
        "Plant": {{
            qualifier: "Creative / Conceptual",
            definition: "The Plant generates original ideas and solves difficult problems through unconventional thinking. In traditional teams, Plants are the source of innovation — the person who rethinks the brief when everyone else is executing it.",
            abc: "Craft-dominant satisfaction places this person in the Thinking cluster. High Openness — curiosity, tolerance for ambiguity, and intellectual independence — selects the Plant role. Creative (natural) when Openness is strong; Conceptual (manageable) when moderate.",
            condition: "Craft primary domain \u00d7 Openness percentile"
        }},
        "Specialist": {{
            qualifier: "Deep Mastery / Focused",
            definition: "The Specialist contributes deep, focused expertise in a narrow field. Teams rely on Specialists for technical authority — they are the person whose knowledge others trust without question.",
            abc: "Craft-dominant satisfaction places this person in the Thinking cluster. High Conscientiousness — discipline, thoroughness, and sustained focus — selects the Specialist role. Deep Mastery when Conscientiousness is strong; Focused when moderate.",
            condition: "Craft primary domain \u00d7 Conscientiousness percentile"
        }},
        "Monitor-Evaluator": {{
            qualifier: "Vigilant / Analytical",
            definition: "Monitor-Evaluators see flaws others miss. They analyse proposals critically, weigh evidence dispassionately, and prevent the team from committing to weak plans. Their value lies in what they stop, not what they start.",
            abc: "Craft-dominant satisfaction places this person in the Thinking cluster. Higher Neuroticism — sensitivity to risk, critical awareness, and attention to what could go wrong — selects the Monitor-Evaluator role. Vigilant when N is strong; Analytical when moderate.",
            condition: "Craft primary domain \u00d7 Neuroticism percentile"
        }},
        "Teamworker": {{
            qualifier: "Anchor / Supportive",
            definition: "Teamworkers hold the group together. They smooth interpersonal friction, support quieter members, and ensure everyone feels heard. Without a Teamworker, talented teams fracture under stress.",
            abc: "Belonging-dominant satisfaction places this person in the People cluster. High Agreeableness — cooperation, empathy, and harmony-seeking — selects the Teamworker role. Anchor when Agreeableness is strong; Supportive when moderate.",
            condition: "Belonging primary domain \u00d7 Agreeableness percentile"
        }},
        "Resource Investigator": {{
            qualifier: "Networker / Curious",
            definition: "Resource Investigators explore outside the team, finding opportunities, contacts, and ideas from the wider environment. They are the team's antenna — always scanning for what is new and useful.",
            abc: "Belonging-dominant satisfaction places this person in the People cluster. High Extraversion — social energy, assertiveness, and comfort with new contacts — selects the Resource Investigator role. Networker when Extraversion is strong; Curious when moderate.",
            condition: "Belonging primary domain \u00d7 Extraversion percentile"
        }},
        "Coordinator": {{
            qualifier: "Balanced / Structured",
            definition: "The Coordinator delegates effectively, draws out contributions from others, and keeps the team aligned toward shared goals. They lead through structure rather than charisma.",
            abc: "Belonging-dominant satisfaction places this person in the People cluster. High Conscientiousness — organisation, reliability, and methodical leadership — selects the Coordinator role. Balanced when Conscientiousness is strong; Structured when moderate.",
            condition: "Belonging primary domain \u00d7 Conscientiousness percentile"
        }},
        "Shaper": {{
            qualifier: "Inspiring / Driving",
            definition: "Shapers push the team toward action. They thrive under pressure, challenge complacency, and keep momentum high. When a project stalls, the Shaper is the one who breaks the deadlock.",
            abc: "Ambition-dominant satisfaction places this person in the Action cluster. High Extraversion — assertiveness, social boldness, and drive to influence — selects the Shaper role. Inspiring when Extraversion is strong; Driving when moderate.",
            condition: "Ambition primary domain \u00d7 Extraversion percentile"
        }},
        "Implementer": {{
            qualifier: "Systematic / Practical",
            definition: "Implementers turn ideas into practical plans and plans into results. They are disciplined, reliable, and efficient — the person who builds the process that makes the vision real.",
            abc: "Ambition-dominant satisfaction places this person in the Action cluster. High Conscientiousness — discipline, planning, and reliable execution — selects the Implementer role. Systematic when Conscientiousness is strong; Practical when moderate.",
            condition: "Ambition primary domain \u00d7 Conscientiousness percentile"
        }},
        "Completer-Finisher": {{
            qualifier: "Quality Driven / Thorough",
            definition: "Completer-Finishers ensure nothing ships with errors. They check details others skip, catch mistakes before they reach the client, and hold the team to its quality standard.",
            abc: "Ambition-dominant satisfaction places this person in the Action cluster. Higher Neuroticism — anxiety about errors, perfectionism, and quality vigilance — selects the Completer-Finisher role. Quality Driven when N is strong; Thorough when moderate.",
            condition: "Ambition primary domain \u00d7 Neuroticism percentile"
        }}
    }};

    let activeBelbinRole = null;

    function updateBelbin(results) {{
        const n = results.length;
        const rc = {{}};
        results.forEach(r => r.belbin_roles.forEach(br => {{
            const key = br.role + ' (' + br.qualifier + ')';
            rc[key] = (rc[key]||0)+1;
        }}));
        const sorted = Object.entries(rc).sort((a,b) => b[1]-a[1]);

        makeChart('chart-belbin', {{
            type: 'bar',
            data: {{ labels: sorted.map(r => r[0]), datasets: [{{ data: sorted.map(r => r[1]), backgroundColor: sorted.map(r => BELBIN_COLOURS[r[0]] || '#666') }}] }},
            options: {{ responsive: true, indexAxis: 'y', plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => ctx.raw + ' (' + (ctx.raw/n*100).toFixed(1) + '%)' }} }} }} }}
        }});

        let tableHTML = '';
        for (const [label, count] of sorted) {{
            tableHTML += `<tr><td>${{label}}</td><td class="num">${{count}}</td><td class="num">${{(count/n*100).toFixed(1)}}%</td></tr>`;
        }}
        document.getElementById('belbin-table-body').innerHTML = tableHTML;

        // Compute role-to-type co-occurrence
        const roleTypes = {{}};
        results.forEach(r => {{
            r.belbin_roles.forEach(br => {{
                if (!roleTypes[br.role]) roleTypes[br.role] = {{}};
                roleTypes[br.role][r.type] = (roleTypes[br.role][r.type] || 0) + 1;
            }});
        }});

        // Build role guide index
        const indexEl = document.getElementById('belbin-guide-index');
        const detailEl = document.getElementById('belbin-guide-detail');
        detailEl.innerHTML = '';
        activeBelbinRole = null;

        const roles = Object.keys(BELBIN_DESCS);
        let indexHTML = '<div class="bg-role-list">';
        for (const role of roles) {{
            const bd = BELBIN_DESCS[role];
            const colour = BELBIN_COLOURS[role + ' (' + bd.qualifier.split(' / ')[0] + ')'] || '#666';
            indexHTML += `<div class="bg-role-item" data-role="${{role}}"><div><div class="bg-role-name">${{role}}</div><div class="bg-role-qual">${{bd.qualifier}}</div></div><div class="bg-role-dot" style="background:${{colour}}"></div></div>`;
        }}
        indexHTML += '</div>';
        indexEl.innerHTML = indexHTML;

        // Store for detail rendering
        window._belbinRoleTypes = roleTypes;
        window._belbinN = n;

        // Attach click handlers
        indexEl.querySelectorAll('.bg-role-item').forEach(item => {{
            item.addEventListener('click', () => {{
                const role = item.getAttribute('data-role');
                indexEl.querySelectorAll('.bg-role-item').forEach(el => el.classList.remove('active'));
                if (activeBelbinRole === role) {{
                    detailEl.innerHTML = '';
                    activeBelbinRole = null;
                    return;
                }}
                item.classList.add('active');
                activeBelbinRole = role;
                renderBelbinDetail(role);
                detailEl.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }});
        }});
    }}

    function renderBelbinDetail(role) {{
        const detailEl = document.getElementById('belbin-guide-detail');
        const bd = BELBIN_DESCS[role];
        if (!bd) {{ detailEl.innerHTML = ''; return; }}

        const colour = BELBIN_COLOURS[role + ' (' + bd.qualifier.split(' / ')[0] + ')'] || '#666';
        const roleTypes = window._belbinRoleTypes[role] || {{}};
        const n = window._belbinN;

        // Sort types by frequency, take top 8
        const topTypes = Object.entries(roleTypes).sort((a,b) => b[1]-a[1]).slice(0, 8);

        let typeLinksHTML = '';
        if (topTypes.length > 0) {{
            topTypes.forEach(([typeName, count]) => {{
                const desc = TYPE_DESCS[typeName];
                const domain = desc ? desc.domain : 'any';
                const pct = (count / n * 100).toFixed(1);
                typeLinksHTML += `<a class="bg-type-link" data-domain="${{domain}}" data-typename="${{typeName}}" style="cursor:pointer">${{typeName}} <span style="opacity:0.7">(${{pct}}%)</span></a>`;
            }});
        }} else {{
            typeLinksHTML = '<span style="color:var(--muted);font-size:0.88rem;">No participants hold this role in the current simulation.</span>';
        }}

        detailEl.innerHTML = `<div class="bg-detail">
            <div class="bg-detail-header">
                <div>
                    <h3>${{role}} <span class="bg-qualifier">${{bd.qualifier}}</span></h3>
                </div>
                <button class="bg-detail-close" onclick="document.getElementById('belbin-guide-detail').innerHTML='';activeBelbinRole=null;document.querySelectorAll('.bg-role-item').forEach(el=>el.classList.remove('active'));" title="Close">&times;</button>
            </div>
            <div style="height:3px;background:${{colour}};"></div>
            <div class="bg-detail-body">
                <div class="bg-section">
                    <div class="bg-label">Definition</div>
                    <p>${{bd.definition}}</p>
                </div>
                <div class="bg-section">
                    <div class="bg-label">ABC Alignment</div>
                    <p>${{bd.abc}}</p>
                </div>
                <div class="bg-section">
                    <div class="bg-label">Trigger Condition</div>
                    <div class="bg-condition">${{bd.condition}}</div>
                </div>
                <div class="bg-section">
                    <div class="bg-label">Most Common Types</div>
                    <div class="bg-type-links">${{typeLinksHTML}}</div>
                </div>
            </div>
        </div>`;

        // Attach click handlers for type links
        detailEl.querySelectorAll('.bg-type-link[data-typename]').forEach(link => {{
            link.addEventListener('click', () => {{
                const tn = link.getAttribute('data-typename');
                switchTab('types');
                setTimeout(() => {{
                    const item = document.querySelector('.tg-type-item[data-type="' + tn + '"]');
                    if (item) {{
                        item.click();
                        item.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }}
                }}, 150);
            }});
        }});
    }}

    function updateRisk(results) {{
        const n = results.length;
        // Frustration signatures table
        const sc = {{}}, rm = {{}};
        results.forEach(r => r.frustration_signatures.forEach(sig => {{
            sc[sig.label] = (sc[sig.label]||0)+1;
            rm[sig.label] = sig.risk;
        }}));
        const noSig = results.filter(r => r.frustration_signatures.length===0).length;
        const sorted = Object.entries(sc).sort((a,b) => b[1]-a[1]);

        let tableHTML = '';
        for (const [label, count] of sorted) {{
            const risk = rm[label];
            const rc = risk === 'high' ? '#E8563A' : '#F5A623';
            tableHTML += `<tr><td>${{label}}</td><td><span class="state-badge" style="background:${{rc}}">${{risk}}</span></td><td class="num">${{count}}</td><td class="num">${{(count/n*100).toFixed(1)}}%</td></tr>`;
        }}
        tableHTML += `<tr style="border-top:2px solid var(--border);"><td><em>No signatures</em></td><td></td><td class="num">${{noSig}}</td><td class="num">${{(noSig/n*100).toFixed(1)}}%</td></tr>`;
        document.getElementById('frust-table-body').innerHTML = tableHTML;

        // Subscale distribution chart (mean + SD error bars)
        const means = SUB_KEYS.map(k => {{ const v = results.map(r => r.subscales[k]); return v.reduce((a,b)=>a+b,0)/v.length; }});
        const sds = SUB_KEYS.map((k,i) => {{ const v = results.map(r => r.subscales[k]); const m = means[i]; return Math.sqrt(v.reduce((s2,x)=>s2+(x-m)**2,0)/v.length); }});
        makeChart('chart-subscales', {{
            type: 'bar',
            data: {{ labels: SUB_LABELS, datasets: [{{ label: 'Mean', data: means.map(m => +m.toFixed(2)), backgroundColor: SUB_COLOURS.map(c => c+'99'), borderColor: SUB_COLOURS, borderWidth: 1, errorBars: sds }}] }},
            options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ min: 0, max: 10, title: {{ display: true, text: 'Score (0-10)' }} }} }} }},
            plugins: [{{
                id: 'errorBars2',
                afterDraw(chart) {{
                    const ctx = chart.ctx; const meta = chart.getDatasetMeta(0); const ds = chart.data.datasets[0];
                    if (!ds.errorBars) return;
                    ctx.save(); ctx.strokeStyle = '#333'; ctx.lineWidth = 1.5;
                    meta.data.forEach((bar, i) => {{
                        const sd = ds.errorBars[i]; const yScale = chart.scales.y; const mean = ds.data[i];
                        const yTop = yScale.getPixelForValue(mean+sd); const yBot = yScale.getPixelForValue(mean-sd); const x = bar.x;
                        ctx.beginPath(); ctx.moveTo(x,yTop); ctx.lineTo(x,yBot); ctx.stroke();
                        ctx.beginPath(); ctx.moveTo(x-4,yTop); ctx.lineTo(x+4,yTop); ctx.stroke();
                        ctx.beginPath(); ctx.moveTo(x-4,yBot); ctx.lineTo(x+4,yBot); ctx.stroke();
                    }});
                    ctx.restore();
                }}
            }}]
        }});

        // Big Five chart
        const b5means = B5_TRAITS.map(t => {{ const v = results.map(r => r.bigFive[t]); return v.reduce((a,b)=>a+b,0)/v.length; }});
        const b5sds = B5_TRAITS.map((t,i) => {{ const v = results.map(r => r.bigFive[t]); const m = b5means[i]; return Math.sqrt(v.reduce((s2,x)=>s2+(x-m)**2,0)/v.length); }});
        makeChart('chart-bigfive', {{
            type: 'bar',
            data: {{ labels: B5_LABELS, datasets: [{{ data: b5means.map(m => +m.toFixed(1)), backgroundColor: B5_COLOURS.map(c => c+'99'), borderColor: B5_COLOURS, borderWidth: 1, errorBars: b5sds }}] }},
            options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ min: 0, max: 100, title: {{ display: true, text: 'Percentile' }} }} }} }},
            plugins: [{{
                id: 'errorBars3',
                afterDraw(chart) {{
                    const ctx = chart.ctx; const meta = chart.getDatasetMeta(0); const ds = chart.data.datasets[0];
                    if (!ds.errorBars) return;
                    ctx.save(); ctx.strokeStyle = '#333'; ctx.lineWidth = 1.5;
                    meta.data.forEach((bar, i) => {{
                        const sd = ds.errorBars[i]; const yScale = chart.scales.y; const mean = ds.data[i];
                        const yTop = yScale.getPixelForValue(mean+sd); const yBot = yScale.getPixelForValue(mean-sd); const x = bar.x;
                        ctx.beginPath(); ctx.moveTo(x,yTop); ctx.lineTo(x,yBot); ctx.stroke();
                        ctx.beginPath(); ctx.moveTo(x-4,yTop); ctx.lineTo(x+4,yTop); ctx.stroke();
                        ctx.beginPath(); ctx.moveTo(x-4,yBot); ctx.lineTo(x+4,yBot); ctx.stroke();
                    }});
                    ctx.restore();
                }}
            }}]
        }});

        // Subscale stats table
        const mins = SUB_KEYS.map(k => Math.min(...results.map(r => r.subscales[k])));
        const maxs = SUB_KEYS.map(k => Math.max(...results.map(r => r.subscales[k])));
        let subHTML = '';
        const subNames = ["A-Satisfaction","A-Frustration","B-Satisfaction","B-Frustration","C-Satisfaction","C-Frustration"];
        for (let i = 0; i < 6; i++) {{
            subHTML += `<tr><td>${{subNames[i]}}</td><td class="num">${{means[i].toFixed(2)}}</td><td class="num">${{sds[i].toFixed(2)}}</td><td class="num">${{mins[i].toFixed(2)}}</td><td class="num">${{maxs[i].toFixed(2)}}</td></tr>`;
        }}
        document.getElementById('subscale-stats-body').innerHTML = subHTML;
    }}

    /* ═══════════════════════════════════════════════════
       PARTICIPANTS TABLE
       ═══════════════════════════════════════════════════ */
    let sortKey = "id", sortAsc = true, expandedId = null;

    function stateBadge(state) {{ return `<span class="state-badge" style="background:${{STATE_COLOURS[state]||'#666'}}">${{state}}</span>`; }}
    function domainBadge(domain) {{ return `<span class="domain-badge" style="background:${{DOMAIN_COLOURS[domain]||'#666'}}">${{domain}}</span>`; }}
    function scoreBar(label, value, max, colour, showThreshold) {{
        const pct = (value/max*100).toFixed(1);
        const threshold = showThreshold ? '<div class="threshold-line"></div>' : '';
        return `<div class="score-bar-wrap"><span class="score-bar-label">${{label}}</span><div class="score-bar-track">${{threshold}}<div class="score-bar-fill" style="width:${{pct}}%;background:${{colour}}"></div></div><span class="score-bar-val">${{value}}</span></div>`;
    }}

    function buildDetailHTML(p) {{
        let responsesHTML = '';
        SUBSCALE_GROUPS.forEach(g => {{
            responsesHTML += `<div><strong style="color:${{g.colour}}">${{g.label}}</strong><div class="items-grid">`;
            g.items.forEach(item => {{
                const raw = p.responses[item];
                if (item.endsWith("4")) {{
                    const scored = 8 - raw;
                    responsesHTML += `<div><span class="item-label">${{item}} (R):</span> <span class="item-val">${{raw}} <span style="color:var(--muted);font-size:0.75rem;">&rarr; ${{scored}}</span></span></div>`;
                }} else {{
                    responsesHTML += `<div><span class="item-label">${{item}}:</span> <span class="item-val">${{raw}}</span></div>`;
                }}
            }});
            responsesHTML += '</div></div>';
        }});

        let scoresHTML = '';
        scoresHTML += scoreBar("A-Sat", p.a_sat, 10, "#E8563A", true);
        scoresHTML += scoreBar("A-Frust", p.a_frust, 10, "#E8563A", true);
        scoresHTML += scoreBar("B-Sat", p.b_sat, 10, "#3A8FE8", true);
        scoresHTML += scoreBar("B-Frust", p.b_frust, 10, "#3A8FE8", true);
        scoresHTML += scoreBar("C-Sat", p.c_sat, 10, "#3ABF5E", true);
        scoresHTML += scoreBar("C-Frust", p.c_frust, 10, "#3ABF5E", true);

        let b5HTML = '';
        BIG_FIVE_KEYS.forEach(t => {{ b5HTML += scoreBar(t.label, p[t.key], 99, t.colour, false); }});

        let belbinHTML = '';
        if (p.belbin_roles && p.belbin_roles.length > 0) {{
            p.belbin_roles.forEach(br => {{ belbinHTML += `<span class="belbin-badge">${{br.role}} (${{br.qualifier}})</span> `; }});
        }} else {{ belbinHTML = '<span style="color:var(--muted)">None</span>'; }}

        let sigHTML = '';
        if (p.frustration_signatures && p.frustration_signatures.length > 0) {{
            p.frustration_signatures.forEach(sig => {{
                const cls = sig.risk === 'high' ? 'sig-badge-high' : 'sig-badge-medium';
                sigHTML += `<span class="sig-badge ${{cls}}">${{sig.label}} (${{sig.risk}})</span> `;
            }});
        }} else {{ sigHTML = '<span style="color:var(--muted)">None detected</span>'; }}

        let typeDescHTML = '';
        const td = TYPE_DESCS[p.type];
        if (td) {{
            typeDescHTML = `<div class="type-desc-block"><div class="tagline">${{p.type}}: ${{td.tagline}}</div><p>${{td.description}}</p><p class="growth"><strong>Growth edge:</strong> ${{td.growth_edge}}</p></div>`;
        }}

        // Full domain narrative — all three domains, not just the primary
        const domainMeta = [
            {{ key: "ambition", label: "Ambition", colour: "#E8563A", satK: "a_sat", frustK: "a_frust" }},
            {{ key: "belonging", label: "Belonging", colour: "#3A8FE8", satK: "b_sat", frustK: "b_frust" }},
            {{ key: "craft", label: "Craft", colour: "#3ABF5E", satK: "c_sat", frustK: "c_frust" }}
        ];
        const stateColours = {{ Thriving: "#3ABF5E", Vulnerable: "#F5A623", Mild: "#6c757d", Distressed: "#E74C3C" }};
        const stateNarrative = {{
            Thriving: "This need is well met with minimal obstruction.",
            Vulnerable: "Satisfaction is high but so is frustration — performance under strain.",
            Mild: "Neither strongly satisfied nor frustrated — latent potential.",
            Distressed: "High frustration with low satisfaction — active unmet need."
        }};
        let domNarrativeHTML = '<div class="domain-narrative"><h4>Motivational Profile</h4>';
        domNarrativeHTML += '<p style="color:var(--muted);font-size:0.85rem;margin-bottom:0.6rem;">The type label orients which need dominates. The scores across all three domains tell the full story.</p>';
        for (const dm of domainMeta) {{
            const state = p.domainStates[dm.key];
            const sat = p[dm.satK];
            const frust = p[dm.frustK];
            const isPrimary = dm.key === p.domDomain;
            const stCol = stateColours[state] || '#666';
            const badge = isPrimary ? '<span style="font-size:0.7rem;background:rgba(0,0,0,0.08);padding:2px 6px;border-radius:3px;margin-left:6px;">Primary</span>' : '';
            domNarrativeHTML += `<div class="dn-domain" style="border-left:3px solid ${{dm.colour}};padding:0.4rem 0.6rem;margin-bottom:0.5rem;">`;
            domNarrativeHTML += `<div style="display:flex;align-items:center;gap:6px;"><strong>${{dm.label}}</strong>${{badge}} <span class="state-badge" style="background:${{stCol}};font-size:0.75rem;padding:2px 8px;border-radius:3px;color:white;">${{state}}</span></div>`;
            domNarrativeHTML += `<div style="font-size:0.85rem;color:var(--muted);margin-top:2px;">Sat ${{sat}} · Frust ${{frust}} — ${{stateNarrative[state]}}</div>`;
            domNarrativeHTML += `</div>`;
        }}
        domNarrativeHTML += '</div>';

        return `<div class="detail-grid">
            <div class="detail-section"><h4>Raw Responses (1-7 Likert) &mdash; (R) = reverse-scored</h4>${{responsesHTML}}</div>
            <div class="detail-section"><h4>Subscale Scores (0-10)</h4>${{scoresHTML}}${{domNarrativeHTML}}<div style="margin-top:0.8rem"><h4>Big Five Percentiles</h4>${{b5HTML}}</div><div style="margin-top:0.8rem"><h4>Belbin Roles</h4>${{belbinHTML}}</div><div style="margin-top:0.8rem"><h4>Frustration Signatures</h4>${{sigHTML}}</div>${{typeDescHTML}}</div>
        </div>`;
    }}

    function getFiltered() {{
        const search = document.getElementById("search-input").value.toLowerCase();
        const typeF = document.getElementById("type-filter").value;
        const domainF = document.getElementById("domain-filter").value;
        const stateF = document.getElementById("state-filter").value;
        return DATA.filter(p => {{
            if (typeF && p.type !== typeF) return false;
            if (domainF && p.domain !== domainF) return false;
            if (stateF && p.a_state !== stateF && p.b_state !== stateF && p.c_state !== stateF) return false;
            if (search) {{
                const hay = `${{p.id}} ${{p.type}} ${{p.domain}} ${{p.a_state}} ${{p.b_state}} ${{p.c_state}}`.toLowerCase();
                if (!hay.includes(search)) return false;
            }}
            return true;
        }});
    }}

    function renderParticipants() {{
        const panel = document.getElementById('participant-detail');
        panel.style.display = 'none';
        panel.innerHTML = '';
        expandedId = null;
        let filtered = getFiltered();
        filtered.sort((a,b) => {{
            let va = a[sortKey], vb = b[sortKey];
            if (typeof va === "string") {{ va = va.toLowerCase(); vb = vb.toLowerCase(); }}
            if (va < vb) return sortAsc ? -1 : 1;
            if (va > vb) return sortAsc ? 1 : -1;
            return 0;
        }});
        const tbody = document.getElementById("participants-body");
        tbody.innerHTML = "";
        // Randomly sample 500 for performance when dataset is large
        const limit = 500;
        let displayed = filtered;
        let sampled = false;
        if (filtered.length > limit) {{
            const indices = new Set();
            while (indices.size < limit) indices.add(Math.floor(Math.random() * filtered.length));
            displayed = [...indices].sort((a,b) => a-b).map(i => filtered[i]);
            sampled = true;
        }}
        document.getElementById("row-count").textContent = sampled
            ? `Showing ${{limit}} random of ${{filtered.length}} (from ${{DATA.length}} total)`
            : `Showing ${{filtered.length}} of ${{DATA.length}}`;
        for (let idx = 0; idx < displayed.length; idx++) {{
            const p = displayed[idx];
            const tr = document.createElement("tr");
            tr.className = "row-clickable";
            tr.innerHTML = `<td class="num">${{p.id}}</td><td><strong>${{p.type}}</strong></td><td>${{domainBadge(p.domain)}}</td><td>${{stateBadge(p.a_state)}}</td><td>${{stateBadge(p.b_state)}}</td><td>${{stateBadge(p.c_state)}}</td><td class="num">${{p.a_sat.toFixed(2)}}</td><td class="num">${{p.a_frust.toFixed(2)}}</td><td class="num">${{p.b_sat.toFixed(2)}}</td><td class="num">${{p.b_frust.toFixed(2)}}</td><td class="num">${{p.c_sat.toFixed(2)}}</td><td class="num">${{p.c_frust.toFixed(2)}}</td>`;
            tr.addEventListener("click", () => {{
                const panel = document.getElementById('participant-detail');
                if (expandedId === p.id) {{
                    panel.style.display = 'none';
                    panel.innerHTML = '';
                    expandedId = null;
                }} else {{
                    panel.innerHTML = buildDetailHTML(p);
                    panel.style.display = 'block';
                    panel.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
                    expandedId = p.id;
                }}
            }});
            tbody.appendChild(tr);
        }}
        if (filtered.length > limit) {{
            const tr = document.createElement("tr");
            tr.innerHTML = `<td colspan="12" style="text-align:center;color:var(--muted);padding:1rem;">Showing ${{limit}} randomly sampled participants out of ${{filtered.length}} total. Use filters to narrow results.</td>`;
            tbody.appendChild(tr);
        }}
    }}

    function updateParticipants(results) {{
        DATA = results;
        // Repopulate type filter
        const typeSelect = document.getElementById("type-filter");
        const current = typeSelect.value;
        typeSelect.innerHTML = '<option value="">All Types</option>';
        const types = [...new Set(DATA.map(d => d.type))].sort();
        types.forEach(t => {{
            const opt = document.createElement("option");
            opt.value = t; opt.textContent = t;
            typeSelect.appendChild(opt);
        }});
        typeSelect.value = current;
        document.getElementById("search-input").value = '';
        renderParticipants();
    }}

    function exportCSV() {{
        const filtered = getFiltered();
        const headers = ["ID","Type","Domain","A-State","B-State","C-State","A-Sat","A-Frust","B-Sat","B-Frust","C-Sat","C-Frust","O","C","E","A","N",...ITEM_ORDER];
        const rows = filtered.map(p => [p.id, p.type, p.domain, p.a_state, p.b_state, p.c_state, p.a_sat, p.a_frust, p.b_sat, p.b_frust, p.c_sat, p.c_frust, p.O, p.C, p.E, p.A, p.N, ...ITEM_ORDER.map(i => p.responses[i])]);
        let csv = headers.join(",") + "\\n";
        rows.forEach(r => {{ csv += r.join(",") + "\\n"; }});
        const blob = new Blob([csv], {{type: "text/csv"}});
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "abc_participants.csv";
        a.click();
    }}

    /* ═══════════════════════════════════════════════════
       ASSESSMENT QUESTIONNAIRE
       ═══════════════════════════════════════════════════ */
    const ASSESS_ITEMS = {{
        // Each item: {{ id, subscale, domain, domainLabel, text, reverse }}
        // Subscale order: AS, AF, BS, BF, CS, CF
        // Based on SDT Basic Psychological Need Satisfaction & Frustration Scale
        // adapted for sport/performance context

        // ── Ambition Satisfaction ──
        AS1: {{ subscale: "a_sat", domain: "ambition", domainLabel: "Ambition", text: "I feel confident pursuing the goals that matter most to me.", reverse: false, tier: 1 }},
        AS2: {{ subscale: "a_sat", domain: "ambition", domainLabel: "Ambition", text: "I am making meaningful progress toward my personal ambitions.", reverse: false, tier: 2 }},
        AS3: {{ subscale: "a_sat", domain: "ambition", domainLabel: "Ambition", text: "I can see a clear path from where I am to where I want to be.", reverse: false, tier: 3 }},
        AS4: {{ subscale: "a_sat", domain: "ambition", domainLabel: "Ambition", text: "My ambitions feel unrealistic given my current situation.", reverse: true, tier: 3 }},

        // ── Ambition Frustration ──
        AF1: {{ subscale: "a_frust", domain: "ambition", domainLabel: "Ambition", text: "I feel held back from achieving what I know I am capable of.", reverse: false, tier: 1 }},
        AF2: {{ subscale: "a_frust", domain: "ambition", domainLabel: "Ambition", text: "I doubt whether my efforts toward my goals will pay off.", reverse: false, tier: 2 }},
        AF3: {{ subscale: "a_frust", domain: "ambition", domainLabel: "Ambition", text: "External circumstances keep blocking my path forward.", reverse: false, tier: 3 }},
        AF4: {{ subscale: "a_frust", domain: "ambition", domainLabel: "Ambition", text: "Nothing stands in the way of my drive and motivation.", reverse: true, tier: 3 }},

        // ── Belonging Satisfaction ──
        BS1: {{ subscale: "b_sat", domain: "belonging", domainLabel: "Belonging", text: "I feel genuinely connected to the people around me.", reverse: false, tier: 1 }},
        BS2: {{ subscale: "b_sat", domain: "belonging", domainLabel: "Belonging", text: "The people I work with understand and support who I am.", reverse: false, tier: 2 }},
        BS3: {{ subscale: "b_sat", domain: "belonging", domainLabel: "Belonging", text: "I can be myself around the people I spend the most time with.", reverse: false, tier: 3 }},
        BS4: {{ subscale: "b_sat", domain: "belonging", domainLabel: "Belonging", text: "I feel like an outsider in the groups that matter to me.", reverse: true, tier: 3 }},

        // ── Belonging Frustration ──
        BF1: {{ subscale: "b_frust", domain: "belonging", domainLabel: "Belonging", text: "I feel excluded from decisions or conversations that affect me.", reverse: false, tier: 1 }},
        BF2: {{ subscale: "b_frust", domain: "belonging", domainLabel: "Belonging", text: "I sense that people around me do not fully accept me.", reverse: false, tier: 2 }},
        BF3: {{ subscale: "b_frust", domain: "belonging", domainLabel: "Belonging", text: "My relationships feel conditional on meeting others' expectations.", reverse: false, tier: 3 }},
        BF4: {{ subscale: "b_frust", domain: "belonging", domainLabel: "Belonging", text: "I feel completely accepted by my teammates and peers.", reverse: true, tier: 3 }},

        // ── Craft Satisfaction ──
        CS1: {{ subscale: "c_sat", domain: "craft", domainLabel: "Craft", text: "I feel skilled and effective at what I do.", reverse: false, tier: 1 }},
        CS2: {{ subscale: "c_sat", domain: "craft", domainLabel: "Craft", text: "I regularly learn new things that improve my performance.", reverse: false, tier: 2 }},
        CS3: {{ subscale: "c_sat", domain: "craft", domainLabel: "Craft", text: "I can handle the challenges my work or training puts in front of me.", reverse: false, tier: 3 }},
        CS4: {{ subscale: "c_sat", domain: "craft", domainLabel: "Craft", text: "I feel out of my depth in important areas of my craft.", reverse: true, tier: 3 }},

        // ── Craft Frustration ──
        CF1: {{ subscale: "c_frust", domain: "craft", domainLabel: "Craft", text: "I feel my skills are being judged rather than developed.", reverse: false, tier: 1 }},
        CF2: {{ subscale: "c_frust", domain: "craft", domainLabel: "Craft", text: "I lack opportunities to practise and refine my abilities.", reverse: false, tier: 2 }},
        CF3: {{ subscale: "c_frust", domain: "craft", domainLabel: "Craft", text: "Mistakes feel punished rather than treated as chances to grow.", reverse: false, tier: 3 }},
        CF4: {{ subscale: "c_frust", domain: "craft", domainLabel: "Craft", text: "My environment supports me in mastering my craft.", reverse: true, tier: 3 }}
    }};

    // Tier definitions: which items to include
    const TIER_ITEMS = {{
        onboarding: ["AS1","AF1","BS1","BF1","CS1","CF1"],  // 6 items (1 per subscale)
        standard: ["AS1","AS2","AF1","AF2","BS1","BS2","BF1","BF2","CS1","CS2","CF1","CF2"],  // 12 items (2 per subscale)
        full: ITEM_ORDER  // 24 items (4 per subscale)
    }};

    let currentTier = null;
    let assessResponses = {{}};

    function selectTier(tier) {{
        currentTier = tier;
        assessResponses = {{}};
        document.querySelectorAll('.assess-tier-card').forEach(c => c.classList.remove('selected'));
        document.querySelector(`.assess-tier-card[data-tier="${{tier}}"]`).classList.add('selected');

        const items = TIER_ITEMS[tier];
        const container = document.getElementById('assess-items-container');
        container.innerHTML = '';

        items.forEach((itemId, idx) => {{
            const item = ASSESS_ITEMS[itemId];
            const domColour = DOMAIN_COLOURS[item.domain];
            let html = `<div class="assess-question" id="q-${{itemId}}">`;
            html += `<div class="q-domain" style="color:${{domColour}}">${{item.domainLabel}} &mdash; ${{item.subscale.includes('sat') ? 'Satisfaction' : 'Frustration'}}</div>`;
            html += `<div class="q-text">${{idx + 1}}. ${{item.text}}</div>`;
            html += `<div class="assess-likert">`;
            for (let v = 1; v <= 7; v++) {{
                html += `<label><input type="radio" name="q_${{itemId}}" value="${{v}}" onchange="recordAnswer('${{itemId}}', ${{v}})"><span class="likert-btn">${{v}}</span></label>`;
            }}
            html += `</div>`;
            html += `<div class="assess-likert-labels"><span>Strongly disagree</span><span>Strongly agree</span></div>`;
            html += `</div>`;
            container.innerHTML += html;
        }});

        document.getElementById('assess-picker').style.display = 'none';
        document.getElementById('assess-questions').style.display = 'block';
        document.getElementById('assess-results').style.display = 'none';
        updateAssessProgress();
    }}

    function recordAnswer(itemId, value) {{
        assessResponses[itemId] = parseInt(value);
        document.getElementById('q-' + itemId).classList.add('answered');
        updateAssessProgress();
    }}

    function updateAssessProgress() {{
        const items = TIER_ITEMS[currentTier];
        const answered = items.filter(id => assessResponses[id] !== undefined).length;
        const total = items.length;
        const pct = total > 0 ? (answered / total * 100) : 0;
        document.getElementById('assess-progress-fill').style.width = pct + '%';
        document.getElementById('assess-progress-text').textContent = answered + ' / ' + total;
        document.getElementById('assess-submit-btn').disabled = answered < total;
    }}

    function backToTierPicker() {{
        document.getElementById('assess-picker').style.display = 'block';
        document.getElementById('assess-questions').style.display = 'none';
        document.getElementById('assess-results').style.display = 'none';
        currentTier = null;
        assessResponses = {{}};
        document.querySelectorAll('.assess-tier-card').forEach(c => c.classList.remove('selected'));
    }}

    function scoreAssessment() {{
        // Score from raw responses to subscale scores using the same pipeline
        // as the simulation engine.
        const items = TIER_ITEMS[currentTier];
        const itemsPerSubscale = {{}};
        SUB_KEYS.forEach(k => itemsPerSubscale[k] = []);

        items.forEach(itemId => {{
            const item = ASSESS_ITEMS[itemId];
            let raw = assessResponses[itemId];
            // Reverse-score reverse items
            if (item.reverse) raw = 8 - raw;
            itemsPerSubscale[item.subscale].push(raw);
        }});

        // Compute subscale means (1-7) then normalise to 0-10
        const subscales = {{}};
        SUB_KEYS.forEach(k => {{
            const vals = itemsPerSubscale[k];
            if (vals.length === 0) {{
                subscales[k] = 5.0; // default midpoint if no items
            }} else {{
                const mean = vals.reduce((s, v) => s + v, 0) / vals.length;
                subscales[k] = Math.max(0, Math.min(10, (mean - 1) * 10 / 6));
            }}
        }});

        // Domain states
        const domainPairs = [["ambition","a_sat","a_frust"],["belonging","b_sat","b_frust"],["craft","c_sat","c_frust"]];
        const domainStates = {{}};
        for (const [dom, satK, frustK] of domainPairs) {{
            const sat = subscales[satK], frust = subscales[frustK];
            if (sat >= DOM_SAT_THRESHOLD && frust < DOM_FRUST_THRESHOLD) domainStates[dom] = "Thriving";
            else if (sat >= DOM_SAT_THRESHOLD && frust >= DOM_FRUST_THRESHOLD) domainStates[dom] = "Vulnerable";
            else if (sat < DOM_SAT_THRESHOLD && frust < DOM_FRUST_THRESHOLD) domainStates[dom] = "Mild";
            else domainStates[dom] = "Distressed";
        }}

        // Type derivation
        const aStrong = subscales.a_sat >= TYPE_SAT_THRESHOLD ? 1 : 0;
        const bStrong = subscales.b_sat >= TYPE_SAT_THRESHOLD ? 1 : 0;
        const cStrong = subscales.c_sat >= TYPE_SAT_THRESHOLD ? 1 : 0;
        const baseName = BASE_PATTERNS[aStrong + "," + bStrong + "," + cStrong];

        let frustCount = 0;
        if (subscales.a_frust >= TYPE_FRUST_THRESHOLD) frustCount++;
        if (subscales.b_frust >= TYPE_FRUST_THRESHOLD) frustCount++;
        if (subscales.c_frust >= TYPE_FRUST_THRESHOLD) frustCount++;
        const modifier = frustCount === 0 ? "Steady" : frustCount === 1 ? "Striving" : "Resolute";
        const typeName = modifier + " " + baseName;

        function satLevel(v) {{ if (v >= 8.0) return 5; if (v >= 6.0) return 4; if (v >= 4.0) return 3; if (v >= 2.0) return 2; return 1; }}
        const profileCode = satLevel(subscales.a_sat) + "-" + satLevel(subscales.b_sat) + "-" + satLevel(subscales.c_sat);

        // Dominant domain
        const sats = [["ambition", subscales.a_sat],["belonging", subscales.b_sat],["craft", subscales.c_sat]];
        let domDomain = sats[0][0], domMax = sats[0][1];
        for (let si = 1; si < 3; si++) {{ if (sats[si][1] > domMax) {{ domMax = sats[si][1]; domDomain = sats[si][0]; }} }}

        // Frustration signatures
        const frustSigs = [];
        for (const [dom, satK, frustK] of domainPairs) {{
            const sat = subscales[satK], frust = subscales[frustK];
            if (frust >= FRUST_SIG_FRUST_THRESHOLD) {{
                if (sat >= FRUST_SIG_SAT_THRESHOLD) frustSigs.push({{label: FRUST_LABELS[dom].medium, domain: dom, risk: "medium"}});
                else frustSigs.push({{label: FRUST_LABELS[dom].high, domain: dom, risk: "high"}});
            }}
        }}

        return {{ subscales, domainStates, typeName, profileCode, domDomain, frustSigs }};
    }}

    function submitAssessment() {{
        const result = scoreAssessment();
        const typeDesc = TYPE_DESCS[result.typeName] || {{}};
        const domColour = DOMAIN_COLOURS[result.domDomain] || '#555';

        let html = '<div class="result-type-card">';
        // Header with type name
        html += `<div class="result-type-header" style="background:${{domColour}}">`;
        html += `<div class="result-type-name">${{result.typeName}}</div>`;
        if (typeDesc.tagline) html += `<div class="result-type-tagline">${{typeDesc.tagline}}</div>`;
        html += `<div class="result-type-profile">Profile: ${{result.profileCode}} &middot; Dominant: ${{result.domDomain.charAt(0).toUpperCase() + result.domDomain.slice(1)}}</div>`;
        html += '</div>';

        // Body
        html += '<div class="result-body">';

        // Domain cards
        html += '<div class="result-domains">';
        const domainPairs = [["Ambition","a_sat","a_frust","ambition"],["Belonging","b_sat","b_frust","belonging"],["Craft","c_sat","c_frust","craft"]];
        for (const [label, satK, frustK, dom] of domainPairs) {{
            const state = result.domainStates[dom];
            const stateCol = STATE_COLOURS[state] || '#aaa';
            html += `<div class="result-domain" style="border-top:3px solid ${{DOMAIN_COLOURS[dom]}}">`;
            html += `<h4 style="color:${{DOMAIN_COLOURS[dom]}}">${{label}}</h4>`;
            html += `<div class="domain-scores">Sat: ${{result.subscales[satK].toFixed(1)}} &middot; Frust: ${{result.subscales[frustK].toFixed(1)}}</div>`;
            html += `<span class="state-badge" style="background:${{stateCol}}">${{state}}</span>`;
            html += '</div>';
        }}
        html += '</div>';

        // Description
        if (typeDesc.description) {{
            html += `<div style="font-size:0.92rem;line-height:1.7;margin-bottom:1.5rem;">${{typeDesc.description}}</div>`;
        }}

        // Pattern
        if (typeDesc.pattern) {{
            html += '<div style="margin-bottom:1.5rem;">';
            html += '<h4 style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.06em;color:var(--muted);margin-bottom:0.5rem;">Motivational Pattern</h4>';
            html += '<div style="display:flex;gap:0.5rem;">';
            for (const [d, status] of Object.entries(typeDesc.pattern)) {{
                const col = DOMAIN_COLOURS[d];
                const opacity = status === 'strong' ? '1' : '0.35';
                html += `<span style="background:${{col}};color:white;opacity:${{opacity}};padding:0.3rem 0.8rem;border-radius:6px;font-size:0.85rem;font-weight:600;">${{d.charAt(0).toUpperCase() + d.slice(1)}}: ${{status}}</span>`;
            }}
            html += '</div></div>';
        }}

        // Strengths
        if (typeDesc.strengths && typeDesc.strengths.length > 0) {{
            html += '<div class="result-strengths"><h4>Strengths</h4><ul>';
            typeDesc.strengths.forEach(s => {{ html += `<li>${{s}}</li>`; }});
            html += '</ul></div>';
        }}

        // Watch for & Growth edge
        if (typeDesc.watch_for || typeDesc.growth_edge) {{
            html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem;">';
            if (typeDesc.watch_for) {{
                html += '<div class="result-growth"><h4>Watch For</h4><p>' + typeDesc.watch_for + '</p></div>';
            }}
            if (typeDesc.growth_edge) {{
                html += '<div class="result-growth"><h4>Growth Edge</h4><p>' + typeDesc.growth_edge + '</p></div>';
            }}
            html += '</div>';
        }}

        // Frustration signals
        if (result.frustSigs.length > 0) {{
            html += '<div class="result-sigs"><h4>Frustration Signals</h4>';
            result.frustSigs.forEach(sig => {{
                const cls = sig.risk === 'high' ? 'sig-badge-high' : 'sig-badge-medium';
                html += `<span class="sig-badge ${{cls}}" style="margin-right:0.5rem;">${{sig.label}} (${{sig.risk}} risk)</span>`;
            }});
            html += '</div>';
        }}

        // Tier note
        const tierNames = {{ onboarding: "Onboarding (6 items)", standard: "Standard (12 items)", full: "Full Assessment (24 items)" }};
        html += `<div style="font-size:0.8rem;color:var(--muted);padding-top:1rem;border-top:1px solid var(--border);">`;
        html += `Assessed with: ${{tierNames[currentTier]}}`;
        if (currentTier !== 'full') {{
            html += ` &middot; <em>A longer assessment strengthens this profile.</em>`;
        }}
        html += '</div>';

        html += '</div></div>';

        // Retake button
        html += '<div style="text-align:center;margin-top:1.5rem;">';
        html += '<button class="assess-back" onclick="backToTierPicker()">Take Another Assessment</button>';
        html += '</div>';

        document.getElementById('assess-results').innerHTML = html;
        document.getElementById('assess-questions').style.display = 'none';
        document.getElementById('assess-results').style.display = 'block';
        document.getElementById('assess-results').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}

    /* ═══════════════════════════════════════════════════
       NAVIGATION
       ═══════════════════════════════════════════════════ */
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const sidebar = document.getElementById('sidebar');
    const hamburger = document.getElementById('hamburger');
    const navOverlay = document.getElementById('nav-overlay');
    let participantsInitialised = false;

    function switchTab(tabId) {{
        tabContents.forEach(tc => tc.classList.remove('active'));
        navItems.forEach(ni => ni.classList.remove('active'));
        const target = document.getElementById('tab-' + tabId);
        if (target) target.classList.add('active');
        navItems.forEach(ni => {{ if (ni.dataset.tab === tabId) ni.classList.add('active'); }});
        history.replaceState(null, '', '#' + tabId);
        if (tabId === 'participants' && !participantsInitialised) {{
            // Set up sort + filter listeners once
            document.querySelectorAll("#participants-table th").forEach(th => {{
                th.addEventListener("click", () => {{
                    const key = th.dataset.key;
                    if (sortKey === key) {{ sortAsc = !sortAsc; }}
                    else {{ sortKey = key; sortAsc = true; }}
                    document.querySelectorAll("#participants-table th").forEach(h => h.classList.remove("sorted"));
                    th.classList.add("sorted");
                    th.querySelector(".sort-arrow").innerHTML = sortAsc ? "&#9650;" : "&#9660;";
                    renderParticipants();
                }});
            }});
            document.getElementById("search-input").addEventListener("input", renderParticipants);
            document.getElementById("type-filter").addEventListener("change", renderParticipants);
            document.getElementById("domain-filter").addEventListener("change", renderParticipants);
            document.getElementById("state-filter").addEventListener("change", renderParticipants);
            participantsInitialised = true;
            renderParticipants();
        }}
        sidebar.classList.remove('open');
        navOverlay.classList.remove('open');
        // Resize charts in newly visible tab (Chart.js needs visible container)
        setTimeout(() => {{
            Object.values(charts).forEach(c => {{ try {{ c.resize(); }} catch(e) {{}} }});
        }}, 50);
    }}

    navItems.forEach(ni => {{ ni.addEventListener('click', () => switchTab(ni.dataset.tab)); }});
    hamburger.addEventListener('click', () => {{ sidebar.classList.toggle('open'); navOverlay.classList.toggle('open'); }});
    navOverlay.addEventListener('click', () => {{ sidebar.classList.remove('open'); navOverlay.classList.remove('open'); }});

    /* ═══════════════════════════════════════════════════
       SIMULATION ORCHESTRATOR
       ═══════════════════════════════════════════════════ */
    document.getElementById('sim-n').addEventListener('input', function() {{
        document.getElementById('sim-n-val').textContent = parseInt(this.value).toLocaleString();
    }});
    document.getElementById('sim-noise').addEventListener('input', function() {{
        document.getElementById('sim-noise-val').textContent = parseFloat(this.value).toFixed(1);
    }});

    function runSimulation() {{
        const n = parseInt(document.getElementById('sim-n').value);
        const noise = parseFloat(document.getElementById('sim-noise').value);
        const btn = document.getElementById('sim-run-btn');
        const status = document.getElementById('sim-status');
        btn.disabled = true;
        status.textContent = 'Simulating...';

        setTimeout(() => {{
            const t0 = performance.now();
            const results = simulatePopulation(n, noise);

            // Centre Big Five percentiles to remove systematic bias from sat/frust z-means.
            // Without this, traits loading on satisfaction (E) are boosted while traits
            // loading on frustration (N) are suppressed, skewing Belbin role distribution.
            const B5_SHORT = {{openness:'O',conscientiousness:'C',extraversion:'E',agreeableness:'A',neuroticism:'N'}};
            for (const trait of B5_TRAITS) {{
                const mean = results.reduce((s, r) => s + r.bigFive[trait], 0) / results.length;
                const shift = 50 - mean;
                results.forEach(r => {{
                    r.bigFive[trait] = Math.max(1, Math.min(99, Math.round(r.bigFive[trait] + shift)));
                    r[B5_SHORT[trait]] = r.bigFive[trait];
                }});
            }}

            // Recompute Belbin roles with centred Big Five
            const ROLE_DEFS = [
                {{role:"Plant", domain:"craft", trait:"openness", qN:"Creative", qM:"Conceptual"}},
                {{role:"Specialist", domain:"craft", trait:"conscientiousness", qN:"Deep Mastery", qM:"Focused"}},
                {{role:"Monitor-Evaluator", domain:"craft", trait:"neuroticism", qN:"Vigilant", qM:"Analytical"}},
                {{role:"Teamworker", domain:"belonging", trait:"agreeableness", qN:"Anchor", qM:"Supportive"}},
                {{role:"Resource Investigator", domain:"belonging", trait:"extraversion", qN:"Networker", qM:"Curious"}},
                {{role:"Coordinator", domain:"belonging", trait:"conscientiousness", qN:"Balanced", qM:"Structured"}},
                {{role:"Shaper", domain:"ambition", trait:"extraversion", qN:"Inspiring", qM:"Driving"}},
                {{role:"Implementer", domain:"ambition", trait:"conscientiousness", qN:"Systematic", qM:"Practical"}},
                {{role:"Completer-Finisher", domain:"ambition", trait:"neuroticism", qN:"Quality Driven", qM:"Thorough"}},
            ];
            const satMap = {{ambition:"a_sat",belonging:"b_sat",craft:"c_sat"}};
            results.forEach(r => {{
                const satArr = ["ambition","belonging","craft"].map(d => ({{d, v: r.subscales[satMap[d]] + Math.random() * 0.001}}));
                satArr.sort((a,b) => b.v - a.v);
                const domRanks = {{}};
                satArr.forEach((item, idx) => domRanks[item.d] = idx);
                const scored = ROLE_DEFS.map(rd => {{
                    const aff = [1.0, 0.5, 0.0][domRanks[rd.domain]];
                    const tPct = r.bigFive[rd.trait];
                    return {{role: rd.role, qualifier: tPct >= 60 ? rd.qN : rd.qM, score: aff * tPct / 100}};
                }});
                scored.sort((a,b) => b.score - a.score);
                const belbinRoles = [scored[0]];
                for (let bi = 1; bi < scored.length; bi++) {{
                    if (scored[bi].score >= 0.30) belbinRoles.push(scored[bi]);
                }}
                r.belbin_roles = belbinRoles;
            }});

            const elapsed = ((performance.now() - t0) / 1000).toFixed(2);

            updateOverview(results);
            updateTypes(results);
            updateDomainStates(results);
            updateBelbin(results);
            updateRisk(results);
            updateParticipants(results);

            document.getElementById('sidebar-footer').textContent = results.length.toLocaleString() + ' participants';
            status.textContent = 'Done in ' + elapsed + 's';
            btn.disabled = false;
        }}, 50);
    }}

    // Auto-run on load
    switchTab(location.hash ? location.hash.slice(1) : 'overview');
    runSimulation();
    </script>
</body>
</html>"""


if __name__ == "__main__":
    sys.exit(main())
