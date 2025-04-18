import streamlit as st
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import os

# Get the absolute path to the config directory
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
service_account_path = os.path.join(root_dir, "config", "demo.json")

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error initializing Firebase: {str(e)}")
        st.stop()

# Initialize Firestore
db = firestore.client()

st.set_page_config(page_title="Organization Signup")

# Custom CSS
st.markdown("""
    <style>
        .stApp {
            background: #FFFFFF !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #262626;
        }
        .auth-card {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            border: 1px solid #E0E0E0;
            box-shadow: 0 2px 4px rgba(33, 150, 243, 0.1);
            margin-bottom: 1rem;
            margin-top: 2rem;
            position: relative;
        }
        .back-btn {
            position: absolute;
            left: 1rem;
            top: 1rem;
            padding: 0.4rem 0.8rem;
            background-color: #2196F3;
            color: white !important;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            width: auto !important;
        }
        .back-btn:hover {
            background-color: #1976D2;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(33, 150, 243, 0.2);
        }
        .stButton button {
            background: #2196F3 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            transition: all 0.3s ease !important;
            width: 100%;
            box-shadow: 0 2px 4px rgba(33, 150, 243, 0.1);
        }
        .stButton button:hover {
            background: #1976D2 !important;
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(33, 150, 243, 0.2) !important;
        }
        div[data-testid="stMarkdownContainer"] {
            color: #262626 !important;
        }
        [data-testid="stHeader"] {
            background: white;
            border-bottom: 1px solid #dbdbdb;
        }
        [data-testid="stSidebar"] {
            background: white;
            border-right: 1px solid #dbdbdb;
        }
        [data-testid="stSidebarNav"] {
            color: #262626 !important;
        }
        .stTextInput input, .stTextArea textarea {
            border-radius: 6px !important;
            border: 1px solid #dbdbdb !important;
            padding: 0.5rem !important;
            font-size: 0.9rem !important;
            color: #262626 !important;
            background-color: white !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #8e8e8e !important;
            box-shadow: none !important;
        }
        .stTextInput label, .stTextArea label {
            color: #262626 !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
        }
        [data-testid="stAppViewContainer"] {
            color: #262626;
        }
        .main-title {
            color: #262626;
            font-size: 1.8rem;
            font-weight: 600;
            text-align: center;
            margin-bottom: 1rem;
        }
        [data-testid="stNotificationMessage"] {
            background: white;
            border: 1px solid #dbdbdb;
            border-radius: 8px;
            color: #262626;
        }
        .signup-text {
            color: #0095f6 !important;
            text-align: center;
            margin-top: 1rem;
            font-size: 0.9rem;
        }
        .page-title {
            color: #262626;
            font-size: 1.8rem;
            font-weight: 600;
            text-align: center;
            margin-bottom: 2rem;
            margin-top: 0;
            padding-top: 0;
        }
    </style>
""", unsafe_allow_html=True)

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



col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if st.button("← Back", key="org_signup_back_btn", help="Go back to home"):
        st.switch_page("app.py")

with col2:
    st.markdown('<div style="margin-top: -1rem;">', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Organization Sign Up</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    name = st.text_input("Organization Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    description = st.text_area("Organization Description")
    contact_number = st.text_input("Contact Number")
    website = st.text_input("Organization Website Link")
    
    if st.button("Sign Up"):
        if name and email and password and confirm_password and description and contact_number:
            if password == confirm_password:
                try:
                    # Check if email already exists
                    existing_org = db.collection('organizations').where('email', '==', email).get()
                    if not existing_org:
                        # Add organization to Firestore
                        org_ref = db.collection('organizations').add({
                            'name': name,
                            'email': email,
                            'password': password,
                            'description': description,
                            'contact_number': contact_number,
                            'website': website
                        })
                        st.success("Organization registered successfully!")
                        st.switch_page("pages/Organization_Login.py")
                    else:
                        st.error("An organization with this email already exists")
                except Exception as e:
                    st.error(f"Error during registration: {str(e)}")
            else:
                st.error("Passwords do not match")
        else:
            st.warning("Please fill in all fields")

# Hide sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)
