import streamlit as st
from datetime import datetime, date, time
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Get the absolute path to the config directory
config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config'))
key_path = os.path.join(config_dir, "demo.json")

# Initialize session state for organization
if 'org_id' not in st.session_state:
    st.session_state.org_id = None
if 'org_name' not in st.session_state:
    st.session_state.org_name = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

# Validate authentication
if not st.session_state.get('org_id'):
    st.warning("Please login first")
    st.switch_page("pages/Organization_Login.py")

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(key_path)
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

# Define minimum datetime for sorting
MIN_DATETIME = datetime(2000, 1, 1)  # Use a reasonable minimum date instead of datetime.min

# Helper Functions
def get_org_name(org_id):
    """Helper function to get organization name from org_id"""
    try:
        if not org_id:
            return "Unknown Organization"
        
        org_ref = db.collection('organizations').document(org_id).get()
        if org_ref.exists:
            return org_ref.to_dict().get('name', 'Unknown Organization')
        return "Unknown Organization"
    except Exception as e:
        st.error(f"Error fetching organization name: {str(e)}")
        return "Unknown Organization"

def get_event_date(event):
    """Helper function to get event date for sorting"""
    event_dict = event.to_dict()
    event_date = event_dict.get('date')
    if isinstance(event_date, datetime):
        # Convert to naive datetime if it has timezone info
        if event_date.tzinfo is not None:
            event_date = event_date.replace(tzinfo=None)
        return event_date
    return MIN_DATETIME

def format_date(date_obj):
    """Helper function to format dates consistently"""
    if date_obj is None:
        return "Date not set"
    if isinstance(date_obj, datetime):
        # Convert to naive datetime if it has timezone info
        if date_obj.tzinfo is not None:
            date_obj = date_obj.replace(tzinfo=None)
        return date_obj.strftime("%d-%m-%Y")
    return str(date_obj)

