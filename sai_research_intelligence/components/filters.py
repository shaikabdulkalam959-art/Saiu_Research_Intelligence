import streamlit as st


DEFAULTS = {
    "f_years": [], "f_schools": [], "f_authors": [], "f_doctypes": [],
    "f_indexing": [], "f_quartiles": [], "f_sdgs": [], "f_publishers": [],
    "search_query": "",
}


def _init_state():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_global_search():
    _init_state()
    st.text_input(
        "🔎 Search research, researchers, schools or SDGs...",
        key="search_query",
        placeholder="e.g. \"machine learning\", \"School of Law\", \"SDG 3\", an author name...",
        label_visibility="collapsed",
    )


def render_sidebar_filters(df):
    _init_state()
    def _reset_all():
        # Runs as an on_click callback, i.e. BEFORE this run's widgets are
        # (re)instantiated, so writing to their session_state keys is safe.
        for k, v in DEFAULTS.items():
            st.session_state[k] = v

    with st.sidebar:
        st.markdown("### Filters")
        st.button("Reset all filters", use_container_width=True, on_click=_reset_all)

        years = sorted([int(y) for y in df["year"].dropna().unique()], reverse=True)
        st.multiselect("Publication year", years, key="f_years")

        schools = sorted(df["school"].dropna().unique())
        st.multiselect("School", schools, key="f_schools")

        all_authors = sorted({a for xs in df["authors_list"] for a in xs})
        st.multiselect("Author", all_authors, key="f_authors")

        doc_types = sorted(df["doc_type"].dropna().unique())
        st.multiselect("Document type", doc_types, key="f_doctypes")

        st.multiselect("Indexing status", ["Scopus", "WoS", "Non Indexed", "Unknown"], key="f_indexing")

        st.multiselect("SJR quartile", ["Q1", "Q2", "Q3", "Q4", "Unclassified"], key="f_quartiles")

        all_sdgs = sorted({s for xs in df["sdg_list"] for s in xs})
        st.multiselect("SDG", all_sdgs, key="f_sdgs", format_func=lambda x: f"SDG {x}")

        publishers = sorted([p for p in df["publisher"].dropna().unique() if p])
        st.multiselect("Publisher / source", publishers, key="f_publishers")

    return {
        "years": st.session_state["f_years"],
        "schools": st.session_state["f_schools"],
        "authors": st.session_state["f_authors"],
        "doc_types": st.session_state["f_doctypes"],
        "indexing": st.session_state["f_indexing"],
        "quartiles": st.session_state["f_quartiles"],
        "sdgs": st.session_state["f_sdgs"],
        "publishers": st.session_state["f_publishers"],
    }
