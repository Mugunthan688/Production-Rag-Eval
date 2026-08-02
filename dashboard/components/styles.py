import streamlit as st


def apply_master_theme():
    """Applies the Stitch Deep Research AI master UI/UX theme styling."""
    st.markdown(
        """
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Hide default Streamlit top header & footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Main app canvas */
        .stApp {
            background-color: #090D16;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.10) 0px, transparent 50%);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0D121F !important;
            border-right: 1px solid rgba(99, 102, 241, 0.15);
        }

        section[data-testid="stSidebar"] .stMarkdown h1, 
        section[data-testid="stSidebar"] .stMarkdown h2, 
        section[data-testid="stSidebar"] .stMarkdown h3 {
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #F3F4F6;
        }

        /* Hero Titles & Gradient Text */
        .hero-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 800;
            font-size: 2.2rem;
            background: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }

        .hero-subtitle {
            color: #9CA3AF;
            font-size: 1.05rem;
            margin-bottom: 1.5rem;
        }

        /* Glassmorphic Cards */
        .glass-card {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
            padding: 18px 22px;
            margin-bottom: 16px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .glass-card:hover {
            border-color: rgba(99, 102, 241, 0.45);
            transform: translateY(-2px);
        }

        /* Badges */
        .badge-violet {
            background: rgba(99, 102, 241, 0.18);
            color: #818CF8;
            border: 1px solid rgba(99, 102, 241, 0.4);
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .badge-green {
            background: rgba(16, 185, 129, 0.18);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.4);
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .badge-amber {
            background: rgba(245, 158, 11, 0.18);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.4);
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        /* Custom Buttons */
        div.stButton > button {
            background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 10px 24px !important;
            box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39) !important;
            transition: all 0.2s ease-in-out !important;
        }

        div.stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.55) !important;
        }

        /* Metrics Display */
        div[data-testid="stMetric"] {
            background: rgba(17, 24, 39, 0.6);
            border: 1px solid rgba(99, 102, 241, 0.15);
            border-radius: 10px;
            padding: 12px 16px;
        }

        div[data-testid="stMetricLabel"] {
            color: #9CA3AF !important;
            font-size: 0.85rem !important;
        }

        div[data-testid="stMetricValue"] {
            color: #F9FAFB !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
