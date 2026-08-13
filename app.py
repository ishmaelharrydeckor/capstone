import streamlit as st

# Configure page metadata first (MUST be the very first Streamlit command)
st.set_page_config(
    page_title="EngSuite - Computational Engineering Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define sub-pages
pipe_flow_page = st.Page("pages/page_pipe_flow.py", title="Pipe Flow Analyser", icon="🚰")
heat_transfer_page = st.Page("pages/page_heat_transfer.py", title="Heat Transfer Calculator", icon="🔥")
data_dashboard_page = st.Page("pages/page_data_dashboard.py", title="Rock & Fluid Dashboard", icon="📊")
documentation_page = st.Page("pages/page_documentation.py", title="AI Usage & Documentation", icon="📚")

# Setup multi-page navigation layout
pg = st.navigation({
    "Engineering Modules": [pipe_flow_page, heat_transfer_page, data_dashboard_page],
    "Documentation": [documentation_page]
})

# Custom CSS styling for premium Vercel-like dark mode and beautiful metrics
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

/* Main font family overrides */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Inter', sans-serif !important;
}

/* Headline Styling with tight tracking and custom typeface */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}

/* Custom premium card design */
.premium-card {
    background-color: #18181B;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.premium-card:hover {
    border-color: rgba(0, 114, 245, 0.4);
    box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* Sleek Metrics styling */
.metric-container {
    background-color: #18181B;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    display: flex;
    flex-direction: column;
    height: 100%;
}
.metric-label {
    font-size: 0.85rem;
    color: #A1A1AA;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #ECEDEE;
    font-family: 'Outfit', sans-serif;
    margin-top: 0.5rem;
    letter-spacing: -0.02em;
}
.metric-unit {
    font-size: 0.9rem;
    color: #71717A;
    font-weight: 500;
    margin-left: 0.25rem;
}

/* Sidebar styling tweaks */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}

/* Custom badges */
.badge {
    display: inline-block;
    padding: 0.25em 0.5em;
    font-size: 75%;
    font-weight: 700;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 0.25rem;
    background-color: rgba(0, 114, 245, 0.15);
    color: #0072F5;
    border: 1px solid rgba(0, 114, 245, 0.3);
}
</style>
"""

# Inject CSS rules
st.markdown(custom_css, unsafe_allow_html=True)

# Execute page routing
pg.run()
