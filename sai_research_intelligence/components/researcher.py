import streamlit as st
from components import charts


def render_researcher_explorer(df):
    st.markdown("#### Researcher Explorer")
    all_authors = sorted({a for xs in df["authors_list"] for a in xs})
    if not all_authors:
        st.info("No researchers present in the current filter selection.")
        return

    selected = st.selectbox("Select a researcher", ["—"] + all_authors)
    if selected == "—":
        st.caption(f"{len(all_authors)} researchers match the current filters. Select one to view their profile.")
        return

    rdf = df[df["authors_list"].apply(lambda xs: selected in xs)]
    total = len(rdf)
    years = sorted([int(y) for y in rdf["year"].dropna().unique()])
    schools = sorted(rdf["school"].unique())
    indexed = int((rdf["is_scopus"] | rdf["is_wos"]).sum())
    q1 = int((rdf["quartile"] == "Q1").sum())
    sdgs = sorted({s for xs in rdf["sdg_list"] for s in xs})
    main_doc = rdf["doc_type"].value_counts()
    main_pub = rdf[rdf["publisher"] != ""]["publisher"].value_counts()

    st.markdown(f"### {selected}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total publications", total)
    c2.metric("Indexed publications", indexed)
    c3.metric("Q1 publications", q1)
    c4.metric("SDGs represented", len(sdgs))

    st.markdown(f"**Schools:** {', '.join(schools) if schools else '—'}")
    st.markdown(f"**Active years:** {', '.join(map(str, years)) if years else '—'}")
    st.markdown(f"**Main document type:** {main_doc.index[0] if len(main_doc) else '—'}")
    st.markdown(f"**Main publisher/source:** {main_pub.index[0] if len(main_pub) else '—'}")

    trend = rdf.dropna(subset=["year"]).groupby("year").size()
    if len(trend):
        charts.render_trend_chart(list(trend.index), list(trend.values),
                                   title=f"{selected} — Publication Timeline")

    st.markdown("**Publications**")
    show_cols = {
        "title": "Title", "year": "Year", "school": "School",
        "source_title": "Source", "quartile": "Quartile",
        "indexing_status": "Indexing", "doi_link": "DOI Link",
    }
    display = rdf[list(show_cols.keys())].rename(columns=show_cols).sort_values("Year", ascending=False)
    st.dataframe(
        display,
        column_config={"DOI Link": st.column_config.LinkColumn("DOI Link")},
        use_container_width=True, hide_index=True,
    )
