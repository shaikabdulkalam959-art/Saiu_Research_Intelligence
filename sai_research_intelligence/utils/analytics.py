"""
analytics.py
All KPI, growth, quality and Research Momentum calculations.
Every function operates on the already-filtered dataframe so every view
in the app reflects the same active filter/search state.
"""

import pandas as pd
import numpy as np


def filter_data(df: pd.DataFrame, filters: dict, search_query: str = "") -> pd.DataFrame:
    """Apply sidebar filters + global search to the cleaned dataframe."""
    out = df

    if filters.get("years"):
        out = out[out["year"].isin(filters["years"])]
    if filters.get("schools"):
        out = out[out["school"].isin(filters["schools"])]
    if filters.get("authors"):
        chosen = set(filters["authors"])
        out = out[out["authors_list"].apply(lambda xs: bool(chosen.intersection(xs)))]
    if filters.get("doc_types"):
        out = out[out["doc_type"].isin(filters["doc_types"])]
    if filters.get("indexing"):
        chosen = set(filters["indexing"])
        def _match_idx(xs):
            if "Unknown" in chosen and len(xs) == 0:
                return True
            return bool(chosen.intersection(xs))
        out = out[out["indexing_list"].apply(_match_idx)]
    if filters.get("quartiles"):
        chosen = set(filters["quartiles"])
        def _match_q(row_q):
            if "Unclassified" in chosen and row_q == "":
                return True
            return row_q in chosen
        out = out[out["quartile"].apply(_match_q)]
    if filters.get("sdgs"):
        chosen = set(filters["sdgs"])
        out = out[out["sdg_list"].apply(lambda xs: bool(chosen.intersection(set(xs))))]
    if filters.get("publishers"):
        out = out[out["publisher"].isin(filters["publishers"])]

    if search_query and search_query.strip():
        q = search_query.strip().lower()
        out = out[out["search_blob"].str.contains(q, na=False, regex=False)]

    return out


def calculate_kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    scopus = int(df["is_scopus"].sum())
    wos = int(df["is_wos"].sum())
    known_q = df[df["quartile_known"]]
    q1 = int((df["quartile"] == "Q1").sum())
    q1_denom = len(known_q)
    q1_pct = round(100 * q1 / q1_denom, 1) if q1_denom else None

    known_idx = df[df["indexing_known"]]
    idx_denom = len(known_idx)
    scopus_pct = round(100 * scopus / idx_denom, 1) if idx_denom else None

    schools = df["school"].nunique()
    authors = set()
    for xs in df["authors_list"]:
        authors.update(xs)
    faculty_count = len(authors)

    sdgs = set()
    for xs in df["sdg_list"]:
        sdgs.update(xs)
    sdg_count = len(sdgs)

    return {
        "total_publications": total,
        "scopus_count": scopus,
        "scopus_pct_of_known": scopus_pct,
        "wos_count": wos,
        "q1_count": q1,
        "q1_pct_of_known": q1_pct,
        "q1_denominator": q1_denom,
        "indexing_denominator": idx_denom,
        "school_count": schools,
        "faculty_count": faculty_count,
        "sdg_count": sdg_count,
    }


def calculate_yoy(df: pd.DataFrame) -> dict:
    """Year-over-year publication, indexed and Q1 growth. Never fabricates
    a percentage when the previous year's count is zero/unavailable."""
    years = sorted([int(y) for y in df["year"].dropna().unique()])
    if not years:
        return {"available": False}

    current_year = years[-1]
    previous_year = current_year - 1

    cur = df[df["year"] == current_year]
    prev = df[df["year"] == previous_year] if previous_year in years else pd.DataFrame(columns=df.columns)

    def _pct_change(cur_n, prev_n):
        if previous_year not in years or prev_n == 0:
            return None
        return round(100 * (cur_n - prev_n) / prev_n, 1)

    cur_total, prev_total = len(cur), len(prev)
    cur_idx = int((cur["is_scopus"] | cur["is_wos"]).sum()) if len(cur) else 0
    prev_idx = int((prev["is_scopus"] | prev["is_wos"]).sum()) if len(prev) else 0
    cur_q1, prev_q1 = int((cur["quartile"] == "Q1").sum()), int((prev["quartile"] == "Q1").sum())

    trend = df.groupby("year").size().reindex(years, fill_value=0)

    return {
        "available": True,
        "current_year": current_year,
        "previous_year": previous_year,
        "previous_year_available": previous_year in years,
        "current_total": cur_total,
        "previous_total": prev_total,
        "publication_growth_pct": _pct_change(cur_total, prev_total),
        "indexed_growth_pct": _pct_change(cur_idx, prev_idx),
        "q1_growth_pct": _pct_change(cur_q1, prev_q1),
        "trend_years": list(trend.index),
        "trend_counts": list(trend.values),
    }


