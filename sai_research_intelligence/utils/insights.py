"""
insights.py
Generates the dynamic Research Intelligence Summary using transparent,
reproducible Pandas/statistical logic only. Never calls an external AI API.
"""

from utils.analytics import calculate_yoy, calculate_kpis, calculate_quality_metrics


def generate_insights(df) -> list:
    """Return a list of plain-language sentences describing the current
    (filtered) dataset. Every number traces back to a Pandas calculation."""
    sentences = []
    if len(df) == 0:
        return ["No publications match the current research filters."]

    yoy = calculate_yoy(df)
    if yoy["available"] and yoy["previous_year_available"]:
        if yoy["publication_growth_pct"] is not None:
            direction = "increased" if yoy["publication_growth_pct"] >= 0 else "decreased"
            sentences.append(
                f"Publication output {direction} by {abs(yoy['publication_growth_pct'])}% "
                f"in {yoy['current_year']} compared with {yoy['previous_year']} "
                f"({yoy['current_total']} vs {yoy['previous_total']} publications)."
            )
    elif yoy["available"]:
        sentences.append(
            f"{yoy['current_total']} publications recorded in {yoy['current_year']}; "
            f"no {yoy['current_year']-1} data is available for a year-over-year comparison."
        )

    school_counts = df["school"].value_counts()
    if len(school_counts):
        top_school = school_counts.index[0]
        top_count = int(school_counts.iloc[0])
        share = round(100 * top_count / len(df), 1)
        sentences.append(
            f"{top_school} contributed the largest publication share at {share}% "
            f"({top_count} of {len(df)} filtered publications)."
        )

    kpis = calculate_kpis(df)
    if kpis["indexing_denominator"]:
        sentences.append(
            f"{kpis['scopus_pct_of_known']}% of publications with known indexing status "
            f"are indexed in Scopus ({kpis['scopus_count']} of {kpis['indexing_denominator']} classified records)."
        )
    else:
        sentences.append("Indexing status is unavailable for the currently filtered publications.")

    if kpis["q1_denominator"]:
        sentences.append(
            f"Among publications with a known SJR quartile, {kpis['q1_pct_of_known']}% "
            f"are Q1-ranked ({kpis['q1_count']} of {kpis['q1_denominator']})."
        )

    return sentences
