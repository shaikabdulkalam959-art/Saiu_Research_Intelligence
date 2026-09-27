import streamlit as st
from components import charts


def render_school_ecosystem(df):
    st.markdown("#### School Research Ecosystem")
    schools = sorted(df["school"].unique())
    if not schools:
        st.info("No schools present in the current filter selection.")
        return

    grid_cols = st.columns(3)
    for i, school in enumerate(schools):
        sdf = df[df["school"] == school]
        sdgs = {}
        for xs in sdf["sdg_list"]:
            for s in xs:
                sdgs[s] = sdgs.get(s, 0) + 1
        top_sdg = max(sdgs, key=sdgs.get) if sdgs else None
        researchers = {a for xs in sdf["authors_list"] for a in xs}

        with grid_cols[i % 3]:
            st.markdown(
                f"""
                <div class="school-card">
                    <div class="school-name">{school}</div>
                    <div class="school-stat"><b>{len(sdf)}</b> publications</div>
                    <div class="school-stat"><b>{len(researchers)}</b> researchers</div>
                    <div class="school-stat"><b>{int((sdf['quartile']=='Q1').sum())}</b> Q1 papers</div>
                    <div class="school-stat"><b>{int((sdf['is_scopus']|sdf['is_wos']).sum())}</b> indexed</div>
                    <div class="school-stat-muted">Top SDG: {f'SDG {top_sdg}' if top_sdg else '—'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    selected = st.selectbox("Open a school's detailed research profile", ["—"] + schools)
    if selected != "—":
        render_school_profile(df, selected)


def render_school_profile(df, school):
    sdf = df[df["school"] == school]
    st.markdown(f"### {school} — Research Profile")

    total = len(sdf)
    researchers = {a for xs in sdf["authors_list"] for a in xs}
    scopus_share = round(100 * sdf["is_scopus"].sum() / total, 1) if total else 0
    wos_share = round(100 * sdf["is_wos"].sum() / total, 1) if total else 0
    known_q = sdf[sdf["quartile_known"]]
    q1_share = round(100 * (sdf["quartile"] == "Q1").sum() / len(known_q), 1) if len(known_q) else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total publications", total)
    c2.metric("Active researchers", len(researchers))
    c3.metric("Scopus share", f"{scopus_share}%")
    c4.metric("Q1 share (of classified)", f"{q1_share}%" if q1_share is not None else "N/A")

    top_doc = sdf["doc_type"].value_counts()
    top_pub = sdf[sdf["publisher"] != ""]["publisher"].value_counts()
    colA, colB = st.columns(2)
    with colA:
        st.markdown(f"**Top document type:** {top_doc.index[0] if len(top_doc) else '—'}")
        st.markdown(f"**Top publisher/source:** {top_pub.index[0] if len(top_pub) else '—'}")
        st.markdown(f"**WoS share:** {wos_share}%")
    with colB:
        sdgs = {}
        for xs in sdf["sdg_list"]:
            for s in xs:
                sdgs[s] = sdgs.get(s, 0) + 1
        top_sdgs = sorted(sdgs.items(), key=lambda x: x[1], reverse=True)[:5]
        st.markdown("**Most represented SDGs:** " + (
            ", ".join(f"SDG {s} ({c})" for s, c in top_sdgs) if top_sdgs else "—"
        ))

    trend = sdf.dropna(subset=["year"]).groupby("year").size()
    if len(trend):
        charts.render_trend_chart(list(trend.index), list(trend.values),
                                   title=f"{school} — Publication Trend")

    counts = {}
    for xs in sdf["authors_list"]:
        for a in xs:
            counts[a] = counts.get(a, 0) + 1
    top_researchers = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    if top_researchers:
        charts.render_bar([a for a, _ in top_researchers], [c for _, c in top_researchers],
                           "Top Researchers by Publication Count")
