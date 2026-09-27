"""
data_cleaning.py
Normalization layer built from the ACTUAL schema returned by
https://sai-publications-dashboard.vercel.app/api/publications

Observed raw fields (verified via live inspection of the API):
Authors, SaiU Authors, School, SaiU Author Email, Designation, Title, Year,
Publication Date, Source title, Volume, Issue, Page start, Page end,
SJR Quartile, Year Wise Quartile, DOI, DOI Link, Article Link, Journal Link,
Abstract, Keywords, Editors, Publisher, Conference name, ISSN, eISSN, ISBN,
Document Type, Indexing Status, Achieved SDG (WoS), Achieved SDG (Scopus),
SaiU SDG Indexing, Scopus URL, WoS URL, Faculty Profile Photo

Multi-value fields observed in the wild:
- "Indexing Status": "Scopus", "Non Indexed", "Scopus | WoS"  -> pipe-delimited
- "SaiU SDG Indexing": "14|6|9"                                -> pipe-delimited
- "SaiU Authors": semicolon-delimited when more than one SaiU author is listed
"""

import re
import numpy as np
import pandas as pd

# raw API field -> internal snake_case field
COLUMN_MAP = {
    "Authors": "raw_authors",
    "SaiU Authors": "authors_raw",
    "School": "school",
    "SaiU Author Email": "author_email",
    "Designation": "designation",
    "Title": "title",
    "Year": "year_raw",
    "Publication Date": "pub_date",
    "Source title": "source_title",
    "Volume": "volume",
    "Issue": "issue",
    "Page start": "page_start",
    "Page end": "page_end",
    "SJR Quartile": "sjr_quartile",
    "Year Wise Quartile": "year_quartile",
    "DOI": "doi",
    "DOI Link": "doi_link",
    "Article Link": "article_link",
    "Journal Link": "journal_link",
    "Abstract": "abstract",
    "Keywords": "keywords",
    "Editors": "editors",
    "Publisher": "publisher",
    "Conference name": "conference",
    "ISSN": "issn",
    "eISSN": "eissn",
    "ISBN": "isbn",
    "Document Type": "doc_type",
    "Indexing Status": "indexing_status",
    "Achieved SDG (WoS)": "sdg_wos_raw",
    "Achieved SDG (Scopus)": "sdg_scopus_raw",
    "SaiU SDG Indexing": "sdg_raw",
    "Scopus URL": "scopus_url",
    "WoS URL": "wos_url",
    "Faculty Profile Photo": "photo",
}

VALID_SDGS = set(range(1, 18))


def _s(val) -> str:
    """Safely coerce any raw API value (incl. NaN/None) to a clean string."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    s = str(val).strip()
    if s.lower() in ("nan", "none", "n/a", "na", "null"):
        return ""
    return s


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename raw API columns to internal names. Missing columns are added
    as empty so downstream code never KeyErrors on a schema drift."""
    df = df.rename(columns=COLUMN_MAP)
    for internal_name in COLUMN_MAP.values():
        if internal_name not in df.columns:
            df[internal_name] = ""
    return df


def _to_year(val):
    """Coerce a year value to an int, or pd.NA if missing/invalid."""
    s = _s(val)
    if s == "":
        return pd.NA
    m = re.search(r"(19|20)\d{2}", s)
    if not m:
        return pd.NA
    year = int(m.group(0))
    if 1990 <= year <= 2035:
        return year
    return pd.NA


def parse_authors(raw: str) -> list:
    """Split a SaiU Authors string into a clean list of individual names."""
    s = _s(raw)
    if s == "":
        return []
    parts = re.split(r";|&|\band\b", s)
    names = [p.strip(" ,") for p in parts if p.strip(" ,")]
    return names


