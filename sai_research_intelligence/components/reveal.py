"""
reveal.py

Adapts the reference Instagram Reel's interaction — an organic, cursor-
following mask that reveals a hidden second layer of a portfolio — to the
research-intelligence context.

Layer 1 (always visible): the university's public research identity —
headline + top-line KPIs, in bold italic display type.
Layer 2 (hidden by default): the "Research DNA" layer — a denser, more
analytical strip (Research Momentum, top schools, SDG signal) revealed only
where the cursor / finger passes, through a soft organic blob mask that
morphs continuously as it follows the pointer (never a perfect circle),
exactly like the reference reel. Mouse-leave / touch-end hides it again.

All values are pre-computed from the live, filtered dataframe by app.py and
injected below — this component never invents numbers of its own.
"""

import streamlit as st
import streamlit.components.v1 as components


def _embed(html: str, height: int):
    """Use st.iframe when available (modern Streamlit); fall back to the
    components.v1.html API on older Streamlit versions."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:
        components.html(html, height=height, scrolling=False)


def render_reveal_feature(kpis: dict, momentum: dict, top_schools: list, top_sdgs: list):
    momentum_score = momentum["score"] if momentum["score"] is not None else "N/A"
    schools_html = "".join(
        f'<div class="dna-row"><span>{name}</span><span class="dna-bar-track">'
        f'<span class="dna-bar-fill" style="width:{min(100, pct)}%"></span></span>'
        f'<span class="dna-val">{count}</span></div>'
        for name, count, pct in top_schools
    )
    sdg_chips = "".join(f'<span class="dna-chip">SDG {s}</span>' for s in top_sdgs) or "<span class='dna-chip'>No SDG data</span>"

    html = f"""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0; background: transparent;
    font-family: 'Inter', -apple-system, sans-serif;
    overflow: hidden;
  }}
  .stage {{
    position: relative;
    width: 100%;
    height: 340px;
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(45, 212, 200, 0.18);
    background: linear-gradient(160deg, #0e1622 0%, #0a1018 100%);
    cursor: none;
    touch-action: none;
  }}
  .hint {{
    position: absolute; top: 16px; left: 20px; z-index: 5;
    font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase;
    color: #8b98a9; font-weight: 600;
  }}
  .layer {{
    position: absolute; inset: 0;
    padding: 56px 28px 24px 28px;
  }}
  .layer-base {{ z-index: 1; }}
  .layer-hidden {{
    z-index: 2;
    background: radial-gradient(120% 140% at 30% 20%, #123028 0%, #0a1d18 55%, #08130f 100%);
    -webkit-mask-image: none;
    mask-image: none;
    will-change: mask-image, -webkit-mask-image;
  }}
  .headline {{
    font-family: 'Archivo Black', 'Inter', sans-serif;
    font-style: italic;
    font-weight: 900;
    font-size: clamp(22px, 4vw, 34px);
    line-height: 1.05;
    color: #eef4f6;
    letter-spacing: -0.01em;
    text-transform: uppercase;
    margin: 0 0 6px 0;
  }}
  .headline .accent {{ color: #2dd4c8; }}
  .subtext {{ color: #8b98a9; font-size: 13px; margin-bottom: 22px; max-width: 420px; }}
  .chip-row {{ display: flex; gap: 10px; flex-wrap: wrap; }}
  .chip {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 12px;
    color: #cbd5e1;
  }}
  .chip b {{ color: #e6edf3; font-size: 15px; display: block; }}

  .dna-title {{
    font-family: 'Archivo Black', 'Inter', sans-serif;
    font-style: italic;
    font-weight: 900;
    color: #5eead4;
    font-size: clamp(16px, 2.6vw, 20px);
    text-transform: uppercase;
    margin: 0 0 4px 0;
  }}
  .dna-momentum {{ color: #e6edf3; font-size: 13px; margin-bottom: 14px; }}
  .dna-momentum b {{ color: #5eead4; font-size: 20px; }}
  .dna-row {{ display: grid; grid-template-columns: 110px 1fr 32px; align-items: center; gap: 8px; margin-bottom: 7px; }}
  .dna-row span:first-child {{ font-size: 11px; color: #9fb3ac; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .dna-bar-track {{ background: rgba(255,255,255,0.06); border-radius: 6px; height: 7px; overflow: hidden; }}
  .dna-bar-fill {{ display: block; height: 100%; background: linear-gradient(90deg, #2dd4c8, #5eead4); border-radius: 6px; }}
  .dna-val {{ font-size: 11px; color: #cbd5e1; text-align: right; }}
  .dna-chips {{ margin-top: 12px; display: flex; gap: 6px; flex-wrap: wrap; }}
  .dna-chip {{
    font-size: 10.5px; color: #5eead4; border: 1px solid rgba(94,234,212,0.35);
    border-radius: 999px; padding: 3px 9px;
  }}
  .glow {{
    position: absolute; width: 26px; height: 26px; border-radius: 50%;
    background: radial-gradient(circle, rgba(94,234,212,0.9), rgba(94,234,212,0));
    pointer-events: none; z-index: 6; transform: translate(-50%, -50%);
    opacity: 0; transition: opacity 0.15s ease;
  }}
</style>
</head>
<body>
<div class="stage" id="stage">
  <div class="hint">Move your cursor to reveal the Research DNA →</div>

  <div class="layer layer-base">
    <div class="headline">SAI <span class="accent">RESEARCH</span><br/>INTELLIGENCE</div>
    <div class="subtext">Mapping the University's Research Ecosystem — the public snapshot, at a glance.</div>
    <div class="chip-row">
      <div class="chip"><b>{kpis['total_publications']:,}</b>Publications</div>
      <div class="chip"><b>{kpis['school_count']}</b>Schools</div>
      <div class="chip"><b>{kpis['faculty_count']}</b>Faculty authors</div>
      <div class="chip"><b>{kpis['sdg_count']}/17</b>SDGs engaged</div>
    </div>
  </div>

  <div class="layer layer-hidden" id="hiddenLayer">
    <div class="dna-title">Research DNA — Hidden Signal</div>
    <div class="dna-momentum">Research Momentum <b>{momentum_score}{"/100" if momentum_score != "N/A" else ""}</b></div>
    {schools_html if schools_html else "<div class='dna-momentum'>No school data in current filter.</div>"}
    <div class="dna-chips">{sdg_chips}</div>
  </div>

  <div class="glow" id="glow"></div>
</div>

<script>
(function() {{
  const stage = document.getElementById('stage');
  const hidden = document.getElementById('hiddenLayer');
  const glow = document.getElementById('glow');

  let targetX = -1000, targetY = -1000;
  let curX = -1000, curY = -1000;
  let active = false;
  let t = 0;

  function setPointer(clientX, clientY) {{
    const rect = stage.getBoundingClientRect();
    targetX = clientX - rect.left;
    targetY = clientY - rect.top;
    active = true;
  }}

  stage.addEventListener('mousemove', (e) => setPointer(e.clientX, e.clientY));
  stage.addEventListener('mouseleave', () => {{ active = false; }});
  stage.addEventListener('touchmove', (e) => {{
    if (e.touches && e.touches[0]) setPointer(e.touches[0].clientX, e.touches[0].clientY);
    e.preventDefault();
  }}, {{ passive: false }});
  stage.addEventListener('touchend', () => {{ active = false; }});

  function loop() {{
    t += 0.06;
    // smooth interpolation toward pointer target
    curX += (targetX - curX) * 0.18;
    curY += (targetY - curY) * 0.18;

    const baseR = active ? 130 : 0;
    // organic, continuously morphing radius via layered sine waves (never a perfect circle)
    const r1 = baseR + Math.sin(t * 1.3) * 14;
    const r2 = baseR + Math.cos(t * 1.7 + 1.0) * 10;
    const r3 = baseR + Math.sin(t * 2.1 + 2.0) * 12;

    const grad = `radial-gradient(ellipse ${{r1}}px ${{r2}}px at ${{curX}}px ${{curY}}px, black 0%, black 55%, transparent 78%),`+
                 `radial-gradient(circle ${{r3}}px at ${{curX + 18}}px ${{curY - 12}}px, black 0%, transparent 70%)`;

    hidden.style.maskImage = grad;
    hidden.style.webkitMaskImage = grad;
    hidden.style.maskComposite = 'add';
    hidden.style.webkitMaskComposite = 'source-over';

    if (active) {{
      glow.style.left = curX + 'px';
      glow.style.top = curY + 'px';
      glow.style.opacity = '0.7';
    }} else {{
      glow.style.opacity = '0';
    }}

    requestAnimationFrame(loop);
  }}
  loop();
}})();
</script>
</body>
</html>
"""
    _embed(html, height=360)
