"""
charts_interactive.py

Matplotlib/Seaborn (see charts.py) render static images — a browser image
cannot show a floating tooltip on hover, no matter how it's styled. To get
the Power-BI-style "hover over a point/bar and see a floating value card"
interaction the user asked for, these specific charts are rendered with
Plotly instead (st.plotly_chart), which draws real interactive SVG/canvas
elements with built-in hover tooltips, while keeping the same dark/teal
visual identity as the rest of the dashboard.

Used only where hover genuinely adds value (trends, comparisons, rankings) —
the SDG matrix, co-occurrence and school×year heatmaps, and distribution
histograms stay on the required Matplotlib/Seaborn stack in charts.py.
"""

import plotly.graph_objects as go
import streamlit as st

BG = "#131c2b"
ACCENT = "#2dd4c8"
ACCENT_2 = "#5eead4"
TEXT = "#e6edf3"
MUTED = "#8b98a9"
GRID = "#22303f"
PALETTE = ["#2dd4c8", "#5eead4", "#3b82f6", "#f97316", "#a78bfa", "#f472b6", "#facc15"]

_HOVERLABEL = dict(
    bgcolor="#0d1520", font_size=12, font_color=TEXT,
    bordercolor="rgba(45,212,200,0.5)",
)


def _base_layout(fig, title, height=340):
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=TEXT, family="Inter"), x=0),
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=TEXT, family="Inter", size=11),
        margin=dict(l=10, r=10, t=44, b=10),
        height=height,
        hoverlabel=_HOVERLABEL,
        hovermode="x unified",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT, size=10)),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, color=TEXT)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, color=TEXT)
    return fig


def render_trend_hover(years, counts, title="Annual Publication Trend"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=counts, mode="lines+markers", line=dict(color=ACCENT, width=3, shape="spline"),
        marker=dict(size=8, color=ACCENT, line=dict(color=BG, width=1.5)),
        fill="tozeroy", fillcolor="rgba(45,212,200,0.10)",
        hovertemplate="<b>%{x}</b><br>Publications: %{y}<extra></extra>",
        name="Publications",
    ))
    _base_layout(fig, title)
    fig.update_yaxes(rangemode="tozero")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_stacked_area_hover(years, series: dict, title):
    fig = go.Figure()
    for i, (name, values) in enumerate(series.items()):
        color = PALETTE[i % len(PALETTE)]
        fig.add_trace(go.Scatter(
            x=years, y=values, mode="lines", stackgroup="one", name=name,
            line=dict(width=0.6, color=color),
            hovertemplate=f"<b>{name}</b>: %{{y}}<extra></extra>",
        ))
    _base_layout(fig, title)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_bar_hover(categories, values, title, horizontal=True, color=ACCENT, value_suffix=""):
    fig = go.Figure()
    if horizontal:
        fig.add_trace(go.Bar(
            x=values, y=categories, orientation="h", marker=dict(color=color),
            hovertemplate=f"<b>%{{y}}</b><br>%{{x}}{value_suffix}<extra></extra>",
        ))
        fig.update_yaxes(autorange="reversed")
    else:
        fig.add_trace(go.Bar(
            x=categories, y=values, marker=dict(color=color),
            hovertemplate=f"<b>%{{x}}</b><br>%{{y}}{value_suffix}<extra></extra>",
        ))
    _base_layout(fig, title, height=max(300, 32 * len(categories)) if horizontal else 340)
    fig.update_layout(hovermode="closest")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_grouped_bar_hover(categories, series: dict, title):
    fig = go.Figure()
    for i, (name, values) in enumerate(series.items()):
        fig.add_trace(go.Bar(
            x=categories, y=values, name=name, marker=dict(color=PALETTE[i % len(PALETTE)]),
            hovertemplate=f"<b>{name}</b>: %{{y}}%<extra></extra>",
        ))
    fig.update_layout(barmode="group")
    _base_layout(fig, title, height=380)
    fig.update_layout(hovermode="closest")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_donut_hover(labels, values, title, colors=None):
    colors = colors or PALETTE
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors[: len(labels)], line=dict(color=BG, width=2)),
        hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>",
        textinfo="percent", textfont=dict(color=TEXT, size=11),
    )])
    _base_layout(fig, title, height=340)
    fig.update_layout(hovermode="closest")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
