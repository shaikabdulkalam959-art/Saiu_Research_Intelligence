"""
data_loader.py
API-first data access layer for SAI RESEARCH INTELLIGENCE.

The REST API is the single source of truth for every publication record.
Nothing here is hardcoded — if the API is unreachable or malformed we
surface a clear error state instead of inventing data.
"""

import time
import requests
import pandas as pd
import streamlit as st

API_URL = "https://sai-publications-dashboard.vercel.app/api/publications"
REQUEST_TIMEOUT = 20  # seconds


class APIError(Exception):
    """Raised for any API-related failure with a human-readable reason."""
    def __init__(self, message: str, kind: str = "error"):
        super().__init__(message)
        self.message = message
        self.kind = kind  # "timeout" | "http" | "json" | "empty" | "shape" | "error"


def _request_with_retry(url: str, retries: int = 2, backoff: float = 1.5):
    last_exc = None
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            return resp
        except requests.exceptions.Timeout as e:
            last_exc = APIError(
                "The publications API timed out. It may be waking up (cold start) "
                "or temporarily slow.", "timeout"
            )
        except requests.exceptions.ConnectionError as e:
            last_exc = APIError(
                "Could not connect to the publications API. Check your network "
                "connection or the API's availability.", "error"
            )
        except requests.exceptions.RequestException as e:
            last_exc = APIError(f"Unexpected request error: {e}", "error")
        if attempt < retries:
            time.sleep(backoff * (attempt + 1))
    raise last_exc


def validate_response(resp) -> list:
    """Validate HTTP status + JSON shape, return the raw list of records."""
    if resp.status_code != 200:
        raise APIError(
            f"The publications API returned HTTP {resp.status_code}.", "http"
        )
    try:
        payload = resp.json()
    except ValueError:
        raise APIError(
            "The publications API did not return valid JSON.", "json"
        )

    # The observed schema wraps records in {"data": [...]}. Support a bare
    # list as a fallback in case the API shape changes.
    if isinstance(payload, dict) and "data" in payload:
        records = payload["data"]
    elif isinstance(payload, list):
        records = payload
    else:
        raise APIError(
            "The publications API responded with an unexpected JSON shape "
            "(no top-level 'data' list found).", "shape"
        )

    if not isinstance(records, list):
        raise APIError(
            "The 'data' field in the API response is not a list of records.",
            "shape",
        )

    if len(records) == 0:
        raise APIError("The publications API returned zero records.", "empty")

    return records


@st.cache_data(ttl=900, show_spinner=False)
def load_data() -> pd.DataFrame:
    """
    Fetch, validate and return the raw publications as a DataFrame.
    Raises APIError on any failure — callers must handle it and render
    an error state rather than falling back to fake data.
    """
    resp = _request_with_retry(API_URL)
    records = validate_response(resp)
    df = pd.DataFrame.from_records(records)
    return df