def parse_sdgs(raw: str) -> list:
    """Split a pipe-delimited SDG string into a sorted list of valid SDG ints
    (1-17 only). Never invents an SDG that isn't present in the source field."""
    s = _s(raw)
    if s == "":
        return []
    out = []
    for token in s.split("|"):
        token = token.strip()
        if token.isdigit():
            n = int(token)
            if n in VALID_SDGS:
                out.append(n)
    return sorted(set(out))


def parse_indexing(raw: str) -> list:
    """Split a pipe-delimited Indexing Status string, e.g. 'Scopus | WoS'."""
    s = _s(raw)
    if s == "":
        return []
    return [p.strip() for p in s.split("|") if p.strip()]


def _norm_title(title: str) -> str:
    s = _s(title).lower()
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the analysis-ready dataframe: typed year, parsed author/SDG/
    indexing lists, and standardized quartile / missing-value markers.
    Distinguishes '' (missing) from real categorical values — never fills
    missing data with assumed defaults.
    """
    df = df.copy()

    df["year"] = df["year_raw"].apply(_to_year)

    df["authors_list"] = df["authors_raw"].apply(parse_authors)
    df["author_count"] = df["authors_list"].apply(len)

    df["sdg_list"] = df["sdg_raw"].apply(parse_sdgs)
    # Fall back to Scopus/WoS achieved-SDG fields only when SaiU SDG Indexing
    # itself is empty, so we don't silently drop real signal — but we never
    # merge/guess beyond what the API already states.
    def _fallback_sdg(row):
        if row["sdg_list"]:
            return row["sdg_list"]
        combined = f'{row.get("sdg_scopus_raw","")}|{row.get("sdg_wos_raw","")}'
        return parse_sdgs(combined)
    df["sdg_list"] = df.apply(_fallback_sdg, axis=1)
    df["sdg_count"] = df["sdg_list"].apply(len)

    df["indexing_list"] = df["indexing_status"].apply(parse_indexing)
    df["is_scopus"] = df["indexing_list"].apply(lambda xs: any("scopus" in x.lower() for x in xs))
    df["is_wos"] = df["indexing_list"].apply(lambda xs: any("wos" in x.lower() or "web of science" in x.lower() for x in xs))
    df["indexing_known"] = df["indexing_status"].apply(lambda s: _s(s) != "")
    df["is_non_indexed"] = df["indexing_status"].apply(lambda s: _s(s).lower() == "non indexed")

    df["quartile"] = df["sjr_quartile"].apply(lambda s: _s(s).upper())
    df["quartile_known"] = df["quartile"].apply(lambda q: q in {"Q1", "Q2", "Q3", "Q4"})

    df["school"] = df["school"].apply(lambda s: _s(s) or "Unknown School")
    df["doc_type"] = df["doc_type"].apply(lambda s: _s(s) or "Unspecified")
    df["publisher"] = df["publisher"].apply(_s)
    df["title"] = df["title"].apply(lambda s: _s(s) or "Untitled")

    df["doi_clean"] = df["doi"].apply(lambda s: _s(s).lower())
    df["norm_title"] = df["title"].apply(_norm_title)

    def _dedupe_key(row):
        if row["doi_clean"]:
            return f"doi::{row['doi_clean']}"
        y = row["year"] if pd.notna(row["year"]) else "unknown-year"
        return f"title::{row['norm_title']}::{y}"
    df["dedupe_key"] = df.apply(_dedupe_key, axis=1)

    # searchable text blob for global search
    df["search_blob"] = (
        df["title"].astype(str) + " " +
        df["authors_raw"].astype(str) + " " +
        df["school"].astype(str) + " " +
        df["source_title"].astype(str) + " " +
        df["publisher"].astype(str) + " " +
        df["sdg_raw"].astype(str)
    ).str.lower()

    return df


def detect_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Flag (not remove) duplicate records. Prefers DOI as the key, else
    normalized-title + year."""
    df = df.copy()
    counts = df["dedupe_key"].value_counts()
    dup_keys = set(counts[counts > 1].index)
    df["is_duplicate"] = df["dedupe_key"].isin(dup_keys)
    return df
