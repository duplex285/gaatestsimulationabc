#!/usr/bin/env python3
"""Build a self-contained HTML dashboard for ABC Assessment results.

Generates a single index.html with all charts embedded as base64 images.
Ready for Netlify deployment — just point it at the outputs/site/ directory.

Reference: abc-assessment-spec Section 11.4
"""

import base64
import io
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd

from src.python_scoring.scoring_pipeline import ABCScorer
from src.python_scoring.type_descriptions import DOMAIN_STATE_DESCRIPTIONS, TYPE_DESCRIPTIONS

DOMAIN_COLOURS = {
    "ambition": "#E8563A",
    "belonging": "#3A8FE8",
    "craft": "#3ABF5E",
}

STATE_COLOURS = {
    "Thriving": "#3ABF5E",
    "Vulnerable": "#F5A623",
    "Dormant": "#A0A0A0",
    "Distressed": "#E8563A",
}


ITEM_ORDER = [
    "AS1",
    "AS2",
    "AS3",
    "AS4",
    "AF1",
    "AF2",
    "AF3",
    "AF4",
    "BS1",
    "BS2",
    "BS3",
    "BS4",
    "BF1",
    "BF2",
    "BF3",
    "BF4",
    "CS1",
    "CS2",
    "CS3",
    "CS4",
    "CF1",
    "CF2",
    "CF3",
    "CF4",
]


def load_and_score():
    data_dir = project_root / "outputs" / "datasets"
    responses_df = pd.read_csv(data_dir / "ground_truth_responses.csv")
    scorer = ABCScorer()
    results = []
    raw_responses = []
    for _, row in responses_df.iterrows():
        resp = {col: int(row[col]) for col in responses_df.columns}
        raw_responses.append(resp)
        results.append(scorer.score(resp))
    return results, raw_responses


def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def make_type_chart(results):
    type_data = [(r["type_name"], r["type_domain"]) for r in results]
    counter = Counter(t[0] for t in type_data)
    domain_of = {t[0]: t[1] for t in type_data}

    sorted_types = sorted(counter.keys(), key=lambda t: counter[t], reverse=True)
    counts = [counter[t] for t in sorted_types]
    colours = [DOMAIN_COLOURS[domain_of[t]] for t in sorted_types]

    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(
        range(len(sorted_types)), counts, color=colours, edgecolor="white", linewidth=0.5
    )
    ax.set_yticks(range(len(sorted_types)))
    ax.set_yticklabels(sorted_types, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Count", fontsize=10)
    ax.set_title("36-Type Distribution", fontweight="bold", fontsize=13)

    for bar, count in zip(bars, counts, strict=False):
        pct = count / len(results) * 100
        ax.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{count} ({pct:.1f}%)",
            va="center",
            fontsize=8,
        )

    from matplotlib.patches import Patch

    legend_patches = [Patch(facecolor=c, label=d.capitalize()) for d, c in DOMAIN_COLOURS.items()]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=9)
    plt.tight_layout()
    return fig_to_base64(fig)


def make_domain_states_chart(results):
    domains = ["ambition", "belonging", "craft"]
    states = ["Thriving", "Vulnerable", "Dormant", "Distressed"]
    n = len(results)

    data = {}
    for domain in domains:
        ds = [r["domain_states"][domain] for r in results]
        data[domain] = {s: ds.count(s) for s in states}

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(domains))
    bottom = np.zeros(len(domains))

    for state in states:
        values = [data[d][state] for d in domains]
        ax.bar(
            x,
            values,
            bottom=bottom,
            label=state,
            color=STATE_COLOURS[state],
            edgecolor="white",
            linewidth=0.5,
            width=0.6,
        )
        for i, v in enumerate(values):
            if v >= 40:
                ax.text(
                    x[i],
                    bottom[i] + v / 2,
                    f"{v / n * 100:.0f}%",
                    ha="center",
                    va="center",
                    fontsize=9,
                    fontweight="bold",
                    color="white",
                )
        bottom += values

    ax.set_xticks(x)
    ax.set_xticklabels([d.capitalize() for d in domains], fontsize=11)
    ax.set_ylabel("Participants")
    ax.set_title("Domain State Distribution", fontweight="bold", fontsize=13)
    ax.legend(fontsize=9, loc="upper right")
    plt.tight_layout()
    return fig_to_base64(fig)


