import streamlit as st


def _card(label, value, desc, accent=False):
    accent_class = "kpi-card kpi-accent" if accent else "kpi-card"
    st.markdown(
        f"""
        <div class="{accent_class}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_grid(kpis: dict, momentum: dict):
    cols = st.columns(4)
    with cols[0]:
        _card("TOTAL PUBLICATIONS", f"{kpis['total_publications']:,}",
              "All records in current filter")
    with cols[1]:
        val = f"{kpis['scopus_count']:,}"
        desc = (f"{kpis['scopus_pct_of_known']}% of {kpis['indexing_denominator']} classified"
                if kpis["indexing_denominator"] else "No indexing data available")
        _card("SCOPUS-INDEXED", val, desc)
    with cols[2]:
        _card("WEB OF SCIENCE", f"{kpis['wos_count']:,}", "WoS-indexed publications")
    with cols[3]:
        val = f"{kpis['q1_count']:,}"
        desc = (f"{kpis['q1_pct_of_known']}% of {kpis['q1_denominator']} classified"
                if kpis["q1_denominator"] else "No quartile data available")
        _card("Q1 PUBLICATIONS", val, desc)

    cols2 = st.columns(4)
    with cols2[0]:
        _card("SCHOOLS", f"{kpis['school_count']}", "Unique schools represented")
    with cols2[1]:
        _card("FACULTY AUTHORS", f"{kpis['faculty_count']}", "Unique SaiU authors")
    with cols2[2]:
        _card("SDGs REPRESENTED", f"{kpis['sdg_count']} / 17", "Distinct SDGs found in data")
    with cols2[3]:
        score = f"{momentum['score']}/100" if momentum["score"] is not None else "N/A"
        desc = "Insufficient data to compute" if momentum["score"] is None else "Dashboard-derived indicator"
        _card("RESEARCH MOMENTUM", score, desc, accent=True)


def render_momentum_explainer(momentum: dict):
    with st.expander("How is Research Momentum calculated?"):
        st.markdown(
            "**Research Momentum** is a dashboard-derived indicator (not an "
            "official university metric), scored **0–100**, built from up to "
            "four components — each normalized to a 0–100 scale:\n\n"
            "- **Recent growth (35%)** — most-recent-year vs prior-year publication count\n"
            "- **Indexed share (25%)** — % of known-indexing publications that are Scopus/WoS indexed\n"
            "- **Q1 share (20%)** — % of known-quartile publications ranked Q1\n"
            "- **Active researchers (20%)** — unique authors publishing in the most recent year, "
            "relative to all-time unique authors\n\n"
            "If a component has no computable denominator (e.g. no prior year to compare against), "
            "it is dropped and the remaining weights are re-normalized proportionally, so the score "
            "never silently assumes missing data is zero."
        )
        if momentum["components"]:
            st.markdown("**Current component scores:**")
            for k, v in momentum["components"].items():
                w = momentum["weights_used"].get(k, 0)
                st.markdown(f"- `{k}`: {v}/100  (effective weight: {w})")
        else:
            st.markdown("_No components could be computed for the current filter selection._")
