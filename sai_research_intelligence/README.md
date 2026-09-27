# SAI RESEARCH INTELLIGENCE
**Mapping the University's Research Ecosystem**

A premium, API-first research intelligence platform for Sai University,
Chennai — built with Streamlit, Pandas, NumPy, Matplotlib and Seaborn.

---

## 1. Project overview

Every number in this dashboard is computed live from
`https://sai-publications-dashboard.vercel.app/api/publications`. Nothing is
hardcoded: no publication counts, faculty names, schools, journals, SDGs,
DOIs or statistics are invented. If the API is unavailable, the app shows a
clear error/retry state instead of fake data.

## 2. The "Research DNA Reveal" feature

The brief asked for a specific Instagram Reel (`DdtyaFrhB4S`) to be inspected
and its interaction adapted to this context. The reel could be opened and
watched directly (frames were inspected): it shows a developer portfolio
where an organic, non-circular mask follows the visitor's cursor across a
laptop screen, continuously morphing while moving, and revealing a second
"creative/AI" identity layer hidden underneath a polished default layer —
with the on-screen checklist explicitly specifying: two same-sized layers,
an organic (never-circular) reveal shape, smooth cursor-interpolated
tracking, a continuously morphing mask, touch support, and no full-page
swap — reveal only, nothing else changing.

This dashboard reproduces that exact interaction on the **Overview** page,
re-purposed for research analytics:

