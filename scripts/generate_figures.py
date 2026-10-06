"""
Generate publication-quality architectural and benchmark figures for the technical report.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "docs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Set font styling
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'


def generate_architecture_figure():
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.5)
    ax.axis('off')

    # Color palette
    c_blue = '#1E3A8A'
    c_cyan = '#0284C7'
    c_amber = '#D97706'
    c_green = '#059669'
    c_purple = '#6D28D9'
    c_light = '#F1F5F9'
    c_edge = '#94A3B8'

    boxes = [
        {"x": 0.3, "y": 2.6, "w": 1.5, "h": 1.4, "title": "Netlist Parser\n& PyG Graph", "sub": "41 structural\ngate features", "color": c_light, "border": c_blue},
        {"x": 2.2, "y": 2.6, "w": 1.6, "h": 1.4, "title": "Trained GNN\n(Statistical)", "sub": "Gate suspicion\nprobabilities s_i", "color": c_light, "border": c_blue},
        {"x": 4.2, "y": 2.6, "w": 1.7, "h": 1.4, "title": "Heuristic Layer\n(Attribution)", "sub": "17 features, tau*,\ncomposite score", "color": c_light, "border": c_cyan},
        {"x": 6.3, "y": 2.6, "w": 1.6, "h": 1.4, "title": "Region Refinement\n(Graph Pruning)", "sub": "100% recall,\nleaf pruning", "color": c_light, "border": c_amber},
        {"x": 8.3, "y": 2.6, "w": 1.4, "h": 1.4, "title": "LLM Arbitrator\n(Downstream)", "sub": "Contradiction\nanalysis & JSON", "color": c_light, "border": c_green},
    ]

    for b in boxes:
        rect = patches.FancyBboxPatch(
            (b["x"], b["y"]), b["w"], b["h"],
            boxstyle="round,pad=0.1,rounding_size=0.12",
            facecolor=b["color"], edgecolor=b["border"], linewidth=2, zorder=2
        )
        ax.add_patch(rect)
        ax.text(b["x"] + b["w"]/2, b["y"] + b["h"]*0.62, b["title"],
                ha='center', va='center', fontsize=9, fontweight='bold', color='#0F172A', zorder=3)
        ax.text(b["x"] + b["w"]/2, b["y"] + b["h"]*0.22, b["sub"],
                ha='center', va='center', fontsize=7.5, color='#475569', zorder=3)

    # Connecting arrows
    for i in range(len(boxes) - 1):
        x_start = boxes[i]["x"] + boxes[i]["w"] + 0.08
        x_end = boxes[i+1]["x"] - 0.08
        y_pos = 3.3
        ax.annotate('', xy=(x_end, y_pos), xytext=(x_start, y_pos),
                    arrowprops=dict(arrowstyle="-|>", color='#334155', lw=1.8, mutation_scale=14), zorder=4)

    # Flow Annotation Banner underneath
    banner = patches.FancyBboxPatch(
        (0.3, 0.4), 9.4, 1.6,
        boxstyle="round,pad=0.08,rounding_size=0.1",
        facecolor='#F8FAFC', edgecolor='#CBD5E1', linewidth=1.2, zorder=1
    )
    ax.add_patch(banner)

    ax.text(0.6, 1.6, "MULTI-MODAL EVIDENCE SYNTHESIS WORKFLOW", fontsize=8.5, fontweight='bold', color=c_blue)
    ax.text(0.6, 1.25, "- Statistical Detection: GNN processes graph topology and extracts top-k anomalous gates (seeds).", fontsize=7.5, color='#334155')
    ax.text(0.6, 0.95, "- Structural Validation: Intelligent heuristic quantifies internal connectivity, sequential loops, and exit ratios.", fontsize=7.5, color='#334155')
    ax.text(0.6, 0.65, "- Contextual Arbitration: LLM resolves divergence when GNN and Heuristic disagree, producing structured JSON verdict.", fontsize=7.5, color='#334155')

    fig.tight_layout()
    out_path = FIG_DIR / "architecture_pipeline.png"
    fig.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"Generated: {out_path}")


def generate_refinement_figure():
    fig, ax = plt.subplots(figsize=(9, 4), dpi=300)
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 4)
    ax.axis('off')

    c_blue = '#1E3A8A'
    c_red = '#DC2626'
    c_green = '#059669'
    c_amber = '#D97706'
    c_gray = '#94A3B8'

    # Title
    ax.text(4.5, 3.7, "Graph-Theoretic Suspicious Region Refinement Algorithm",
            ha='center', va='center', fontsize=11, fontweight='bold', color=c_blue)

    # Step 1 Box: Anchor Protection
    rect1 = patches.FancyBboxPatch(
        (0.4, 0.8), 2.5, 2.5,
        boxstyle="round,pad=0.1,rounding_size=0.1",
        facecolor='#EFF6FF', edgecolor=c_blue, linewidth=1.5
    )
    ax.add_patch(rect1)
    ax.text(1.65, 3.0, "Step 1: Anchor Protection", ha='center', va='center', fontsize=9, fontweight='bold', color=c_blue)
    ax.text(1.65, 2.4, "- Core Seeds: s_i >= 0.95\n- Sequential State:\nDFFs / Latches connected\nto seeds (triggers)\n- Critical Paths:\nSeed-to-exit shortest paths",
            ha='center', va='center', fontsize=7.5, color='#1E293B')

    # Arrow 1 -> 2
    ax.annotate('', xy=(3.3, 2.05), xytext=(2.95, 2.05),
                arrowprops=dict(arrowstyle="-|>", color='#334155', lw=1.6, mutation_scale=12))

    # Step 2 Box: Iterative Leaf Pruning
    rect2 = patches.FancyBboxPatch(
        (3.35, 0.8), 2.5, 2.5,
        boxstyle="round,pad=0.1,rounding_size=0.1",
        facecolor='#FEF3C7', edgecolor=c_amber, linewidth=1.5
    )
    ax.add_patch(rect2)
    ax.text(4.6, 3.0, "Step 2: Iterative Leaf Pruning", ha='center', va='center', fontsize=9, fontweight='bold', color='#92400E')
    ax.text(4.6, 2.4, "- Subgraph Degree <= 1\n- Score s_i < 0.30\n- Node not in protected set\n- Multi-pass cascade until\nfixpoint reached",
            ha='center', va='center', fontsize=7.5, color='#1E293B')

    # Arrow 2 -> 3
    ax.annotate('', xy=(6.25, 2.05), xytext=(5.9, 2.05),
                arrowprops=dict(arrowstyle="-|>", color='#334155', lw=1.6, mutation_scale=12))

    # Step 3 Box: High-Precision Compact Region
    rect3 = patches.FancyBboxPatch(
        (6.3, 0.8), 2.3, 2.5,
        boxstyle="round,pad=0.1,rounding_size=0.1",
        facecolor='#ECFDF5', edgecolor=c_green, linewidth=1.5
    )
    ax.add_patch(rect3)
    ax.text(7.45, 3.0, "Step 3: Refined Region", ha='center', va='center', fontsize=9, fontweight='bold', color=c_green)
    ax.text(7.45, 2.4, "100% Trojan Recall\n\nPrunes 15-26% Noise\n\nOptimized Token Cost\nfor Downstream LLM",
            ha='center', va='center', fontsize=8, fontweight='semibold', color='#065F46')

    fig.tight_layout()
    out_path = FIG_DIR / "region_refinement_diagram.png"
    fig.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"Generated: {out_path}")


def generate_benchmark_chart():
    circuits = ['s13207_T421', 's1423_T400', 's15850_T400', 's13207_T400']
    naive_precision = [53.2, 57.5, 62.0, 58.0]
    refined_precision = [71.4, 76.2, 78.6, 73.5]
    recall = [100.0, 100.0, 100.0, 100.0]
    compression = [25.5, 24.5, 21.1, 21.0]

    x = np.arange(len(circuits))
    width = 0.28

    fig, ax1 = plt.subplots(figsize=(8.5, 4.2), dpi=300)

    # Bars for precision
    b1 = ax1.bar(x - width/2, naive_precision, width, label='Naive Region Trojan Precision (%)', color='#94A3B8', edgecolor='#64748B')
    b2 = ax1.bar(x + width/2, refined_precision, width, label='Refined Region Trojan Precision (%)', color='#0284C7', edgecolor='#0369A1')

    ax1.set_ylabel('Trojan Gate Precision (%)', fontsize=9.5, fontweight='bold', color='#1E293B')
    ax1.set_ylim(0, 115)
    ax1.set_xticks(x)
    ax1.set_xticklabels(circuits, fontsize=9, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.3)

    # Line for 100% Recall
    ax2 = ax1.twinx()
    l1 = ax2.plot(x, recall, color='#059669', marker='o', linewidth=2.5, markersize=8, label='Trojan Gate Recall (100% Preserved)')
    ax2.set_ylabel('Trojan Gate Recall (%)', fontsize=9.5, fontweight='bold', color='#059669')
    ax2.set_ylim(70, 110)

    # Annotate bars
    for bar in b1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 1.5, f"{yval:.1f}%", ha='center', va='bottom', fontsize=7.5, color='#475569')
    for bar in b2:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 1.5, f"{yval:.1f}%", ha='center', va='bottom', fontsize=7.5, fontweight='bold', color='#0369A1')

    # Legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper center', bbox_to_anchor=(0.5, 1.16), ncol=3, frameon=True, fontsize=8)

    ax1.set_title("Region Refinement Benchmark: Precision Improvement with 100% Trojan Recall", fontsize=10.5, fontweight='bold', color='#1E3A8A', pad=25)

    fig.tight_layout()
    out_path = FIG_DIR / "benchmark_metrics_chart.png"
    fig.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    generate_architecture_figure()
    generate_refinement_figure()
    generate_benchmark_chart()
