"""Vendor Failure Forecast: Streamlit host for the self-contained HTML app.

The forecast model, charts and what-if controls all run in the browser, inside
vendor_failure_forecast.html (data and code are inline). This file only serves
that page full-width inside a Streamlit app, so it can be deployed on Streamlit
Community Cloud or run locally with:   streamlit run streamlit_app.py

Data is synthetic: it shows how the method behaves, not how a real property would perform.
"""
from pathlib import Path

import streamlit as st

HTML_FILE = Path(__file__).parent / "vendor_failure_forecast.html"

# Height handling. On Streamlit 1.56+ the page is embedded with st.iframe(height="content"),
# which sizes the frame to the page. If the page is ever cut off, or leaves a gap at the
# bottom, after switching tabs or changing a scenario, set SELF_FIT = True: the page then
# resizes its own frame (this is always used on older Streamlit, which has no "content" mode).
SELF_FIT = False
START_HEIGHT = 1800  # pixels; only the starting height when SELF_FIT is on

st.set_page_config(
    page_title="Vendor Failure Forecast",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Remove Streamlit's own header, footer and page padding so the app fills the page.
st.markdown(
    """
    <style>
      [data-testid="stHeader"], [data-testid="stToolbar"], footer, #MainMenu { display: none !important; }
      .block-container, [data-testid="stMainBlockContainer"] {
        padding: 0 !important; max-width: 100% !important;
      }
      iframe { border: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

FIT_SCRIPT = """<script>
(function () {
  var frame;
  try { frame = window.frameElement; } catch (e) { return; }
  if (!frame) return;               // opened on its own, not embedded
  var last = -1, queued = false;
  function fit() {
    queued = false;
    var h = Math.ceil(document.documentElement.getBoundingClientRect().height);
    if (h > 0 && h !== last) { last = h; frame.style.height = h + 'px'; frame.setAttribute('height', h); }
  }
  function schedule() { if (!queued) { queued = true; requestAnimationFrame(fit); } }
  if (window.ResizeObserver) new ResizeObserver(schedule).observe(document.documentElement);
  window.addEventListener('load', schedule);
  window.addEventListener('resize', schedule);
  schedule();
})();
</script>"""


@st.cache_data(show_spinner=False)
def load_page() -> str:
    return HTML_FILE.read_text(encoding="utf-8")


def theme_type():
    """'light' or 'dark' if Streamlit reports its theme, else None (the page then follows the OS)."""
    try:
        t = st.context.theme.type
        return t if t in ("light", "dark") else None
    except Exception:
        return None


def prepare(html: str, theme, self_fit: bool) -> str:
    if theme:  # keep the page's colours consistent with the Streamlit theme
        html = html.replace('<html lang="en">', f'<html lang="en" data-theme="{theme}">', 1)
    if self_fit:
        i = html.rfind("</body>")
        html = html[:i] + FIT_SCRIPT + html[i:]
    return html


has_iframe = hasattr(st, "iframe")  # Streamlit 1.56+
page = prepare(load_page(), theme_type(), self_fit=SELF_FIT or not has_iframe)

if has_iframe:
    st.iframe(page, height=START_HEIGHT if SELF_FIT else "content")
else:
    import streamlit.components.v1 as components

    components.html(page, height=START_HEIGHT, scrolling=True)