def calculate_quality_metrics(df: pd.DataFrame) -> dict:
    total = len(df)
    quartile_counts = {
        "Q1": int((df["quartile"] == "Q1").sum()),
        "Q2": int((df["quartile"] == "Q2").sum()),
        "Q3": int((df["quartile"] == "Q3").sum()),
        "Q4": int((df["quartile"] == "Q4").sum()),
        "Unclassified": int((df["quartile"] == "").sum()),
    }
    indexing_counts = {
        "Indexed": int((df["is_scopus"] | df["is_wos"]).sum()),
        "Non-indexed": int(df["is_non_indexed"].sum()),
    }
    indexing_counts["Unknown"] = total - indexing_counts["Indexed"] - indexing_counts["Non-indexed"]
    return {
        "total": total,
        "quartile_counts": quartile_counts,
        "indexing_counts": indexing_counts,
    }


def _normalize(value, lo, hi):
    if hi <= lo:
        return 0.0
    return float(np.clip((value - lo) / (hi - lo) * 100, 0, 100))


def calculate_research_momentum(df: pd.DataFrame) -> dict:
    """
    Transparent, documented, reproducible 0-100 dashboard-derived indicator.
    Components (each normalized to 0-100, then weighted):
      1. Recent growth   (35%) - most-recent-year vs prior-year pub count,
                                 pct change clipped to [-50%, +100%] -> 0-100
      2. Indexed share   (25%) - % of known-indexing pubs that are indexed
      3. Q1 share        (20%) - % of known-quartile pubs that are Q1
      4. Active research (20%) - unique authors publishing in the most
         base                    recent year vs. total unique authors overall
    Missing-data treatment: a component with no computable denominator is
    excluded and the remaining weights are re-normalized proportionally.
    """
    weights = {"growth": 0.35, "indexed": 0.25, "q1": 0.20, "active": 0.20}
    scores = {}

    yoy = calculate_yoy(df)
    if yoy["available"] and yoy["publication_growth_pct"] is not None:
        scores["growth"] = _normalize(yoy["publication_growth_pct"], -50, 100)

    quality = calculate_quality_metrics(df)
    idx_known = quality["indexing_counts"]["Indexed"] + quality["indexing_counts"]["Non-indexed"]
    if idx_known:
        scores["indexed"] = 100 * quality["indexing_counts"]["Indexed"] / idx_known

    q_known = sum(quality["quartile_counts"][q] for q in ["Q1", "Q2", "Q3", "Q4"])
    if q_known:
        scores["q1"] = 100 * quality["quartile_counts"]["Q1"] / q_known

    if yoy["available"]:
        all_authors = set()
        for xs in df["authors_list"]:
            all_authors.update(xs)
        recent = df[df["year"] == yoy["current_year"]]
        recent_authors = set()
        for xs in recent["authors_list"]:
            recent_authors.update(xs)
        if all_authors:
            scores["active"] = 100 * len(recent_authors) / len(all_authors)

    if not scores:
        return {"score": None, "components": {}, "weights_used": {}}

    used_weights = {k: weights[k] for k in scores}
    total_w = sum(used_weights.values())
    normalized_weights = {k: v / total_w for k, v in used_weights.items()}
    final_score = sum(scores[k] * normalized_weights[k] for k in scores)

    return {
        "score": round(final_score, 1),
        "components": {k: round(v, 1) for k, v in scores.items()},
        "weights_used": {k: round(v, 2) for k, v in normalized_weights.items()},
    }