# Page config
st.set_page_config(page_title="Organization Dashboard", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        .stApp {
            background: #fafafa !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #262626;
        }
        .event-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid #dbdbdb;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        .event-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(33, 150, 243, 0.1);
        }
        .event-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #1976D2;
        }
        .event-details {
            color: #666666;
            font-size: 0.9rem;
        }
        [data-testid="stSidebar"] {
            background: white;
            border-right: 1px solid #E0E0E0;
        }
        [data-testid="stSidebarNav"] {
            color: #262626 !important;
        }
        .stButton button {
            background: #2196F3 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(33, 150, 243, 0.2) !important;
        }
        .stButton button:hover {
            background: #1976D2 !important;
            box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3) !important;
            transform: translateY(-1px);
        }
        .stButton button[data-testid="baseButton-secondary"] {
            background: #E3F2FD !important;
            color: #1976D2 !important;
        }
        .stButton button[data-testid="baseButton-secondary"]:hover {
            background: #BBDEFB !important;
        }
        .stMetric {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #E0E0E0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        .stMetric:hover {
            border-color: #2196F3;
            box-shadow: 0 4px 8px rgba(33, 150, 243, 0.1);
        }
        .stMetric [data-testid="stMetricValue"] {
            color: #1976D2;
            font-weight: 600;
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



# Check if organization is logged in
if 'org_id' not in st.session_state:
    st.warning("Please login first")
    st.switch_page("pages/Organization_Login.py")

# Display welcome message
st.markdown("""
    <div style="text-align: center; padding: 2rem; background: white; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #dbdbdb;">
        <h1 style="color: #262626; font-size: 1.8rem; font-weight: 600;">👋 Welcome, {}</h1>
        <p style="color: #8e8e8e; font-size: 1rem;">Manage your events and connect with volunteers!</p>
    </div>
""".format(get_org_name(st.session_state.get('org_id', ''))), unsafe_allow_html=True)

# Initialize current page in session state if not exists
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

# Top Navigation
col1, col2, col3, col4, col5, col_space, col_logout = st.columns([1, 1, 1, 1, 1, 0.5, 1])

with col1:
    if st.button("📊 Dashboard", key="nav_dash", use_container_width=True, type="primary" if st.session_state.current_page == 'dashboard' else "secondary"):
        st.session_state.current_page = 'dashboard'
        st.experimental_rerun()

with col2:
    if st.button("📅 Events", key="nav_events", use_container_width=True, type="primary" if st.session_state.current_page == 'events' else "secondary"):
        st.session_state.current_page = 'events'
        st.experimental_rerun()

with col3:
    if st.button("👥 Applications", key="nav_apps", use_container_width=True, type="primary" if st.session_state.current_page == 'applications' else "secondary"):
        st.session_state.current_page = 'applications'
        st.experimental_rerun()

with col4:
    if st.button("🔔 Notifications", key="nav_notif", use_container_width=True, type="primary" if st.session_state.current_page == 'notifications' else "secondary"):
        st.session_state.current_page = 'notifications'
        st.experimental_rerun()

with col5:
    if st.button("👤 Profile", key="nav_profile", use_container_width=True, type="primary" if st.session_state.current_page == 'profile' else "secondary"):
        st.session_state.current_page = 'profile'
        st.experimental_rerun()

with col_logout:
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/Organization_Login.py")

st.markdown("<br>", unsafe_allow_html=True)

# Get current page from session state
current_page = st.session_state.current_page

# Initialize session state for org_id if not exists
if 'org_id' not in st.session_state:
    st.error("⚠️ Please log in first!")
    st.switch_page("pages/Organization_Login.py")

if current_page == 'dashboard':
    try:
        # Get organization's events
        events_ref = db.collection('events').where('org_id', '==', st.session_state['org_id']).stream()
        events_list = list(events_ref)
        
        # Calculate statistics
        total_events = len(events_list)
        active_events = sum(1 for event in events_list if event.to_dict().get('status') == 'active')
        total_applications = sum(len(event.to_dict().get('applications', [])) for event in events_list)
        
        # Display statistics
        st.markdown("### 📊 Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Events", total_events)
        with col2:
            st.metric("Total Applications", total_applications)
        with col3:
            st.metric("Active Events", active_events)
            
        # Display recent events
        st.markdown("### 📅 Recent Events")
        if not events_list:
            st.info("🎯 No events created yet. Create your first event in the Events section!")
        else:
            # Sort events by date
            sorted_events = sorted(events_list, key=get_event_date, reverse=True)[:5]  # Get 5 most recent events
            
            for event in sorted_events:
                event_data = event.to_dict()
                event_date = event_data.get('date')
                formatted_date = format_date(event_date)
                
                st.markdown(f"""
                    <div class="event-card">
                        <div class="event-title">🎯 {event_data.get('title', 'Event Title')}</div>
                        <div class="event-details">
                            <p>📅 Date: {formatted_date}</p>
                            <p>📍 Location: {event_data.get('location', 'Location TBD')}</p>
                            <p>👥 Applications: {len(event_data.get('applications', []))}</p>
                            <p>✨ Status: {event_data.get('status', 'active').title()}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("👥 View Applications", key=f"view_apps_{event.id}"):
                    st.session_state.current_page = 'applications'
                    st.session_state.selected_event = event.id
                    st.experimental_rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {str(e)}")

elif current_page == 'events':
    st.subheader("📅 Events")
    
    # Add new event button
    if st.button("➕ Create New Event"):
        st.session_state.show_event_form = True
    
    # Event creation form
    if st.session_state.get('show_event_form', False):
        with st.form("create_event_form"):
            st.markdown("### ✨ Create New Event")
            title = st.text_input("📝 Event Title")
            description = st.text_area("📄 Description")
            col1, col2 = st.columns(2)
            with col1:
                event_date = st.date_input("📅 Date")
            with col2:
                event_time = st.time_input("⏰ Time")
            location = st.text_input("📍 Location")
            required_volunteers = st.number_input("👥 Required Volunteers", min_value=1, value=1)
            skills_required = st.multiselect(
                "🎯 Required Skills",
                ["Teaching", "First Aid", "Event Planning", "Social Media", "Photography", "Writing/Editing",
                 "Leadership", "Communication", "Project Management", "Fundraising", "Marketing",
                 "Web Development", "Graphic Design", "Data Analysis", "Research", "Public Speaking",
                 "Language Translation", "Counseling", "Sports Coaching", "Music", "Art & Crafts",
                 "Environmental Conservation", "Animal Care", "Healthcare", "Elderly Care", "Child Care",
                 "Food Service", "Administrative", "Legal Aid", "IT Support", "Logistics",
                 "Mental Health Support", "Crisis Management", "Disaster Response", "Community Outreach",
                 "Cultural Awareness", "Sign Language", "Special Education", "Youth Mentoring",
                 "Financial Literacy", "Tutoring", "Gardening", "Carpentry", "Cooking", "Driving",
                 "Emergency Response", "Grant Writing", "Social Work", "Conflict Resolution",
                 "Disability Support", "Veteran Support", "Homeless Support", "Literacy Education",
                 "Digital Marketing", "Video Production", "Content Creation", "Technical Writing",
                 "Database Management", "Mobile App Development", "UI/UX Design", "Quality Assurance",
                 "Cybersecurity", "Cloud Computing", "Data Privacy", "Blockchain", "AI/ML",
                 "Virtual Reality", "Augmented Reality", "3D Printing", "Robotics", "IoT",
                 "Environmental Science", "Renewable Energy", "Waste Management", "Water Conservation",
                 "Sustainable Agriculture", "Climate Change Education", "Wildlife Conservation",
                 "Marine Conservation", "Forest Conservation", "Habitat Restoration"]
            )
            
            custom_skills = st.text_input("✨ Custom Skills (Optional)", help="Enter additional required skills separated by commas")
            
            if st.form_submit_button("💾 Create Event"):
                try:
                    # Combine date and time into datetime (ensure it's timezone naive)
                    event_datetime = datetime.combine(event_date, event_time)
                    
                    # Process custom skills
                    all_skills = skills_required.copy()
                    if custom_skills.strip():
                        custom_skills_list = [skill.strip() for skill in custom_skills.split(',') if skill.strip()]
                        all_skills.extend(custom_skills_list)
                    
                    # Create event in Firestore
                    event_data = {
                        'title': title,
                        'description': description,
                        'date': event_datetime,  # This will be timezone naive
                        'location': location,
                        'required_volunteers': required_volunteers,
                        'skills_required': all_skills,
                        'org_id': st.session_state['org_id'],
                        'org_name': st.session_state['org_name'],
                        'status': 'active',
                        'applications': [],
                        'created_at': datetime.now()  # This will be timezone naive
                    }
                    
                    db.collection('events').add(event_data)
                    st.success("✅ Event created successfully!")
                    st.session_state.show_event_form = False
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Error creating event: {str(e)}")
    
    try:
        # Get organization's events
        events_ref = db.collection('events').where('org_id', '==', st.session_state['org_id']).stream()
        events_list = list(events_ref)
        
        if not events_list:
            st.info("🎯 No events created yet. Create your first event!")
        else:
            # Sort events by date
            sorted_events = sorted(events_list, key=get_event_date, reverse=True)
            
            for event in sorted_events:
                event_data = event.to_dict()
                event_date = event_data.get('date')
                formatted_date = format_date(event_date)
                
                st.markdown(f"""
                    <div class="event-card">
                        <div class="event-title">🎯 {event_data.get('title', 'Event Title')}</div>
                        <div class="event-details">
                            <p>📅 Date: {formatted_date}</p>
                            <p>📍 Location: {event_data.get('location', 'Location TBD')}</p>
                            <p>📝 Description: {event_data.get('description', 'No description available.')}</p>
                            <p>👥 Required Volunteers: {event_data.get('required_volunteers', 'Not specified')}</p>
                            <p>⭐ Skills Required: {', '.join(event_data.get('skills_required', ['None specified']))}</p>
                            <p>👥 Applications: {len(event_data.get('applications', []))}</p>
                            <p>✨ Status: {event_data.get('status', 'active').title()}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👥 View Applications", key=f"view_apps_{event.id}"):
                        st.session_state.current_page = 'applications'
                        st.session_state.selected_event = event.id
                        st.experimental_rerun()
                
                with col2:
                    current_status = event_data.get('status', 'active')
                    new_status = 'inactive' if current_status == 'active' else 'active'
                    if st.button(f"{'🔴' if current_status == 'active' else '🟢'} Mark as {new_status.title()}", key=f"status_{event.id}"):
                        try:
                            db.collection('events').document(event.id).update({
                                'status': new_status
                            })
                            st.success(f"✅ Event marked as {new_status}!")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"❌ Error updating event status: {str(e)}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"❌ Error loading events: {str(e)}")

elif current_page == 'applications':
    st.subheader("👥 Applications")
    
    try:
        if 'selected_event' in st.session_state:
            # Get event details
            event_ref = db.collection('events').document(st.session_state['selected_event']).get()
            if event_ref.exists:
                event_data = event_ref.to_dict()
                
                st.markdown(f"""
                    <div class="event-card">
                        <div class="event-title">🎯 {event_data.get('title', 'Event Title')}</div>
                        <div class="event-details">
                            <p>📅 Date: {format_date(event_data.get('date'))}</p>
                            <p>📍 Location: {event_data.get('location', 'Location TBD')}</p>
                            <p>👥 Applications: {len(event_data.get('applications', []))}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Get applications for this event
                applications_ref = db.collection('applications').where('event_id', '==', st.session_state['selected_event']).stream()
                applications_list = list(applications_ref)
                
                if not applications_list:
                    st.info("📭 No applications received yet for this event.")
                else:
                    for application in applications_list:
                        app_data = application.to_dict()
                        
                        # Get volunteer details to ensure we have complete information
                        volunteer_ref = db.collection('volunteers').document(app_data.get('volunteer_id')).get()
                        volunteer_data = volunteer_ref.to_dict() if volunteer_ref.exists else {}
                        
                        # Get phone and format application date
                        phone = volunteer_data.get('phone') or app_data.get('volunteer_phone', 'Phone not provided')
                        applied_date = app_data.get('created_at') or app_data.get('applied_at')
                        formatted_applied_date = format_date(applied_date) if applied_date else 'Date not available'
                        
                        st.markdown(f"""
                            <div class="event-card">
                                <div class="event-title">👤 {app_data.get('volunteer_name', 'Volunteer')}</div>
                                <div class="event-details">
                                    <p>📧 Email: {app_data.get('volunteer_email', 'Email not provided')}</p>
                                    <p>📱 Phone: {phone}</p>
                                    <p>✨ Status: {app_data.get('status', 'pending').title()}</p>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Application actions
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Accept", key=f"accept_{application.id}"):
                                try:
                                    # Update application status
                                    db.collection('applications').document(application.id).update({
                                        'status': 'accepted'
                                    })
                                    
                                    # Create notification and send email for volunteer
                                    notification_data = {
                                        'volunteer_id': app_data.get('volunteer_id'),
                                        'title': 'Application Accepted',
                                        'message': f"Your application for {event_data.get('title')} has been accepted!",
                                        'timestamp': datetime.now(),
                                        'read': False,
                                        'type': 'application_accepted',
                                        'event_id': st.session_state['selected_event']
                                    }
                                    db.collection('notifications').add(notification_data)
                                    
                                    # Send acceptance email
                                    from services.mail_service import EmailService
                                    email_service = EmailService()
                                    email_service.send_volunteer_acceptance_notification(
                                        volunteer_email=app_data.get('volunteer_email'),
                                        volunteer_name=app_data.get('volunteer_name'),
                                        event_name=event_data.get('title'),
                                        org_name=st.session_state.get('org_name')
                                    )
                                    
                                    st.success("✅ Application accepted!")
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"❌ Error accepting application: {str(e)}")
                        
                        with col2:
                            if st.button("❌ Reject", key=f"reject_{application.id}"):
                                try:
                                    # Update application status
                                    db.collection('applications').document(application.id).update({
                                        'status': 'rejected'
                                    })
                                    
                                    # Create notification and send email for volunteer
                                    notification_data = {
                                        'volunteer_id': app_data.get('volunteer_id'),
                                        'title': 'Application Status Update',
                                        'message': f"Your application for {event_data.get('title')} was not accepted at this time.",
                                        'timestamp': datetime.now(),
                                        'read': False,
                                        'type': 'application_rejected',
                                        'event_id': st.session_state['selected_event']
                                    }
                                    db.collection('notifications').add(notification_data)
                                    
                                    # Send rejection email
                                    from services.mail_service import EmailService
                                    email_service = EmailService()
                                    email_service.send_volunteer_rejection_notification(
                                        volunteer_email=app_data.get('volunteer_email'),
                                        volunteer_name=app_data.get('volunteer_name'),
                                        event_name=event_data.get('title'),
                                        org_name=st.session_state.get('org_name')
                                    )
                                    
                                    st.success("✅ Application rejected!")
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"❌ Error rejecting application: {str(e)}")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.error("❌ Event not found!")
        else:
            # Get all applications for organization's events
            events_ref = db.collection('events').where('org_id', '==', st.session_state['org_id']).stream()
            events_list = list(events_ref)
            
            if not events_list:
                st.info("🎯 No events created yet. Create your first event in the Events section!")
            else:
                for event in events_list:
                    event_data = event.to_dict()
                    applications = event_data.get('applications', [])
                    
                    if applications:
                        st.markdown(f"""
                            <div class="event-card">
                                <div class="event-title">🎯 {event_data.get('title', 'Event Title')}</div>
                                <div class="event-details">
                                    <p>📅 Date: {format_date(event_data.get('date'))}</p>
                                    <p>👥 Applications: {len(applications)}</p>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("👥 View Applications", key=f"view_apps_{event.id}"):
                            st.session_state.selected_event = event.id
                            st.experimental_rerun()
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                
                if not any(event.to_dict().get('applications', []) for event in events_list):
                    st.info("📭 No applications received yet for any events.")
                    
    except Exception as e:
        st.error(f"❌ Error loading applications: {str(e)}")

elif current_page == 'profile':
    st.subheader("👤 Organization Profile")
    try:
        # Get organization details
        org_ref = db.collection('organizations').document(st.session_state['org_id']).get()
        if org_ref.exists:
            org_data = org_ref.to_dict()
            
            # Create form for editing profile
            with st.form("edit_profile_form"):
                name = st.text_input("Organization Name", value=org_data.get('name', ''))
                email = st.text_input("Email", value=org_data.get('email', ''))
                phone = st.text_input("Contact Number", value=org_data.get('phone', ''))
                description = st.text_area("Description", value=org_data.get('description', ''))
                website = st.text_input("Website", value=org_data.get('website', ''))
                
                if st.form_submit_button("💾 Save Changes"):
                    try:
                        # Update organization details
                        db.collection('organizations').document(st.session_state['org_id']).update({
                            'name': name,
                            'email': email,
                            'phone': phone,
                            'description': description,
                            'website': website,
                            'updated_at': datetime.now()
                        })
                        st.success("✅ Profile updated successfully!")
                        st.session_state.org_name = name  # Update session state
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"❌ Error updating profile: {str(e)}")
        else:
            st.error("❌ Organization not found!")
    except Exception as e:
        st.error(f"❌ Error loading profile: {str(e)}")

elif current_page == 'notifications':
    st.subheader("🔔 Notifications")
    try:
        # Get notifications for organization's events
        notifications_ref = db.collection('notifications').where('org_id', '==', st.session_state['org_id']).stream()
        notifications_list = list(notifications_ref)
        
        # Get applications for organization's events
        applications_ref = db.collection('applications').where('org_id', '==', st.session_state['org_id']).where('status', '==', 'pending').stream()
        applications_list = list(applications_ref)
        
        if not notifications_list and not applications_list:
            st.info("📭 No notifications at the moment.")
        else:
            # Display pending applications first
            for application in applications_list:
                app_data = application.to_dict()
                event_ref = db.collection('events').document(app_data.get('event_id')).get()
                event_data = event_ref.to_dict() if event_ref.exists else {}
                
                st.markdown(f"""
                    <div class="event-card">
                        <div class="event-title">🔵 New Application</div>
                        <div class="event-details">
                            <p>👤 {app_data.get('volunteer_name')} has applied for {event_data.get('title', 'an event')}</p>
                            <p>📧 Email: {app_data.get('volunteer_email')}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Sort other notifications by timestamp in memory
            sorted_notifications = sorted(
                notifications_list,
                key=lambda x: x.to_dict().get('timestamp', MIN_DATETIME).replace(tzinfo=None) if x.to_dict().get('timestamp') and x.to_dict().get('timestamp').tzinfo else x.to_dict().get('timestamp', MIN_DATETIME),
                reverse=True
            )
            
            for notification in sorted_notifications:
                notif_data = notification.to_dict()
                # Format timestamp
                timestamp = notif_data.get('timestamp')
                if timestamp:
                    if isinstance(timestamp, datetime):
                        # Convert to naive datetime if it has timezone info
                        if timestamp.tzinfo is not None:
                            timestamp = timestamp.replace(tzinfo=None)
                        formatted_time = timestamp.strftime('%d-%m-%Y %H:%M:%S')
                    else:
                        formatted_time = str(timestamp)
                else:
                    formatted_time = 'Recent'
                
                # Mark notification as read
                if not notif_data.get('read', False):
                    db.collection('notifications').document(notification.id).update({'read': True})
                
                # Get notification status indicator
                status_icon = '🔵' if not notif_data.get('read', False) else '⚪'
                
                st.markdown(f"""
                    <div class="event-card">
                        <div class="event-title">{status_icon} {notif_data.get('title', 'Notification')}</div>
                        <div class="event-details">
                            <p>📝 {notif_data.get('message', '')}</p>
                            <p>⏰ {formatted_time}</p>
                            <p>🏷️ Type: {notif_data.get('type', 'general').replace('_', ' ').title()}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Error loading notifications: {str(e)}")

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
