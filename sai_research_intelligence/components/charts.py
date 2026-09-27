import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

BG = "#0d1520"
CARD_BG = "#131c2b"
ACCENT = "#2dd4c8"
ACCENT_2 = "#5eead4"
TEXT = "#e6edf3"
MUTED = "#8b98a9"
GRID = "#22303f"


def _style_ax(fig, ax):
    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)


def render_trend_chart(years, counts, title="Annual Publication Trend"):
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=140)
    _style_ax(fig, ax)
    ax.plot(years, counts, color=ACCENT, linewidth=2.4, marker="o", markersize=5,
            markerfacecolor=ACCENT, markeredgecolor=CARD_BG, zorder=3)
    ax.fill_between(years, counts, color=ACCENT, alpha=0.12, zorder=1)
    for x, y in zip(years, counts):
        ax.annotate(str(y), (x, y), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=8, color=TEXT)
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left", pad=12)
    ax.set_xticks(years)
    ax.set_ylabel("Publications")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_quartile_bar(quality: dict, title="SJR Quartile Distribution"):
    """Seaborn/Matplotlib bar chart of the Q1-Q4/Unclassified split."""
    q = quality["quartile_counts"]
    labels = list(q.keys())
    values = list(q.values())
    colors = [ACCENT, ACCENT_2, "#3b82f6", "#64748b", "#334155"]
    fig, ax = plt.subplots(figsize=(5, 3.8), dpi=140)
    _style_ax(fig, ax)
    bars = ax.bar(labels, values, color=colors[: len(labels)])
    total = sum(values) or 1
    for b, v in zip(bars, values):
        pct = round(100 * v / total, 1)
        ax.annotate(f"{v}\n({pct}%)", (b.get_x() + b.get_width() / 2, b.get_height()),
                    ha="center", va="bottom", fontsize=8, color=TEXT)
    ax.set_title(title, fontsize=10.5, fontweight="bold", loc="left", pad=12)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_quality_charts(quality: dict):
    """Legacy combined view (static quartile bar + static indexing pie),
    kept for any code path that still wants a fully static pair."""
    col1, col2 = st.columns(2)
    with col1:
        render_quartile_bar(quality, "SJR Quartile Distribution (denominator: all filtered pubs)")
    with col2:
        idx = quality["indexing_counts"]
        labels = list(idx.keys())
        values = list(idx.values())
        colors = [ACCENT, "#f97316", MUTED]
        fig, ax = plt.subplots(figsize=(5, 3.8), dpi=140)
        _style_ax(fig, ax)
        wedges, _ = ax.pie(
            values, colors=colors[: len(labels)], startangle=90,
            wedgeprops=dict(width=0.42, edgecolor=CARD_BG, linewidth=2),
        )
        total = sum(values) or 1
        ax.legend(
            wedges, [f"{l} — {v} ({round(100*v/total,1)}%)" for l, v in zip(labels, values)],
            loc="center", bbox_to_anchor=(0.5, 0.5), frameon=False,
            labelcolor=TEXT, fontsize=8.5,
        )
        ax.set_title("Indexing Coverage (Unknown ≠ Non-indexed)",
                      fontsize=10.5, fontweight="bold", loc="left", pad=12)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)


