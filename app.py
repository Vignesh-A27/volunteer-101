import streamlit as st
import base64
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the absolute path to the config directory
current_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.abspath(os.path.join(current_dir, 'config'))
service_account_path = os.path.join(config_dir, "demo.json")

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error initializing Firebase: {str(e)}")
        st.stop()

# Get Firestore database instance
try:
    db = firestore.client()
except Exception as e:
    st.error(f"Error connecting to Firestore: {str(e)}")
    st.stop()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'volunteer_id' not in st.session_state:
    st.session_state.volunteer_id = None
if 'volunteer_name' not in st.session_state:
    st.session_state.volunteer_name = None
if 'org_id' not in st.session_state:
    st.session_state.org_id = None
if 'org_name' not in st.session_state:
    st.session_state.org_name = None

st.set_page_config(
    page_title="Vol-Link",
    page_icon="🤝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
# Function to encode video file to base64
def get_base64_video(video_path):
    with open(video_path, "rb") as video_file:
        video_base64 = base64.b64encode(video_file.read()).decode()
    return video_base64

# Path to your local video file
video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "volvid1.mp4")

# Convert video to base64
video_base64 = get_base64_video(video_path)

# HTML and CSS for background video
video_html = f"""
    <style>
    .stApp {{
        position: fixed;
        overflow: hidden;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        background: rgba(0, 0, 0, 0.3);
    }}
    video {{
        position: fixed;
        top: 50%;
        left: 50%;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        z-index: -2;
        transform: translate(-50%, -50%);
        object-fit: cover;
    }}
    .logo-text {{
        font-size: 4rem;
        font-weight: 700;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }}
    .tagline {{
        font-size: 2rem;
        text-align: center;
        color: white;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
    }}
    .sub-tagline {{
        font-size: 1.2rem;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }}
    .stButton button {{
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        color: white !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        width: 100% !important;
        height: auto !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
    }}
    .stButton button:hover {{
        background: rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2) !important;
    }}
    </style>

    <video autoplay loop muted>
        <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
    </video>
"""

# Inject HTML into Streamlit
st.markdown(video_html, unsafe_allow_html=True)

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Main Content
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Logo and Tagline
st.markdown('<h1 class="logo-text">Vol-Link</h1>', unsafe_allow_html=True)
st.markdown('<h1 class="tagline">Make a Difference Today</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-tagline">Join our community of changemakers and create lasting impact</p>', unsafe_allow_html=True)

# Create two columns for the cards
col1, col2 = st.columns(2)

# Organization Card Button
with col1:
    org_content = """🏢

For Organizations

Create and manage events, recruit volunteers, and track impact. Build your community and make a difference.

→ Login as Organization"""
    
    if st.button(org_content, key="org_login"):
        st.switch_page("pages/Organization_Login.py")

# Volunteer Card Button
with col2:
    vol_content = """👥

For Volunteers

Discover opportunities, connect with causes, and make a difference. Join a community of changemakers.

→ Login as Volunteer"""
    
    if st.button(vol_content, key="vol_login"):
        st.switch_page("pages/Volunteer_Login.py")

st.markdown('</div>', unsafe_allow_html=True)