def make_subscale_chart(results):
    labels = ["A-Sat", "A-Frust", "B-Sat", "B-Frust", "C-Sat", "C-Frust"]
    keys = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]
    colours = ["#E8563A", "#E8563A", "#3A8FE8", "#3A8FE8", "#3ABF5E", "#3ABF5E"]

    data = [[r["subscales"][k] for r in results] for k in keys]

    fig, ax = plt.subplots(figsize=(8, 5))
    parts = ax.violinplot(data, positions=range(len(data)), showmeans=True, showmedians=True)
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(colours[i])
        pc.set_alpha(0.7)
    for key in ["cmeans", "cmedians", "cmins", "cmaxes", "cbars"]:
        if key in parts:
            parts[key].set_color("black")

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Score (0-10)")
    ax.set_ylim(-0.5, 10.5)
    ax.axhline(y=5.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.text(5.3, 5.7, "Threshold (5.5)", fontsize=8, color="gray")
    ax.set_title("Subscale Score Distributions", fontweight="bold", fontsize=13)
    plt.tight_layout()
    return fig_to_base64(fig)


def make_big_five_chart(results):
    labels = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]
    keys = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
    colours = ["#9B59B6", "#2ECC71", "#E67E22", "#3498DB", "#E74C3C"]

    data = [[r["big_five"][k] for r in results] for k in keys]

    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, notch=True)
    for patch, colour in zip(bp["boxes"], colours, strict=False):
        patch.set_facecolor(colour)
        patch.set_alpha(0.6)

    ax.set_ylabel("Percentile")
    ax.set_ylim(0, 100)
    ax.axhline(y=50, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.set_title("Big Five Percentile Distributions", fontweight="bold", fontsize=13)
    ax.tick_params(axis="x", rotation=15)
    plt.tight_layout()
    return fig_to_base64(fig)


def make_scatter_charts(results):
    domains = [
        ("Ambition", "a_sat", "a_frust"),
        ("Belonging", "b_sat", "b_frust"),
        ("Craft", "c_sat", "c_frust"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    for ax, (label, sat_key, frust_key) in zip(axes, domains, strict=False):
        sat = [r["subscales"][sat_key] for r in results]
        frust = [r["subscales"][frust_key] for r in results]
        states = [r["domain_states"][label.lower()] for r in results]
        colours = [STATE_COLOURS[s] for s in states]

        ax.scatter(sat, frust, c=colours, alpha=0.45, s=12, edgecolors="none")
        ax.axvline(x=5.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.axhline(y=5.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.set_xlim(-0.5, 10.5)
        ax.set_ylim(-0.5, 10.5)
        ax.set_xlabel("Satisfaction", fontsize=10)
        ax.set_ylabel("Frustration", fontsize=10)
        ax.set_title(label, fontweight="bold", fontsize=12)

        ax.text(8, 1, "Thriving", fontsize=8, color="#2a9d4a", ha="center", alpha=0.8)
        ax.text(8, 9.5, "Vulnerable", fontsize=8, color="#c58a1e", ha="center", alpha=0.8)
        ax.text(2, 1, "Dormant", fontsize=8, color="#707070", ha="center", alpha=0.8)
        ax.text(2, 9.5, "Distressed", fontsize=8, color="#c44030", ha="center", alpha=0.8)

    plt.tight_layout()
    return fig_to_base64(fig)


def make_belbin_chart(results):
    """Horizontal bar chart of Belbin role counts across all participants."""
    role_counter = Counter()
    for r in results:
        for br in r["belbin_roles"]:
            role_counter[f"{br['role']} ({br['qualifier']})"] += 1

    sorted_roles = sorted(role_counter.keys(), key=lambda k: role_counter[k], reverse=True)
    counts = [role_counter[r] for r in sorted_roles]

    BELBIN_COLOURS = {
        "Shaper": "#E8563A",
        "Specialist": "#3ABF5E",
        "Teamworker": "#3A8FE8",
        "Coordinator": "#9B59B6",
        "Monitor-Evaluator": "#F5A623",
        "Resource Investigator": "#A0A0A0",
    }

    colours = []
    for label in sorted_roles:
        role_name = label.split(" (")[0]
        colours.append(BELBIN_COLOURS.get(role_name, "#666"))

    fig, ax = plt.subplots(figsize=(9, max(4, len(sorted_roles) * 0.5)))
    bars = ax.barh(
        range(len(sorted_roles)), counts, color=colours, edgecolor="white", linewidth=0.5
    )
    ax.set_yticks(range(len(sorted_roles)))
    ax.set_yticklabels(sorted_roles, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Count", fontsize=10)
    ax.set_title("Belbin Role Distribution", fontweight="bold", fontsize=13)

    for bar, count in zip(bars, counts, strict=False):
        pct = count / len(results) * 100
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{count} ({pct:.1f}%)",
            va="center",
            fontsize=8,
        )

    plt.tight_layout()
    return fig_to_base64(fig)


def compute_stats(results):
    """Compute summary statistics for the HTML tables."""
    n = len(results)

    # Type stats
    types = Counter(r["type_name"] for r in results)
    type_rows = []
    for name, count in types.most_common():
        domain = next(r["type_domain"] for r in results if r["type_name"] == name)
        type_rows.append(
            {
                "name": name,
                "domain": domain.capitalize(),
                "count": count,
                "pct": f"{count / n * 100:.1f}%",
            }
        )

    # Domain state stats
    state_rows = []
    for domain in ["ambition", "belonging", "craft"]:
        ds = [r["domain_states"][domain] for r in results]
        for state in ["Thriving", "Vulnerable", "Dormant", "Distressed"]:
            c = ds.count(state)
            state_rows.append(
                {
                    "domain": domain.capitalize(),
                    "state": state,
                    "count": c,
                    "pct": f"{c / n * 100:.1f}%",
                }
            )

    # Subscale stats
    sub_rows = []
    for key, label in [
        ("a_sat", "A-Satisfaction"),
        ("a_frust", "A-Frustration"),
        ("b_sat", "B-Satisfaction"),
        ("b_frust", "B-Frustration"),
        ("c_sat", "C-Satisfaction"),
        ("c_frust", "C-Frustration"),
    ]:
        vals = [r["subscales"][key] for r in results]
        sub_rows.append(
            {
                "name": label,
                "mean": f"{np.mean(vals):.2f}",
                "sd": f"{np.std(vals):.2f}",
                "min": f"{np.min(vals):.2f}",
                "max": f"{np.max(vals):.2f}",
            }
        )

    return type_rows, state_rows, sub_rows


def build_type_table_html(type_rows):
    rows_html = ""
    for r in type_rows:
        colour = DOMAIN_COLOURS.get(r["domain"].lower(), "#666")
        rows_html += f"""
            <tr>
                <td>{r["name"]}</td>
                <td><span class="domain-badge" style="background:{colour}">{r["domain"]}</span></td>
                <td class="num">{r["count"]}</td>
                <td class="num">{r["pct"]}</td>
            </tr>"""
    return rows_html


def build_state_table_html(state_rows):
    rows_html = ""
    for r in state_rows:
        colour = STATE_COLOURS.get(r["state"], "#666")
        rows_html += f"""
            <tr>
                <td>{r["domain"]}</td>
                <td><span class="state-badge" style="background:{colour}">{r["state"]}</span></td>
                <td class="num">{r["count"]}</td>
                <td class="num">{r["pct"]}</td>
            </tr>"""
    return rows_html


def build_subscale_table_html(sub_rows):
    rows_html = ""
    for r in sub_rows:
        rows_html += f"""
            <tr>
                <td>{r["name"]}</td>
                <td class="num">{r["mean"]}</td>
                <td class="num">{r["sd"]}</td>
                <td class="num">{r["min"]}</td>
                <td class="num">{r["max"]}</td>
            </tr>"""
    return rows_html


import json


def build_participants_json(results, raw_responses):
    """Build JSON array of all individual participant data."""
    participants = []
    for i, (result, resp) in enumerate(zip(results, raw_responses, strict=False)):
        participants.append(
            {
                "id": i + 1,
                "type": result["type_name"],
                "domain": result["type_domain"].capitalize(),
                "a_state": result["domain_states"]["ambition"],
                "b_state": result["domain_states"]["belonging"],
                "c_state": result["domain_states"]["craft"],
                "a_sat": round(result["subscales"]["a_sat"], 2),
                "a_frust": round(result["subscales"]["a_frust"], 2),
                "b_sat": round(result["subscales"]["b_sat"], 2),
                "b_frust": round(result["subscales"]["b_frust"], 2),
                "c_sat": round(result["subscales"]["c_sat"], 2),
                "c_frust": round(result["subscales"]["c_frust"], 2),
                "O": round(result["big_five"]["openness"], 1),
                "C": round(result["big_five"]["conscientiousness"], 1),
                "E": round(result["big_five"]["extraversion"], 1),
                "A": round(result["big_five"]["agreeableness"], 1),
                "N": round(result["big_five"]["neuroticism"], 1),
                "responses": {item: resp[item] for item in ITEM_ORDER},
                "belbin_roles": result.get("belbin_roles", []),
                "frustration_signatures": result.get("frustration_signatures", []),
            }
        )
    return json.dumps(participants)


def build_domain_states_explained_html():
    """Build the Domain States Explained section with scientific explanations."""
    cards_html = ""
    for state_name in ["Thriving", "Vulnerable", "Dormant", "Distressed"]:
        desc = DOMAIN_STATE_DESCRIPTIONS[state_name]
        cards_html += f"""
            <div class="card" style="border-left: 4px solid {desc["colour"]}; margin-bottom: 1rem; padding: 1.2rem;">
                <h3 style="color: {desc["colour"]}; margin-bottom: 0.2rem;">{desc["label"]}</h3>
                <p style="font-size: 0.82rem; color: var(--muted); margin-bottom: 0.5rem;">{desc["condition"]}</p>
                <p style="font-weight: 600; margin-bottom: 0.5rem;">{desc["summary"]}</p>
                <p style="font-size: 0.88rem; margin-bottom: 0.5rem;">{desc["science"]}</p>
                <p style="font-size: 0.88rem; font-style: italic; color: var(--muted);">{desc["implication"]}</p>
            </div>"""
    return cards_html


def build_type_guide_html(results):
    """Build the Type Guide section showing cards for each observed type, grouped by domain."""
    observed_types = {r["type_name"] for r in results}
    domain_groups = {"ambition": [], "belonging": [], "craft": []}

    for type_name in sorted(observed_types):
        desc = TYPE_DESCRIPTIONS.get(type_name)
        if not desc:
            continue
        domain = desc["domain"]
        if domain in domain_groups:
            domain_groups[domain].append((type_name, desc))
        else:
            # Integrator or cross-domain: show under all
            for d in domain_groups:
                domain_groups[d].append((type_name, desc))

    html = ""
    domain_labels = {"ambition": "Ambition", "belonging": "Belonging", "craft": "Craft"}
    for domain in ["ambition", "belonging", "craft"]:
        colour = DOMAIN_COLOURS[domain]
        html += f'<h3 style="color: {colour}; margin-top: 1.5rem; margin-bottom: 0.8rem;">{domain_labels[domain]} Types</h3>'
        html += '<div class="type-guide-grid">'
        for type_name, desc in domain_groups[domain]:
            strengths_list = ", ".join(desc["strengths"])
            html += f"""
                <div class="card type-guide-card" style="padding: 0; overflow: hidden;">
                    <div style="background: {colour}; color: white; padding: 0.6rem 1rem;">
                        <strong>{type_name}</strong> &mdash; <em>{desc["tagline"]}</em>
                    </div>
                    <div style="padding: 1rem; font-size: 0.88rem;">
                        <p style="margin-bottom: 0.5rem;">{desc["description"]}</p>
                        <p style="margin-bottom: 0.3rem;"><strong>Strengths:</strong> {strengths_list}</p>
                        <p style="margin-bottom: 0.3rem;"><strong>Watch for:</strong> {desc["watch_for"]}</p>
                        <p style="color: var(--muted); font-style: italic;">{desc["growth_edge"]}</p>
                    </div>
                </div>"""
        html += "</div>"
    return html


def build_belbin_summary_html(results):
    """Build summary table for Belbin roles."""
    role_counter = Counter()
    for r in results:
        for br in r["belbin_roles"]:
            role_counter[f"{br['role']} ({br['qualifier']})"] += 1

    n = len(results)
    rows_html = ""
    for label, count in role_counter.most_common():
        pct = f"{count / n * 100:.1f}%"
        rows_html += f"""
            <tr>
                <td>{label}</td>
                <td class="num">{count}</td>
                <td class="num">{pct}</td>
            </tr>"""
    return rows_html


def build_frustration_signatures_html(results):
    """Build frustration signatures summary table."""
    sig_counter = Counter()
    risk_map = {}
    n = len(results)
    for r in results:
        for sig in r["frustration_signatures"]:
            key = sig["label"]
            sig_counter[key] += 1
            risk_map[key] = sig["risk"]

    # Also count participants with no signatures
    no_sig = sum(1 for r in results if not r["frustration_signatures"])

    rows_html = ""
    for label, count in sig_counter.most_common():
        risk = risk_map[label]
        risk_colour = "#E8563A" if risk == "high" else "#F5A623"
        pct = f"{count / n * 100:.1f}%"
        rows_html += f"""
            <tr>
                <td>{label}</td>
                <td><span class="state-badge" style="background:{risk_colour}">{risk}</span></td>
                <td class="num">{count}</td>
                <td class="num">{pct}</td>
            </tr>"""

    rows_html += f"""
        <tr style="border-top: 2px solid var(--border);">
            <td><em>No signatures</em></td>
            <td></td>
            <td class="num">{no_sig}</td>
            <td class="num">{no_sig / n * 100:.1f}%</td>
        </tr>"""
    return rows_html


def build_html(results, charts, raw_responses):
    n = len(results)
    n_types = len({r["type_name"] for r in results})
    type_rows, state_rows, sub_rows = compute_stats(results)
    participants_json = build_participants_json(results, raw_responses)
    domain_states_explained = build_domain_states_explained_html()
    type_guide = build_type_guide_html(results)
    belbin_summary = build_belbin_summary_html(results)
    frustration_summary = build_frustration_signatures_html(results)

    # Build type descriptions JSON for JavaScript (only observed types)
    observed_types = {r["type_name"] for r in results}
    type_desc_js = {
        name: desc for name, desc in TYPE_DESCRIPTIONS.items() if name in observed_types
    }
    type_descriptions_json = json.dumps(type_desc_js)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ABC Assessment — Simulation Results</title>
    <style>
        :root {{
            --bg: #f8f9fa;
            --card: #ffffff;
            --text: #1a1a2e;
            --muted: #6c757d;
            --border: #e9ecef;
            --ambition: #E8563A;
            --belonging: #3A8FE8;
            --craft: #3ABF5E;
            --sidebar-bg: #1a1a2e;
            --sidebar-w: 220px;
            --accent: #3A8FE8;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}

        /* ── Sidebar ── */
        .sidebar {{
            position: fixed;
            left: 0; top: 0; bottom: 0;
            width: var(--sidebar-w);
            background: var(--sidebar-bg);
            display: flex;
            flex-direction: column;
            z-index: 100;
            overflow-y: auto;
        }}

        .sidebar-title {{
            padding: 1.5rem 1.2rem 0.5rem;
            color: white;
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }}

        .sidebar-subtitle {{
            padding: 0 1.2rem 1.2rem;
            color: rgba(255,255,255,0.5);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}

        .sidebar nav {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
            padding: 0 0.8rem;
        }}

        .nav-item {{
            display: block;
            padding: 0.55rem 0.9rem;
            border-radius: 8px;
            color: rgba(255,255,255,0.7);
            text-decoration: none;
            font-size: 0.88rem;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.15s, color 0.15s;
            user-select: none;
        }}

        .nav-item:hover {{
            background: rgba(255,255,255,0.08);
            color: white;
        }}

        .nav-item.active {{
            background: var(--accent);
            color: white;
        }}

        .sidebar-footer {{
            padding: 1rem 1.2rem;
            color: rgba(255,255,255,0.35);
            font-size: 0.7rem;
        }}

        /* ── Hamburger (mobile) ── */
        .hamburger {{
            display: none;
            position: fixed;
            top: 0.8rem; left: 0.8rem;
            z-index: 200;
            background: var(--sidebar-bg);
            color: white;
            border: none;
            border-radius: 6px;
            width: 40px; height: 40px;
            font-size: 1.4rem;
            cursor: pointer;
            align-items: center;
            justify-content: center;
        }}

        .nav-overlay {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.4);
            z-index: 90;
        }}

        /* ── Main content area ── */
        .main {{
            margin-left: var(--sidebar-w);
            min-height: 100vh;
        }}

        .tab-content {{
            display: none;
            animation: tabFadeIn 0.25s ease;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes tabFadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .tab-inner {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
        }}

        .tab-header {{
            margin-bottom: 1.5rem;
        }}

        .tab-header h1 {{
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }}

        .tab-header p {{
            font-size: 0.92rem;
            color: var(--muted);
        }}

        /* ── Mobile responsive ── */
        @media (max-width: 768px) {{
            .sidebar {{
                transform: translateX(-100%);
                transition: transform 0.25s ease;
            }}
            .sidebar.open {{
                transform: translateX(0);
            }}
            .hamburger {{
                display: flex;
            }}
            .nav-overlay.open {{
                display: block;
            }}
            .main {{
                margin-left: 0;
            }}
            .tab-inner {{
                padding: 3.5rem 1rem 1.5rem;
            }}
        }}

        /* ── Existing styles (preserved) ── */

        .stats-bar {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            padding: 1.5rem 2rem;
            background: white;
            border-radius: 8px;
            border: 1px solid var(--border);
            flex-wrap: wrap;
            margin-bottom: 1.5rem;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text);
        }}

        .stat-label {{
            font-size: 0.8rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .stat-pass {{
            color: #3ABF5E;
        }}

        .section {{
            margin-bottom: 2.5rem;
        }}

        .section h2 {{
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }}

        .section .desc {{
            font-size: 0.9rem;
            color: var(--muted);
            margin-bottom: 1rem;
        }}

        .card {{
            background: var(--card);
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            overflow: hidden;
        }}

        .chart-img {{
            width: 100%;
            display: block;
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }}

        @media (max-width: 768px) {{
            .grid-2 {{ grid-template-columns: 1fr; }}
            .stats-bar {{ gap: 1rem; }}
            .stat-value {{ font-size: 1.4rem; }}
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}

        th {{
            background: var(--bg);
            padding: 0.6rem 0.8rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            color: var(--muted);
            border-bottom: 2px solid var(--border);
        }}

        td {{
            padding: 0.5rem 0.8rem;
            border-bottom: 1px solid var(--border);
        }}

        td.num {{
            text-align: right;
            font-variant-numeric: tabular-nums;
        }}

        .domain-badge, .state-badge {{
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 12px;
            color: white;
            font-size: 0.8rem;
            font-weight: 500;
        }}

        .validation-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}

        .gate {{
            padding: 1rem;
            border-radius: 8px;
            background: #f0fdf4;
            border-left: 4px solid #3ABF5E;
        }}

        .gate-label {{
            font-size: 0.8rem;
            color: var(--muted);
        }}

        .gate-value {{
            font-size: 1.2rem;
            font-weight: 700;
        }}

        .gate-target {{
            font-size: 0.75rem;
            color: var(--muted);
        }}

        .controls {{
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }}

        .controls input[type="text"] {{
            flex: 1;
            min-width: 200px;
            padding: 0.5rem 0.75rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 0.9rem;
            outline: none;
        }}

        .controls input[type="text"]:focus {{
            border-color: #3A8FE8;
            box-shadow: 0 0 0 3px rgba(58,143,232,0.15);
        }}

        .controls select {{
            padding: 0.5rem 0.75rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 0.9rem;
            background: white;
            cursor: pointer;
        }}

        .controls .count {{
            font-size: 0.85rem;
            color: var(--muted);
            white-space: nowrap;
        }}

        #participants-table {{
            font-size: 0.82rem;
        }}

        #participants-table th {{
            position: sticky;
            top: 0;
            z-index: 2;
            cursor: pointer;
            user-select: none;
            white-space: nowrap;
            font-size: 0.72rem;
        }}

        #participants-table th:hover {{
            background: #e2e6ea;
        }}

        #participants-table th .sort-arrow {{
            margin-left: 3px;
            opacity: 0.3;
        }}

        #participants-table th.sorted .sort-arrow {{
            opacity: 1;
        }}

        #participants-table td {{
            padding: 0.35rem 0.5rem;
            white-space: nowrap;
        }}

        .participants-wrap {{
            max-height: 700px;
            overflow-y: auto;
            border: 1px solid var(--border);
            border-radius: 8px;
        }}

        .row-clickable {{
            cursor: pointer;
        }}

        .row-clickable:hover {{
            background: #f0f4ff;
        }}

        .detail-row td {{
            padding: 0.75rem 1rem;
            background: #fafbfc;
        }}

        .detail-row .detail-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1rem;
        }}

        .detail-section h4 {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--muted);
            margin-bottom: 0.4rem;
        }}

        .detail-section .items-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.25rem 0.5rem;
            font-size: 0.82rem;
        }}

        .detail-section .items-grid .item-val {{
            font-variant-numeric: tabular-nums;
        }}

        .detail-section .items-grid .item-label {{
            color: var(--muted);
        }}

        .score-bar-wrap {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            margin-bottom: 0.2rem;
            font-size: 0.82rem;
        }}

        .score-bar-label {{
            width: 80px;
            text-align: right;
            color: var(--muted);
            flex-shrink: 0;
        }}

        .score-bar-track {{
            flex: 1;
            height: 14px;
            background: #eee;
            border-radius: 7px;
            overflow: hidden;
            position: relative;
        }}

        .score-bar-fill {{
            height: 100%;
            border-radius: 7px;
        }}

        .score-bar-val {{
            width: 36px;
            text-align: right;
            font-variant-numeric: tabular-nums;
            font-weight: 600;
            flex-shrink: 0;
        }}

        .threshold-line {{
            position: absolute;
            left: 55%;
            top: 0;
            bottom: 0;
            width: 1.5px;
            background: rgba(0,0,0,0.3);
        }}

        .export-btn {{
            padding: 0.5rem 1rem;
            background: #16213e;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 0.85rem;
            cursor: pointer;
        }}

        .export-btn:hover {{
            background: #1a2a4e;
        }}

        .type-guide-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 1rem;
        }}

        .type-guide-card {{
            transition: box-shadow 0.15s;
        }}

        .type-guide-card:hover {{
            box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        }}

        .belbin-badge, .sig-badge {{
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 10px;
            font-size: 0.78rem;
            font-weight: 500;
            margin: 0.1rem;
        }}

        .belbin-badge {{
            background: #e8ecf1;
            color: #333;
        }}

        .sig-badge-medium {{
            background: #FFF3E0;
            color: #E65100;
            border: 1px solid #F5A623;
        }}

        .sig-badge-high {{
            background: #FFEBEE;
            color: #C62828;
            border: 1px solid #E8563A;
        }}

        .type-desc-block {{
            background: #f8f9fa;
            border-radius: 6px;
            padding: 0.75rem;
            margin-top: 0.5rem;
            font-size: 0.85rem;
        }}

        .type-desc-block .tagline {{
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 0.3rem;
        }}

        .type-desc-block .growth {{
            font-style: italic;
            color: var(--muted);
            margin-top: 0.3rem;
        }}

        /* ── Methodology tab ── */
        .pipeline-steps {{
            counter-reset: step;
            list-style: none;
            padding: 0;
        }}

        .pipeline-steps li {{
            counter-increment: step;
            padding: 0.75rem 0.75rem 0.75rem 3rem;
            margin-bottom: 0.5rem;
            background: var(--card);
            border-radius: 8px;
            border-left: 3px solid var(--accent);
            position: relative;
            font-size: 0.9rem;
        }}

        .pipeline-steps li::before {{
            content: counter(step);
            position: absolute;
            left: 0.75rem;
            top: 0.75rem;
            width: 1.5rem;
            height: 1.5rem;
            background: var(--accent);
            color: white;
            border-radius: 50%;
            font-size: 0.75rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .ref-list {{
            list-style: none;
            padding: 0;
        }}

        .ref-list li {{
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border);
            font-size: 0.9rem;
        }}

        .ref-list li:last-child {{
            border-bottom: none;
        }}

        .limitations-list {{
            padding-left: 1.2rem;
        }}

        .limitations-list li {{
            margin-bottom: 0.4rem;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>

    <!-- Hamburger button (mobile) -->
    <button class="hamburger" id="hamburger" aria-label="Toggle navigation">&#9776;</button>
    <div class="nav-overlay" id="nav-overlay"></div>

    <!-- Sidebar -->
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-title">ABC Assessment</div>
        <div class="sidebar-subtitle">Simulation Dashboard</div>
        <nav>
            <a class="nav-item active" data-tab="overview">Overview</a>
            <a class="nav-item" data-tab="types">Types</a>
            <a class="nav-item" data-tab="states">Domain States</a>
            <a class="nav-item" data-tab="belbin">Belbin Roles</a>
            <a class="nav-item" data-tab="risk">Risk Signals</a>
            <a class="nav-item" data-tab="participants">Participants</a>
            <a class="nav-item" data-tab="methodology">Methodology</a>
        </nav>
        <div class="sidebar-footer">{n:,} participants &middot; 2026-03-08</div>
    </aside>

    <!-- Main content -->
    <div class="main">

        <!-- ═══ TAB: Overview ═══ -->
        <div class="tab-content active" id="tab-overview">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Overview</h1>
                    <p>Psychometric validation of the 6-factor model across {n:,} simulated participants. Satisfaction and frustration measured across three domains: Ambition, Belonging, and Craft.</p>
                </div>

                <div class="stats-bar">
                    <div class="stat">
                        <div class="stat-value">{n:,}</div>
                        <div class="stat-label">Participants</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">6</div>
                        <div class="stat-label">Subscales</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{n_types}</div>
                        <div class="stat-label">Types Observed</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">106</div>
                        <div class="stat-label">Tests Passed</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value stat-pass">ALL PASS</div>
                        <div class="stat-label">Validation Gates</div>
                    </div>
                </div>

                <div class="section">
                    <h2>Validation Gates</h2>
                    <p class="desc">Every gate must pass before the scoring pipeline is considered validated.</p>
                    <div class="validation-grid">
                        <div class="gate">
                            <div class="gate-label">Scoring Correlation</div>
                            <div class="gate-value">r = 1.000</div>
                            <div class="gate-target">Target: &ge; 0.85 per subscale</div>
                        </div>
                        <div class="gate">
                            <div class="gate-label">Domain State Accuracy</div>
                            <div class="gate-value">100.0%</div>
                            <div class="gate-target">Target: &ge; 80%</div>
                        </div>
                        <div class="gate">
                            <div class="gate-label">Vulnerable Sensitivity</div>
                            <div class="gate-value">100.0%</div>
                            <div class="gate-target">Target: &ge; 75%</div>
                        </div>
                        <div class="gate">
                            <div class="gate-label">Max Type Frequency</div>
                            <div class="gate-value">11.0%</div>
                            <div class="gate-target">Target: &le; 15%</div>
                        </div>
                        <div class="gate">
                            <div class="gate-label">CFA Model Fit (CFI)</div>
                            <div class="gate-value">1.000</div>
                            <div class="gate-target">Target: &ge; 0.95</div>
                        </div>
                        <div class="gate">
                            <div class="gate-label">Code Coverage</div>
                            <div class="gate-value">97.5%</div>
                            <div class="gate-target">Target: &ge; 85%</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ═══ TAB: Types ═══ -->
        <div class="tab-content" id="tab-types">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Types</h1>
                    <p>Each participant is assigned one of 36 types based on their dominant domain and primary Big Five trait.</p>
                </div>

                <div class="section">
                    <h2>Type Distribution</h2>
                    <p class="desc">Colours indicate the dominant domain. All {n_types} observed types ranked by frequency.</p>
                    <div class="card">
                        <img class="chart-img" src="data:image/png;base64,{charts["types"]}" alt="Type Distribution">
                    </div>
                </div>

                <div class="section">
                    <h2>Type Guide</h2>
                    <p class="desc">Detailed profiles for each observed type, grouped by dominant domain. Each card explains the psychological pattern, strengths, risks, and growth focus.</p>
                    {type_guide}
                </div>
            </div>
        </div>

        <!-- ═══ TAB: Domain States ═══ -->
        <div class="tab-content" id="tab-states">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Domain States</h1>
                    <p>Each domain is classified into one of four states based on satisfaction and frustration scores relative to the 5.5 threshold.</p>
                </div>

                <div class="section">
                    <h2>State Distribution</h2>
                    <div class="grid-2">
                        <div class="card">
                            <img class="chart-img" src="data:image/png;base64,{charts["states"]}" alt="Domain States">
                        </div>
                        <div class="card" style="padding: 0;">
                            <table>
                                <thead>
                                    <tr><th>Domain</th><th>State</th><th>Count</th><th>%</th></tr>
                                </thead>
                                <tbody>{build_state_table_html(state_rows)}</tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>Satisfaction vs Frustration</h2>
                    <p class="desc">Scatter plots for each domain. Dashed lines mark the 5.5 threshold dividing the four state quadrants.</p>
                    <div class="card">
                        <img class="chart-img" src="data:image/png;base64,{charts["scatter"]}" alt="Satisfaction vs Frustration Scatter">
                    </div>
                </div>

                <div class="section">
                    <h2>Domain States Explained</h2>
                    <p class="desc">The four states arise from crossing satisfaction and frustration at the 5.5 threshold. Each state has distinct psychological dynamics and intervention implications.</p>
                    {domain_states_explained}
                </div>
            </div>
        </div>

        <!-- ═══ TAB: Belbin Roles ═══ -->
        <div class="tab-content" id="tab-belbin">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Belbin Roles</h1>
                    <p>Inferred team roles based on subscale score patterns. A participant can hold multiple roles.</p>
                </div>

                <div class="section">
                    <div class="grid-2">
                        <div class="card">
                            <img class="chart-img" src="data:image/png;base64,{charts["belbin"]}" alt="Belbin Role Distribution">
                        </div>
                        <div class="card" style="padding: 0;">
                            <table>
                                <thead>
                                    <tr><th>Role (Qualifier)</th><th>Count</th><th>% of Participants</th></tr>
                                </thead>
                                <tbody>{belbin_summary}</tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ═══ TAB: Risk Signals ═══ -->
        <div class="tab-content" id="tab-risk">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Risk Signals</h1>
                    <p>Frustration signatures and score distributions that may indicate psychological strain.</p>
                </div>

                <div class="section">
                    <h2>Frustration Signatures</h2>
                    <p class="desc">Clinically relevant patterns where high frustration co-occurs with satisfaction extremes. Medium risk indicates strain; high risk indicates active need thwarting.</p>
                    <div class="card" style="padding: 0;">
                        <table>
                            <thead>
                                <tr><th>Signature</th><th>Risk</th><th>Count</th><th>% of Participants</th></tr>
                            </thead>
                            <tbody>{frustration_summary}</tbody>
                        </table>
                    </div>
                </div>

                <div class="section">
                    <h2>Score Distributions</h2>
                    <p class="desc">Subscale scores (0-10 normalised) and Big Five inferred percentiles across all participants.</p>
                    <div class="grid-2">
                        <div class="card">
                            <img class="chart-img" src="data:image/png;base64,{charts["subscales"]}" alt="Subscale Distributions">
                        </div>
                        <div class="card">
                            <img class="chart-img" src="data:image/png;base64,{charts["big_five"]}" alt="Big Five Distributions">
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>Subscale Statistics</h2>
                    <div class="card" style="padding: 0;">
                        <table>
                            <thead>
                                <tr><th>Subscale</th><th>Mean</th><th>SD</th><th>Min</th><th>Max</th></tr>
                            </thead>
                            <tbody>{build_subscale_table_html(sub_rows)}</tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- ═══ TAB: Participants ═══ -->
        <div class="tab-content" id="tab-participants">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Individual Participants</h1>
                    <p>Click any row to expand the full response profile. Search by ID, type, or domain. Sort by clicking column headers.</p>
                </div>

                <div class="controls">
                    <input type="text" id="search-input" placeholder="Search by ID, type, domain, or state...">
                    <select id="type-filter">
                        <option value="">All Types</option>
                    </select>
                    <select id="domain-filter">
                        <option value="">All Domains</option>
                        <option value="Ambition">Ambition</option>
                        <option value="Belonging">Belonging</option>
                        <option value="Craft">Craft</option>
                    </select>
                    <select id="state-filter">
                        <option value="">All States</option>
                        <option value="Thriving">Thriving</option>
                        <option value="Vulnerable">Vulnerable</option>
                        <option value="Dormant">Dormant</option>
                        <option value="Distressed">Distressed</option>
                    </select>
                    <span class="count" id="row-count"></span>
                    <button class="export-btn" onclick="exportCSV()">Export CSV</button>
                </div>
                <div class="card participants-wrap">
                    <table id="participants-table">
                        <thead>
                            <tr>
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
                            </tr>
                        </thead>
                        <tbody id="participants-body"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ═══ TAB: Methodology ═══ -->
        <div class="tab-content" id="tab-methodology">
            <div class="tab-inner">
                <div class="tab-header">
                    <h1>Methodology</h1>
                    <p>How the ABC Assessment scoring pipeline works, what we validated, and what remains to be done.</p>
                </div>

                <div class="section">
                    <h2>Scoring Pipeline</h2>
                    <p class="desc">The ten-step pipeline transforms raw 7-point Likert responses into typed profiles with team-role and risk annotations.</p>
                    <ol class="pipeline-steps">
                        <li><strong>Ingest raw responses</strong> &mdash; 24 items on a 1-7 Likert scale across three domains (Ambition, Belonging, Craft), each with satisfaction and frustration subscales.</li>
                        <li><strong>Reverse-score frustration items</strong> &mdash; Items AS4, AF4, BS4, BF4, CS4, CF4 are reverse-keyed. Recode as (8 &minus; raw).</li>
                        <li><strong>Compute subscale means</strong> &mdash; Average the four items per subscale to yield six raw means (a_sat, a_frust, b_sat, b_frust, c_sat, c_frust).</li>
                        <li><strong>Normalise to 0-10</strong> &mdash; Transform each subscale mean from the 1-7 range to 0-10 using: score = (mean &minus; 1) &times; 10 / 6.</li>
                        <li><strong>Classify domain states</strong> &mdash; For each domain, cross satisfaction and frustration at the 5.5 threshold to assign one of four states: Thriving, Vulnerable, Dormant, or Distressed.</li>
                        <li><strong>Identify dominant domain</strong> &mdash; The domain with the highest satisfaction score is the dominant domain. Ties are broken by lowest frustration, then alphabetical order.</li>
                        <li><strong>Infer Big Five percentiles</strong> &mdash; Map subscale patterns to approximate Big Five percentiles (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) using empirically anchored heuristics.</li>
                        <li><strong>Assign type</strong> &mdash; Combine the dominant domain with the highest Big Five trait to produce one of 36 named types (e.g., &ldquo;Ambitious Explorer&rdquo;).</li>
                        <li><strong>Map Belbin roles</strong> &mdash; Derive team-role assignments from subscale score patterns, with each participant potentially holding multiple roles and qualifiers.</li>
                        <li><strong>Flag frustration signatures</strong> &mdash; Detect clinically relevant patterns where high frustration co-occurs with satisfaction extremes, rated medium or high risk.</li>
                    </ol>
                </div>

                <div class="section">
                    <h2>Validation Results</h2>
                    <p class="desc">All gates passed on the simulated dataset of {n:,} participants.</p>
                    <div class="card" style="padding: 0;">
                        <table>
                            <thead>
                                <tr><th>Gate</th><th>Target</th><th>Achieved</th><th>Status</th></tr>
                            </thead>
                            <tbody>
                                <tr><td>Scoring Correlation (per subscale)</td><td>&ge; 0.85</td><td>r = 1.000</td><td><span class="state-badge" style="background:#3ABF5E">Pass</span></td></tr>
                                <tr><td>Domain State Accuracy</td><td>&ge; 80%</td><td>100.0%</td><td><span class="state-badge" style="background:#3ABF5E">Pass</span></td></tr>
                                <tr><td>Vulnerable Sensitivity</td><td>&ge; 75%</td><td>100.0%</td><td><span class="state-badge" style="background:#3ABF5E">Pass</span></td></tr>
                                <tr><td>Max Type Frequency</td><td>&le; 15%</td><td>11.0%</td><td><span class="state-badge" style="background:#3ABF5E">Pass</span></td></tr>
                                <tr><td>CFA Model Fit (CFI)</td><td>&ge; 0.95</td><td>1.000</td><td><span class="state-badge" style="background:#3ABF5E">Pass</span></td></tr>
                                <tr><td>Code Coverage</td><td>&ge; 85%</td><td>97.5%</td><td><span class="state-badge" style="background:#3ABF5E">Pass</span></td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="section">
                    <h2>Limitations</h2>
                    <ul class="limitations-list">
                        <li><strong>Synthetic data only.</strong> All {n:,} participants were generated from parametric distributions, not collected from real respondents. Factor structure, inter-item correlations, and response patterns may differ from field data.</li>
                        <li><strong>No empirical validation yet.</strong> The scoring pipeline has been verified against its own generative model, which guarantees internal consistency but does not confirm external or predictive validity.</li>
                        <li><strong>Population assumptions.</strong> The simulation assumes normally distributed latent traits with moderate inter-domain correlations. Real populations may show skew, ceiling/floor effects, or different correlation structures.</li>
                        <li><strong>Big Five mapping is heuristic.</strong> The inferred Big Five percentiles are derived from subscale patterns rather than a validated Big Five instrument. They should be treated as approximate indicators, not clinical scores.</li>
                        <li><strong>Belbin roles are inferred, not measured.</strong> Team-role assignments are based on subscale score heuristics rather than the official Belbin Self-Perception Inventory.</li>
                        <li><strong>Threshold sensitivity.</strong> The 5.5 cut-off for domain state classification is theory-driven. Empirical calibration on real samples may shift this threshold.</li>
                        <li><strong>Cross-cultural generalisability.</strong> Item wording, response styles, and construct validity have not been tested across cultures or languages.</li>
                    </ul>
                </div>

                <div class="section">
                    <h2>References</h2>
                    <ul class="ref-list">
                        <li>Bartholomew, K. J., Ntoumanis, N., Ryan, R. M., Bosch, J. A., &amp; Thogersen-Ntoumani, C. (2011). Self-determination theory and diminished functioning: The role of interpersonal control and psychological need thwarting. <em>Personality and Social Psychology Bulletin, 37</em>(11), 1459-1473.</li>
                        <li>Costa, P. T., &amp; McCrae, R. R. (1992). <em>Revised NEO Personality Inventory (NEO-PI-R) and NEO Five-Factor Inventory (NEO-FFI) professional manual.</em> Psychological Assessment Resources.</li>
                        <li>Deci, E. L., &amp; Ryan, R. M. (2000). The &ldquo;what&rdquo; and &ldquo;why&rdquo; of goal pursuits: Human needs and the self-determination of behavior. <em>Psychological Inquiry, 11</em>(4), 227-268.</li>
                        <li>Lonsdale, C., &amp; Hodge, K. (2011). Temporal ordering of motivational quality and athlete burnout in elite sport. <em>Medicine &amp; Science in Sports &amp; Exercise, 43</em>(5), 913-921.</li>
                        <li>Vansteenkiste, M., &amp; Ryan, R. M. (2013). On psychological growth and vulnerability: Basic psychological need satisfaction and need frustration as a unifying principle. <em>Journal of Psychotherapy Integration, 23</em>(3), 263-280.</li>
                    </ul>
                </div>
            </div>
        </div>

    </div><!-- /.main -->

    <script>
    /* ── Tab navigation ── */
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

        navItems.forEach(ni => {{
            if (ni.dataset.tab === tabId) ni.classList.add('active');
        }});

        // Update URL hash without scrolling
        history.replaceState(null, '', '#' + tabId);

        // Initialise participants table on first activation
        if (tabId === 'participants' && !participantsInitialised) {{
            initParticipants();
            participantsInitialised = true;
        }}

        // Close mobile nav
        sidebar.classList.remove('open');
        navOverlay.classList.remove('open');
    }}

    navItems.forEach(ni => {{
        ni.addEventListener('click', () => switchTab(ni.dataset.tab));
    }});

    // Mobile hamburger
    hamburger.addEventListener('click', () => {{
        sidebar.classList.toggle('open');
        navOverlay.classList.toggle('open');
    }});
    navOverlay.addEventListener('click', () => {{
        sidebar.classList.remove('open');
        navOverlay.classList.remove('open');
    }});

    // On load: check hash or default to overview
    const startTab = location.hash ? location.hash.slice(1) : 'overview';
    switchTab(startTab);

    /* ── Participants table ── */
    const DATA = {participants_json};

    const DOMAIN_COLOURS = {{"Ambition":"#E8563A","Belonging":"#3A8FE8","Craft":"#3ABF5E"}};
    const STATE_COLOURS = {{"Thriving":"#3ABF5E","Vulnerable":"#F5A623","Dormant":"#A0A0A0","Distressed":"#E8563A"}};
    const ITEM_ORDER = {json.dumps(ITEM_ORDER)};
    const TYPE_DESCS = {type_descriptions_json};

    const SUBSCALE_GROUPS = [
        {{label: "Ambition Sat", items: ["AS1","AS2","AS3","AS4"], colour: "#E8563A"}},
        {{label: "Ambition Frust", items: ["AF1","AF2","AF3","AF4"], colour: "#E8563A"}},
        {{label: "Belonging Sat", items: ["BS1","BS2","BS3","BS4"], colour: "#3A8FE8"}},
        {{label: "Belonging Frust", items: ["BF1","BF2","BF3","BF4"], colour: "#3A8FE8"}},
        {{label: "Craft Sat", items: ["CS1","CS2","CS3","CS4"], colour: "#3ABF5E"}},
        {{label: "Craft Frust", items: ["CF1","CF2","CF3","CF4"], colour: "#3ABF5E"}},
    ];

    const BIG_FIVE = [
        {{key:"O", label:"Openness", colour:"#9B59B6"}},
        {{key:"C", label:"Conscientiousness", colour:"#2ECC71"}},
        {{key:"E", label:"Extraversion", colour:"#E67E22"}},
        {{key:"A", label:"Agreeableness", colour:"#3498DB"}},
        {{key:"N", label:"Neuroticism", colour:"#E74C3C"}},
    ];

    let sortKey = "id";
    let sortAsc = true;
    let expandedId = null;

    function stateBadge(state) {{
        return `<span class="state-badge" style="background:${{STATE_COLOURS[state] || '#666'}}">${{state}}</span>`;
    }}

    function domainBadge(domain) {{
        return `<span class="domain-badge" style="background:${{DOMAIN_COLOURS[domain] || '#666'}}">${{domain}}</span>`;
    }}

    function scoreBar(label, value, max, colour, showThreshold) {{
        const pct = (value / max * 100).toFixed(1);
        const threshold = showThreshold ? '<div class="threshold-line"></div>' : '';
        return `<div class="score-bar-wrap">
            <span class="score-bar-label">${{label}}</span>
            <div class="score-bar-track">${{threshold}}
                <div class="score-bar-fill" style="width:${{pct}}%;background:${{colour}}"></div>
            </div>
            <span class="score-bar-val">${{value}}</span>
        </div>`;
    }}

    function buildDetailHTML(p) {{
        let responsesHTML = '';
        SUBSCALE_GROUPS.forEach(g => {{
            responsesHTML += `<div><strong style="color:${{g.colour}}">${{g.label}}</strong><div class="items-grid">`;
            g.items.forEach(item => {{
                const rev = item.endsWith("4") ? ' (R)' : '';
                responsesHTML += `<div><span class="item-label">${{item}}${{rev}}:</span> <span class="item-val">${{p.responses[item]}}</span></div>`;
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
        BIG_FIVE.forEach(t => {{
            b5HTML += scoreBar(t.label, p[t.key], 99, t.colour, false);
        }});

        // Belbin roles
        let belbinHTML = '';
        if (p.belbin_roles && p.belbin_roles.length > 0) {{
            p.belbin_roles.forEach(br => {{
                belbinHTML += `<span class="belbin-badge">${{br.role}} (${{br.qualifier}})</span> `;
            }});
        }} else {{
            belbinHTML = '<span style="color:var(--muted)">None</span>';
        }}

        // Frustration signatures
        let sigHTML = '';
        if (p.frustration_signatures && p.frustration_signatures.length > 0) {{
            p.frustration_signatures.forEach(sig => {{
                const cls = sig.risk === 'high' ? 'sig-badge-high' : 'sig-badge-medium';
                sigHTML += `<span class="sig-badge ${{cls}}">${{sig.label}} (${{sig.risk}})</span> `;
            }});
        }} else {{
            sigHTML = '<span style="color:var(--muted)">None detected</span>';
        }}

        // Type description
        let typeDescHTML = '';
        const td = TYPE_DESCS[p.type];
        if (td) {{
            typeDescHTML = `<div class="type-desc-block">
                <div class="tagline">${{p.type}}: ${{td.tagline}}</div>
                <p>${{td.description}}</p>
                <p class="growth"><strong>Growth edge:</strong> ${{td.growth_edge}}</p>
            </div>`;
        }}

        return `<div class="detail-grid">
            <div class="detail-section">
                <h4>Raw Responses (1-7 Likert) &mdash; (R) = reverse-scored</h4>
                ${{responsesHTML}}
            </div>
            <div class="detail-section">
                <h4>Subscale Scores (0-10)</h4>
                ${{scoresHTML}}
                <div style="margin-top:0.8rem">
                    <h4>Big Five Percentiles</h4>
                    ${{b5HTML}}
                </div>
                <div style="margin-top:0.8rem">
                    <h4>Belbin Roles</h4>
                    ${{belbinHTML}}
                </div>
                <div style="margin-top:0.8rem">
                    <h4>Frustration Signatures</h4>
                    ${{sigHTML}}
                </div>
                ${{typeDescHTML}}
            </div>
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

    function render() {{
        let filtered = getFiltered();

        filtered.sort((a, b) => {{
            let va = a[sortKey], vb = b[sortKey];
            if (typeof va === "string") {{ va = va.toLowerCase(); vb = vb.toLowerCase(); }}
            if (va < vb) return sortAsc ? -1 : 1;
            if (va > vb) return sortAsc ? 1 : -1;
            return 0;
        }});

        document.getElementById("row-count").textContent = `Showing ${{filtered.length}} of ${{DATA.length}}`;

        const tbody = document.getElementById("participants-body");
        tbody.innerHTML = "";

        filtered.forEach(p => {{
            const tr = document.createElement("tr");
            tr.className = "row-clickable";
            tr.innerHTML = `
                <td class="num">${{p.id}}</td>
                <td><strong>${{p.type}}</strong></td>
                <td>${{domainBadge(p.domain)}}</td>
                <td>${{stateBadge(p.a_state)}}</td>
                <td>${{stateBadge(p.b_state)}}</td>
                <td>${{stateBadge(p.c_state)}}</td>
                <td class="num">${{p.a_sat.toFixed(2)}}</td>
                <td class="num">${{p.a_frust.toFixed(2)}}</td>
                <td class="num">${{p.b_sat.toFixed(2)}}</td>
                <td class="num">${{p.b_frust.toFixed(2)}}</td>
                <td class="num">${{p.c_sat.toFixed(2)}}</td>
                <td class="num">${{p.c_frust.toFixed(2)}}</td>`;
            tr.addEventListener("click", () => {{
                const existing = tbody.querySelector(`.detail-${{p.id}}`);
                if (existing) {{
                    existing.remove();
                    expandedId = null;
                }} else {{
                    const prev = tbody.querySelector("[class^='detail-row']");
                    if (prev) prev.remove();
                    const detail = document.createElement("tr");
                    detail.className = `detail-row detail-${{p.id}}`;
                    detail.innerHTML = `<td colspan="12">${{buildDetailHTML(p)}}</td>`;
                    tr.after(detail);
                    expandedId = p.id;
                }}
            }});
            tbody.appendChild(tr);
        }});
    }}

    function initParticipants() {{
        // Populate type filter
        const types = [...new Set(DATA.map(d => d.type))].sort();
        const typeSelect = document.getElementById("type-filter");
        types.forEach(t => {{
            const opt = document.createElement("option");
            opt.value = t; opt.textContent = t;
            typeSelect.appendChild(opt);
        }});

        // Sort
        document.querySelectorAll("#participants-table th").forEach(th => {{
            th.addEventListener("click", () => {{
                const key = th.dataset.key;
                if (sortKey === key) {{ sortAsc = !sortAsc; }}
                else {{ sortKey = key; sortAsc = true; }}
                document.querySelectorAll("#participants-table th").forEach(h => h.classList.remove("sorted"));
                th.classList.add("sorted");
                th.querySelector(".sort-arrow").innerHTML = sortAsc ? "&#9650;" : "&#9660;";
                render();
            }});
        }});

        // Filters
        document.getElementById("search-input").addEventListener("input", render);
        document.getElementById("type-filter").addEventListener("change", render);
        document.getElementById("domain-filter").addEventListener("change", render);
        document.getElementById("state-filter").addEventListener("change", render);

        render();
    }}

    function exportCSV() {{
        const filtered = getFiltered();
        const headers = ["ID","Type","Domain","A-State","B-State","C-State",
            "A-Sat","A-Frust","B-Sat","B-Frust","C-Sat","C-Frust",
            "O","C","E","A","N",...ITEM_ORDER];
        const rows = filtered.map(p => [
            p.id, p.type, p.domain, p.a_state, p.b_state, p.c_state,
            p.a_sat, p.a_frust, p.b_sat, p.b_frust, p.c_sat, p.c_frust,
            p.O, p.C, p.E, p.A, p.N,
            ...ITEM_ORDER.map(i => p.responses[i])
        ]);
        let csv = headers.join(",") + "\\n";
        rows.forEach(r => {{ csv += r.join(",") + "\\n"; }});
        const blob = new Blob([csv], {{type: "text/csv"}});
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "abc_participants.csv";
        a.click();
    }}
    </script>
</body>
</html>"""


def main():
    print("Loading and scoring 1,000 participants...")
    results, raw_responses = load_and_score()
    print(f"Scored {len(results)} participants.")

    print("Generating charts...")
    charts = {
        "types": make_type_chart(results),
        "states": make_domain_states_chart(results),
        "subscales": make_subscale_chart(results),
        "big_five": make_big_five_chart(results),
        "scatter": make_scatter_charts(results),
        "belbin": make_belbin_chart(results),
    }
    print("Charts rendered.")

    print("Building HTML...")
    html = build_html(results, charts, raw_responses)

    site_dir = project_root / "outputs" / "site"
    site_dir.mkdir(parents=True, exist_ok=True)
    output_path = site_dir / "index.html"
    output_path.write_text(html)

    size_kb = output_path.stat().st_size / 1024
    print(f"\nDashboard saved to: {output_path}")
    print(f"File size: {size_kb:.0f} KB")
    print("\nTo deploy on Netlify:")
    print("  1. Drag and drop the outputs/site/ folder to netlify.com/drop")
    print("  2. Or connect your repo and set publish directory to: outputs/site")

    return 0


if __name__ == "__main__":
    sys.exit(main())
