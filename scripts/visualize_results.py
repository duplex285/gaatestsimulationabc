#!/usr/bin/env python3
"""Visualize ABC Assessment simulation results.

Generates charts showing type distribution, domain states,
subscale scores, and Big Five profiles for 1,000 simulated participants.

Reference: abc-assessment-spec Section 2.4 (36-type derivation)
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.python_scoring.scoring_pipeline import ABCScorer

# Domain-to-colour mapping
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


def load_and_score():
    """Load ground truth responses and score all participants."""
    data_dir = project_root / "outputs" / "datasets"
    responses_df = pd.read_csv(data_dir / "ground_truth_responses.csv")

    scorer = ABCScorer()
    results = []
    for _, row in responses_df.iterrows():
        resp = {col: int(row[col]) for col in responses_df.columns}
        results.append(scorer.score(resp))
    return results


def plot_type_distribution(results, ax):
    """Bar chart of 36-type distribution, coloured by dominant domain."""
    from collections import Counter

    type_data = [(r["type_name"], r["type_domain"]) for r in results]
    counter = Counter(t[0] for t in type_data)
    domain_of_type = {t[0]: t[1] for t in type_data}

    sorted_types = sorted(counter.keys(), key=lambda t: counter[t], reverse=True)
    counts = [counter[t] for t in sorted_types]
    colours = [DOMAIN_COLOURS[domain_of_type[t]] for t in sorted_types]

    bars = ax.barh(
        range(len(sorted_types)), counts, color=colours, edgecolor="white", linewidth=0.5
    )
    ax.set_yticks(range(len(sorted_types)))
    ax.set_yticklabels(sorted_types, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Count")
    ax.set_title("36-Type Distribution (n=1,000)", fontweight="bold")

    # Add count labels
    for bar, count in zip(bars, counts, strict=False):
        ax.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            str(count),
            va="center",
            fontsize=7,
        )

    # Legend
    from matplotlib.patches import Patch

    legend_patches = [Patch(facecolor=c, label=d.capitalize()) for d, c in DOMAIN_COLOURS.items()]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=8)


def plot_domain_states(results, ax):
    """Stacked bar chart of domain states across the three domains."""
    domains = ["ambition", "belonging", "craft"]
    states = ["Thriving", "Vulnerable", "Dormant", "Distressed"]

    data = {}
    for domain in domains:
        domain_states = [r["domain_states"][domain] for r in results]
        data[domain] = {s: domain_states.count(s) for s in states}

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
        )
        # Add percentage labels on segments >= 5%
        for i, v in enumerate(values):
            if v >= 50:
                ax.text(
                    x[i],
                    bottom[i] + v / 2,
                    f"{v / 10:.0f}%",
                    ha="center",
                    va="center",
                    fontsize=8,
                    fontweight="bold",
                )
        bottom += values

    ax.set_xticks(x)
    ax.set_xticklabels([d.capitalize() for d in domains])
    ax.set_ylabel("Participants")
    ax.set_title("Domain State Distribution", fontweight="bold")
    ax.legend(fontsize=8, loc="upper right")


def plot_subscale_distributions(results, ax):
    """Violin plot of the 6 subscale score distributions."""
    subscale_labels = ["A-Sat", "A-Frust", "B-Sat", "B-Frust", "C-Sat", "C-Frust"]
    subscale_keys = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]
    colours = ["#E8563A", "#E8563A", "#3A8FE8", "#3A8FE8", "#3ABF5E", "#3ABF5E"]

    data = [[r["subscales"][k] for r in results] for k in subscale_keys]

    parts = ax.violinplot(data, positions=range(len(data)), showmeans=True, showmedians=True)

    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(colours[i])
        pc.set_alpha(0.7)

    for key in ["cmeans", "cmedians", "cmins", "cmaxes", "cbars"]:
        if key in parts:
            parts[key].set_color("black")

    ax.set_xticks(range(len(subscale_labels)))
    ax.set_xticklabels(subscale_labels, fontsize=9)
    ax.set_ylabel("Score (0-10)")
    ax.set_ylim(-0.5, 10.5)
    ax.axhline(y=5.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.text(5.3, 5.7, "Threshold (5.5)", fontsize=7, color="gray")
    ax.set_title("Subscale Score Distributions", fontweight="bold")


def plot_big_five_profiles(results, ax):
    """Box plot of Big Five percentile distributions."""
    trait_labels = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]
    trait_keys = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]

    data = [[r["big_five"][k] for r in results] for k in trait_keys]

    bp = ax.boxplot(data, tick_labels=trait_labels, patch_artist=True, notch=True)

    colours = ["#9B59B6", "#2ECC71", "#E67E22", "#3498DB", "#E74C3C"]
    for patch, colour in zip(bp["boxes"], colours, strict=False):
        patch.set_facecolor(colour)
        patch.set_alpha(0.6)

    ax.set_ylabel("Percentile")
    ax.set_ylim(0, 100)
    ax.axhline(y=50, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.set_title("Big Five Percentile Distributions", fontweight="bold")
    ax.tick_params(axis="x", rotation=15)


def plot_domain_scatter(results, axes):
    """Scatter plots of satisfaction vs frustration for each domain, coloured by state."""
    domains = [
        ("ambition", "a_sat", "a_frust"),
        ("belonging", "b_sat", "b_frust"),
        ("craft", "c_sat", "c_frust"),
    ]

    for ax, (domain, sat_key, frust_key) in zip(axes, domains, strict=False):
        sat = [r["subscales"][sat_key] for r in results]
        frust = [r["subscales"][frust_key] for r in results]
        states = [r["domain_states"][domain] for r in results]
        colours = [STATE_COLOURS[s] for s in states]

        ax.scatter(sat, frust, c=colours, alpha=0.4, s=10, edgecolors="none")
        ax.axvline(x=5.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.axhline(y=5.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.set_xlim(-0.5, 10.5)
        ax.set_ylim(-0.5, 10.5)
        ax.set_xlabel("Satisfaction")
        ax.set_ylabel("Frustration")
        ax.set_title(f"{domain.capitalize()}", fontweight="bold")

        # Quadrant labels
        ax.text(8, 1, "Thriving", fontsize=7, color="#2a9d4a", ha="center", alpha=0.7)
        ax.text(8, 9, "Vulnerable", fontsize=7, color="#c58a1e", ha="center", alpha=0.7)
        ax.text(2, 1, "Dormant", fontsize=7, color="#707070", ha="center", alpha=0.7)
        ax.text(2, 9, "Distressed", fontsize=7, color="#c44030", ha="center", alpha=0.7)


def main():
    print("Loading and scoring 1,000 participants...")
    results = load_and_score()
    print(f"Scored {len(results)} participants.\n")

    output_dir = project_root / "outputs" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Figure 1: Overview dashboard (4 panels)
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("ABC Assessment Simulation Results (n=1,000)", fontsize=14, fontweight="bold")

    plot_type_distribution(results, axes[0, 0])
    plot_domain_states(results, axes[0, 1])
    plot_subscale_distributions(results, axes[1, 0])
    plot_big_five_profiles(results, axes[1, 1])

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(output_dir / "dashboard.png", dpi=150, bbox_inches="tight")
    print(f"Saved: {output_dir / 'dashboard.png'}")

    # Figure 2: Domain scatter plots (sat vs frust)
    fig2, axes2 = plt.subplots(1, 3, figsize=(15, 5))
    fig2.suptitle("Satisfaction vs Frustration by Domain", fontsize=13, fontweight="bold")

    plot_domain_scatter(results, axes2)

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    fig2.savefig(output_dir / "domain_scatter.png", dpi=150, bbox_inches="tight")
    print(f"Saved: {output_dir / 'domain_scatter.png'}")

    # Figure 3: Type distribution standalone (larger)
    fig3, ax3 = plt.subplots(figsize=(10, 8))
    plot_type_distribution(results, ax3)
    plt.tight_layout()
    fig3.savefig(output_dir / "type_distribution.png", dpi=150, bbox_inches="tight")
    print(f"Saved: {output_dir / 'type_distribution.png'}")

    print(f"\nAll figures saved to {output_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