def render_sdg_heatmap(df):
    rows = []
    for _, r in df.iterrows():
        for sdg in r["sdg_list"]:
            rows.append((r["school"], sdg))
    if not rows:
        st.info("No SDG-tagged publications in the current filter selection.")
        return

    long_df = pd.DataFrame(rows, columns=["school", "sdg"])
    matrix = long_df.pivot_table(index="school", columns="sdg", aggfunc=len, fill_value=0)
    matrix = matrix.reindex(sorted(matrix.columns), axis=1)
    matrix.columns = [f"SDG {c}" for c in matrix.columns]

    fig, ax = plt.subplots(figsize=(max(8, 0.62 * len(matrix.columns)), max(3.2, 0.42 * len(matrix))), dpi=140)
    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)
    sns.heatmap(
        matrix, ax=ax, cmap=sns.light_palette(ACCENT, as_cmap=True),
        linewidths=0.6, linecolor=BG, annot=True, fmt="d",
        annot_kws={"fontsize": 8, "color": TEXT},
        cbar_kws={"label": "Publication–SDG associations"},
    )
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.set_xlabel("")
    ax.set_ylabel("")
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_color(TEXT)
    cbar.ax.tick_params(colors=TEXT)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_doctype_distribution(df):
    """Seaborn count plot of Document Type distribution."""
    counts = df["doc_type"].value_counts().sort_values(ascending=True)
    if len(counts) == 0:
        st.info("No document type data in the current filter selection.")
        return
    fig, ax = plt.subplots(figsize=(7, max(2.6, 0.42 * len(counts))), dpi=140)
    _style_ax(fig, ax)
    sns.barplot(x=counts.values, y=counts.index, ax=ax, color=ACCENT, orient="h")
    for i, v in enumerate(counts.values):
        ax.annotate(str(v), (v, i), va="center", fontsize=8, color=TEXT, xytext=(4, 0), textcoords="offset points")
    ax.set_title("Document Type Distribution", fontsize=11, fontweight="bold", loc="left", pad=10)
    ax.set_xlabel("Publications")
    ax.set_ylabel("")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_publisher_bar(df, top_n=10):
    """Seaborn bar chart of the top N publishers/sources by publication count."""
    pdf = df[df["publisher"] != ""]
    counts = pdf["publisher"].value_counts().head(top_n).sort_values(ascending=True)
    if len(counts) == 0:
        st.info("No publisher/source data in the current filter selection.")
        return
    fig, ax = plt.subplots(figsize=(7, max(2.6, 0.42 * len(counts))), dpi=140)
    _style_ax(fig, ax)
    sns.barplot(x=counts.values, y=counts.index, ax=ax, color=ACCENT_2, orient="h")
    for i, v in enumerate(counts.values):
        ax.annotate(str(v), (v, i), va="center", fontsize=8, color=TEXT, xytext=(4, 0), textcoords="offset points")
    ax.set_title(f"Top {min(top_n, len(counts))} Publishers / Sources", fontsize=11, fontweight="bold", loc="left", pad=10)
    ax.set_xlabel("Publications")
    ax.set_ylabel("")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_sdg_frequency_bar(df):
    """Seaborn bar chart: overall SDG-association frequency across the filtered dataset."""
    counts = {}
    for xs in df["sdg_list"]:
        for s in xs:
            counts[s] = counts.get(s, 0) + 1
    if not counts:
        st.info("No SDG-tagged publications in the current filter selection.")
        return
    items = sorted(counts.items())
    labels = [f"SDG {s}" for s, _ in items]
    values = [c for _, c in items]
    fig, ax = plt.subplots(figsize=(9, 3.6), dpi=140)
    _style_ax(fig, ax)
    sns.barplot(x=labels, y=values, ax=ax, color=ACCENT)
    for i, v in enumerate(values):
        ax.annotate(str(v), (i, v), ha="center", va="bottom", fontsize=8, color=TEXT, xytext=(0, 3), textcoords="offset points")
    ax.set_title("SDG Association Frequency (across filtered publications)",
                 fontsize=11, fontweight="bold", loc="left", pad=10)
    ax.set_ylabel("Associations")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_sdg_cooccurrence_heatmap(df):
    """Seaborn heatmap: how often pairs of SDGs are associated with the same publication."""
    import itertools
    all_sdgs = sorted({s for xs in df["sdg_list"] for s in xs})
    if len(all_sdgs) < 2:
        st.info("Not enough distinct SDGs in the current filter selection for a co-occurrence view.")
        return
    idx = {s: i for i, s in enumerate(all_sdgs)}
    mat = np.zeros((len(all_sdgs), len(all_sdgs)), dtype=int)
    for xs in df["sdg_list"]:
        for a, b in itertools.combinations(sorted(set(xs)), 2):
            mat[idx[a], idx[b]] += 1
            mat[idx[b], idx[a]] += 1
        for a in xs:
            mat[idx[a], idx[a]] += 1

    labels = [f"SDG {s}" for s in all_sdgs]
    fig, ax = plt.subplots(figsize=(max(6, 0.55 * len(labels)), max(5, 0.55 * len(labels))), dpi=140)
    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)
    sns.heatmap(mat, ax=ax, xticklabels=labels, yticklabels=labels,
                cmap=sns.light_palette(ACCENT_2, as_cmap=True),
                linewidths=0.5, linecolor=BG, annot=True, fmt="d",
                annot_kws={"fontsize": 7, "color": TEXT}, cbar_kws={"label": "Co-occurrences"})
    ax.tick_params(colors=TEXT, labelsize=8)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_color(TEXT)
    cbar.ax.tick_params(colors=TEXT)
    ax.set_title("SDG Co-occurrence Matrix (diagonal = total associations)",
                 fontsize=10.5, fontweight="bold", loc="left", pad=10, color=TEXT)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_school_year_heatmap(df):
    """Seaborn heatmap of publication counts: schools (rows) x years (columns)."""
    ydf = df.dropna(subset=["year"])
    if len(ydf) == 0:
        st.info("No year data available for a school × year view.")
        return
    matrix = ydf.pivot_table(index="school", columns="year", values="title", aggfunc="count", fill_value=0)
    matrix = matrix.reindex(sorted(matrix.columns), axis=1)
    fig, ax = plt.subplots(figsize=(max(7, 0.7 * len(matrix.columns)), max(3, 0.42 * len(matrix))), dpi=140)
    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)
    sns.heatmap(matrix, ax=ax, cmap=sns.light_palette(ACCENT, as_cmap=True),
                linewidths=0.5, linecolor=BG, annot=True, fmt="g",
                annot_kws={"fontsize": 7.5, "color": TEXT}, cbar_kws={"label": "Publications"})
    ax.tick_params(colors=TEXT, labelsize=8.5)
    ax.set_xlabel("")
    ax.set_ylabel("")
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_color(TEXT)
    cbar.ax.tick_params(colors=TEXT)
    ax.set_title("School × Year Publication Density", fontsize=10.5, fontweight="bold", loc="left", pad=10, color=TEXT)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_researcher_productivity_histogram(df):
    """Seaborn histogram: distribution of publication counts per researcher."""
    counts = {}
    for xs in df["authors_list"]:
        for a in xs:
            counts[a] = counts.get(a, 0) + 1
    if not counts:
        st.info("No researcher data in the current filter selection.")
        return
    values = list(counts.values())
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=140)
    _style_ax(fig, ax)
    max_v = max(values)
    sns.histplot(values, ax=ax, bins=range(1, max_v + 2), color=ACCENT, edgecolor=CARD_BG, discrete=True)
    ax.set_title("Researcher Productivity Distribution (publications per researcher)",
                 fontsize=10.5, fontweight="bold", loc="left", pad=10)
    ax.set_xlabel("Publications by one researcher")
    ax.set_ylabel("Number of researchers")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_bar(categories, values, title, horizontal=True, top_n=None):
    if top_n:
        pairs = sorted(zip(categories, values), key=lambda x: x[1], reverse=True)[:top_n]
        categories, values = zip(*pairs) if pairs else ([], [])
    fig, ax = plt.subplots(figsize=(7, max(2.6, 0.38 * len(categories))), dpi=140)
    _style_ax(fig, ax)
    if horizontal:
        ax.barh(categories, values, color=ACCENT)
        ax.invert_yaxis()
        for i, v in enumerate(values):
            ax.annotate(str(v), (v, i), va="center", fontsize=8, color=TEXT, xytext=(4, 0), textcoords="offset points")
    else:
        ax.bar(categories, values, color=ACCENT)
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left", pad=10)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