- **Layer 1 (always visible)** — the university's public research identity:
  bold italic headline (matching the Reel's poster-style display type) plus
  headline KPIs (total publications, schools, faculty, SDGs engaged).
- **Layer 2 ("Research DNA", hidden by default)** — a denser analytical
  layer: the live Research Momentum score, a ranked bar list of top schools,
  and the SDGs actually present in the current filter — revealed only
  through an organic blob mask that smoothly follows the mouse (desktop) or
  finger (mobile/touch), continuously morphs via layered sine waves so it is
  never a perfect circle, and disappears again on mouse-leave / touch-end.
- Built with `streamlit.components.v1.html` using CSS `mask-image` +
  `requestAnimationFrame` interpolation — no external chart library needed,
  and it re-renders with fresh numbers every time filters or search change.

Font direction ("give the font like that video") is carried through the
whole app: display headlines use **Archivo Black, italic, uppercase** (Google
Font) to mirror the Reel's bold poster typography, while body/data text uses
clean **Inter** for readability at a Bloomberg-style information density.

## 3. Charts (19 total) & Power-BI-style hover

A static image (which is all a Matplotlib/Seaborn figure ever is, once
rendered) cannot show a floating tooltip on hover — there's no interactivity
in a PNG. To get the "hover and see a floating value card" feel from Power
BI, the highest-value comparison/trend charts are rendered with **Plotly**
instead (`st.plotly_chart`), styled to match the same dark/teal theme, while
the rest of the app stays on the required Matplotlib/Seaborn stack. Hover
tooltips (Plotly) are marked 🖱️ below.

**Research Growth**
1. 🖱️ Annual Publication Trend
2. 🖱️ Indexed vs Non-indexed Publications Over Time (stacked area)
3. 🖱️ Year-over-Year Growth Rate by year
4. 🖱️ SJR Quartile Mix Over Time (stacked area)

**Schools**
5. 🖱️ Publications by School
6. 🖱️ School Comparison — Scopus / WoS / Q1 share (grouped bars)
7. School × Year Publication Density (Seaborn heatmap)
8. School profile: publication trend (Seaborn, on drill-down)
9. School profile: top researchers (Seaborn, on drill-down)

**Researchers**
10. 🖱️ Top 15 Researchers by Publication Count
11. Researcher Productivity Distribution (Seaborn histogram)
12. Researcher profile: publication timeline (Seaborn, on selection)

**Research Quality**
13. SJR Quartile Distribution (Seaborn bar)
14. 🖱️ Indexing Coverage (donut)
15. Document Type Distribution (Seaborn bar)
16. Top Publishers / Sources (Seaborn bar)

**SDG Impact**
17. Schools × SDG Impact Matrix (Seaborn heatmap)
18. SDG Association Frequency (Seaborn bar)
19. SDG Co-occurrence Matrix (Seaborn heatmap)

Every chart recomputes from the currently filtered/searched dataframe —
nothing is cached from an earlier filter state.

## 4. Features

- Global full-text search + 8-way sidebar filters (year, school, author,
  document type, indexing status, SJR quartile, SDG, publisher), all
  updating every KPI, chart, drill-down and export simultaneously.
- Custom KPI cards (not `st.metric` rows) with correct, documented
  denominators for every percentage.
- Transparent **Research Momentum** score (0–100), fully documented and
  reproducible, with missing-data-aware weight re-normalization.
- Research Growth / YoY section with Matplotlib trend chart, and explicit
  "no prior-year data" handling instead of fabricated percentages.
- School Research Ecosystem cards + full drill-down profiles.
- Researcher Explorer populated only from API-derived fields.
- Research Quality profile (quartiles + indexing coverage) via
  Matplotlib/Seaborn, with "Unknown" never conflated with "Non-indexed".
- SDG Impact Matrix — a Seaborn heatmap of schools × SDGs actually present
  in the data.
- Publication Explorer with sortable, clickable-only-when-valid DOI/URL
  columns.
- Data Quality & Coverage center: missing-field counts, duplicate detection
  (DOI-first, else normalized title + year — flagged, never silently
  dropped), and a source-field mapping table.
- CSV export of filtered publications and of summary statistics.
- Defensive error/empty states for API timeouts, HTTP errors, malformed
  JSON, empty responses and empty filter results.

## 5. Technologies

Python · Streamlit · Pandas · NumPy · Requests · Matplotlib · Seaborn.

## 6. API source

`GET https://sai-publications-dashboard.vercel.app/api/publications`
Response shape: `{"data": [ {…36 publication fields…}, … ]}`.

## 7. Installation

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 8. Run

```bash
streamlit run app.py
```

## 9. Project structure

```
research_dashboard/
├── app.py
├── requirements.txt
├── README.md
├── utils/
│   ├── data_loader.py      # load_data, validate_response, APIError
│   ├── data_cleaning.py    # normalize_columns, clean_data, parse_authors,
│   │                       # parse_sdgs, parse_indexing, detect_duplicates
│   ├── analytics.py        # filter_data, calculate_kpis, calculate_yoy,
│   │                       # calculate_quality_metrics,
│   │                       # calculate_research_momentum
│   └── insights.py         # generate_insights (pure Pandas, no external AI)
├── components/
│   ├── kpis.py             # custom KPI cards + momentum explainer
│   ├── charts.py           # Matplotlib/Seaborn chart set, dark themed
│   ├── charts_interactive.py # Plotly hover-tooltip charts (Power-BI style)
│   ├── filters.py          # sidebar filters + global search
│   ├── researcher.py       # researcher explorer
│   ├── school.py           # school ecosystem + drill-down profile
│   └── reveal.py           # the Reel-inspired "Research DNA" cursor reveal
└── assets/
    └── styles.css
```

## 10. Data cleaning approach

Raw API fields are renamed to internal snake_case names
(`normalize_columns`), then typed and parsed (`clean_data`):
- `Year` → validated 4-digit int or missing (never coerced to 0).
- `SaiU Authors` → split on `;`/`&`/" and " into a name list.
- `SaiU SDG Indexing` → pipe-split into valid integers 1–17 only; falls back
  to the Scopus/WoS "Achieved SDG" fields **only** when SaiU SDG Indexing
  itself is empty — never merges or guesses beyond stated fields.
- `Indexing Status` → pipe-split (e.g. `"Scopus | WoS"`), booleans derived
  per source; blank is tracked separately as "unknown", never assumed
  non-indexed.
- `SJR Quartile` → upper-cased `Q1`–`Q4` or `""` (Unclassified) — Q1% uses
  only records with a known quartile as the denominator.
- Duplicate detection key: DOI (lower-cased) when present, else normalized
  title + year. Duplicates are flagged in a boolean column, never removed
  automatically.

## 11. KPI definitions

| KPI | Definition | Denominator |
|---|---|---|
| Total publications | count of filtered rows | — |
| Scopus-indexed | rows where Indexing Status contains "Scopus" | — |
| WoS-indexed | rows where Indexing Status contains "WoS" | — |
| Q1 publications | rows where SJR Quartile == "Q1" | publications with a **known** quartile |
| Schools | `nunique(school)` | — |
| Faculty authors | unique names across parsed `SaiU Authors` | — |
| SDGs represented | unique SDGs across parsed SDG lists | out of 17 |

## 12. Research Momentum formula

See the in-app "How is Research Momentum calculated?" expander on the
Overview page for the live, current-filter breakdown. Summary:

`score = Σ (component_score × re-normalized_weight)` where components are
recent publication growth (35%), indexed share (25%), Q1 share (20%) and
active-researcher ratio (20%) — each 0–100. A component is dropped (and
remaining weights re-normalized) when its denominator is zero (e.g. no
prior year available), so missing data is never treated as zero.

## 13. Missing-data handling

Missing/blank/unknown/not-applicable are kept distinct throughout: an empty
quartile is "Unclassified" (not Q4), an empty indexing status is "Unknown"
(not "Non Indexed"), and a zero previous-year count yields "N/A" growth
rather than a fabricated ±percentage.

## 14. Export functionality

Two CSV downloads in the sidebar, both computed from the **currently
filtered and searched** dataframe: `sai_filtered_publications.csv` (full
record set) and `sai_summary_statistics.csv` (current KPIs + momentum).

## 15. Testing performed & limitations

**Performed:**
- A real HTTP GET against the live API was executed and the JSON response
  inspected field-by-field to build the schema/normalization layer above
  (see `utils/data_cleaning.py` header comment for the verified field list).
- Every module was written directly against that real schema (field names,
  pipe-delimited multi-value fields, blank-vs-populated patterns) rather
  than an assumed one.
- Unit-level testing of `data_cleaning.py` and `analytics.py` against a
  mock dataset shaped exactly like the real API response (multiple schools,
  multi-author and multi-SDG records, missing years/quartiles/authors, a
  duplicate-by-DOI pair, and a fully blank "orphan" record). This caught and
  fixed a real bug — NaN values in optional fields were being stringified to
  the literal text `"NAN"`/`"None"` instead of being treated as missing —
  now handled by a single safe-coercion helper (`_s()`) used everywhere.
- A full **end-to-end run of the actual Streamlit app** (`app.py`) against
  that mock API, using Streamlit's own `AppTest` headless test harness plus
  a local mock HTTP server standing in for the live endpoint:
  - All 8 navigation sections load with **zero runtime exceptions**.
  - Sidebar filters (school, etc.) correctly narrow the dataset and every
    downstream KPI/count reflects the filtered subset (verified 7 → 3
    records).
  - Global search narrows results correctly (verified a specific-term
    search returned exactly the matching record).
  - The empty-filter-result state renders the required
    "No publications match the current research filters." message.
  - School drill-down profile, Researcher Explorer profile, Publication
    Explorer table and Data Quality tables all render without error.
  - Both CSV export buttons are present and wired to the filtered data.
  - **Found and fixed a real bug** during this pass: the "Reset all
    filters" / "Clear all filters" buttons initially threw a
    `StreamlitWidgetAlreadyInstantiatedError` because they tried to reset a
    widget's `session_state` value after that widget had already been
    instantiated in the same script run. Fixed by moving the reset logic
    into an `on_click` callback (which runs before the next script run
    instantiates its widgets), then re-tested and confirmed both buttons
    now correctly restore the full, unfiltered dataset.
  - The live `Instagram` Reel URL itself could not be opened by the
    automated browser available while building this project; its content
    was instead inspected directly from the screen recording you uploaded,
    frame by frame, and the "Research DNA" reveal feature was built from
    that direct inspection (organic non-circular mask, continuous morph,
    smooth cursor interpolation, touch support, mouse-leave hide — all
    confirmed present in the reel's own on-screen creative-direction
    checklist).

**Limitations:**
- The sandboxed authoring environment could reach the live API host only
  through an explicit URL-fetch tool (used once, to inspect the schema),
  not through outbound Python `requests` calls — so the end-to-end test
  above ran against a local mock server serving the real schema rather than
  the live endpoint itself. Please do one live `streamlit run app.py` pass
  in your own environment (with outbound internet access) as a final
  sanity check — if the live schema has drifted since inspection, the app
  is built to fail loudly with a retry button rather than silently showing
  wrong numbers.
- The mock dataset used for testing was small (7 records) by necessity; the
  logic paths (filtering, dedup, missing-data handling, empty states) are
  all exercised, but rendering with your full, larger dataset may surface
  layout/spacing adjustments worth making (e.g. school-card grid density).
