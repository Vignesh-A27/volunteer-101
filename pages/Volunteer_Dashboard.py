import streamlit as st
from datetime import datetime, date, time
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Get the absolute path to the config directory
config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config'))
key_path = os.path.join(config_dir, 'demo.json')

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

def get_event_status(event_date, current_status='pending'):
    """Helper function to determine event status based on date"""
    current_status = current_status.lower()
    if current_status == 'rejected':
        return 'Rejected'
    elif current_status == 'approved':
        if event_date is None:
            return 'Approved'
        if isinstance(event_date, datetime):
            if event_date.tzinfo is not None:
                event_date = event_date.replace(tzinfo=None)
            if event_date < datetime.now():
                return 'Completed'
            return 'Approved'
    
    if event_date is None:
        return current_status.capitalize()
        
    if isinstance(event_date, datetime):
        if event_date.tzinfo is not None:
            event_date = event_date.replace(tzinfo=None)
        if event_date < datetime.now():
            return 'Completed'
    
    return current_status.capitalize()

# Initialize session state variables
if 'volunteer_id' not in st.session_state:
    st.session_state.volunteer_id = None
if 'volunteer_name' not in st.session_state:
    st.session_state.volunteer_name = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = "Feed"

# Page config
st.set_page_config(page_title="Volunteer Dashboard", layout="wide")

# Check authentication
if not st.session_state.get('authenticated') or st.session_state.get('user_type') != 'volunteer':
    st.error("⚠️ Please log in as a volunteer first!")
    st.switch_page("pages/Volunteer_Login.py")

if not st.session_state.get('volunteer_id'):
    st.error("⚠️ Volunteer ID not found. Please log in again!")
    st.switch_page("pages/Volunteer_Login.py")

# Custom CSS
st.markdown("""
    <style>
        .stApp {
            background: #FFFFFF !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #262626;
        }
        div[data-testid="stText"], div[data-testid="stMarkdown"] p {
            color: #262626 !important;
            font-size: 1rem !important;
        }
        .event-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid #E0E0E0;
            box-shadow: 0 2px 4px rgba(33, 150, 243, 0.1);
            transition: all 0.3s ease;
        }
        .event-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(33, 150, 243, 0.2);
        }
        .event-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
            color: #262626;
        }
        .event-details {
            color: #8e8e8e;
            font-size: 0.9rem;
        }
        [data-testid="stSidebar"] {
            background: white;
            border-right: 1px solid #E0E0E0;
        }
        [data-testid="stSidebarNav"] {
            color: #262626 !important;
        }
        [data-testid="stSidebarContent"] > div:not(:last-child) {
            margin-bottom: 1rem;
        }
        [data-testid="stMarkdownContainer"] {
            color: #262626 !important;
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
            box-shadow: 0 2px 4px rgba(33, 150, 243, 0.1);
        }
        .stButton button:hover {
            background: #1976D2 !important;
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(33, 150, 243, 0.2) !important;
        }
        .stTextInput input, .stTextArea textarea {
            border-radius: 6px !important;
            border: 1px solid #E0E0E0 !important;
            padding: 0.5rem !important;
            font-size: 0.9rem !important;
            color: #262626 !important;
            background-color: white !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #2196F3 !important;
            box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2) !important;
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



# Display welcome message
st.markdown("""
    <div style="text-align: center; padding: 2rem; background: white; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #dbdbdb;">
        <h1 style="color: #262626; font-size: 1.8rem; font-weight: 600;">👋 Welcome, {}</h1>
        <p style="color: #8e8e8e; font-size: 1rem;">Find and apply for volunteer opportunities that match your interests!</p>
    </div>
""".format(st.session_state.get('volunteer_name', 'Volunteer')), unsafe_allow_html=True)

# Initialize current page in session state if not exists
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'feed'

# Top Navigation
col1, col2, col3, col4, col5, col_space, col_logout = st.columns([1, 1, 1, 1, 1, 0.5, 1])

# Get current page from session state
current_page = st.session_state.current_page

with col1:
    if st.button("📰 Feed", key="nav_feed", use_container_width=True, type="primary" if st.session_state.current_page == 'feed' else "secondary"):
        st.session_state.current_page = 'feed'
        st.experimental_rerun()

with col2:
    if st.button("📅 My Events", key="nav_events", use_container_width=True, type="primary" if st.session_state.current_page == 'my_events' else "secondary"):
        st.session_state.current_page = 'my_events'
        st.experimental_rerun()

with col3:
    if st.button("🔍 Search", key="nav_search", use_container_width=True, type="primary" if st.session_state.current_page == 'search' else "secondary"):
        st.session_state.current_page = 'search'
        st.experimental_rerun()

with col4:
    if st.button("👤 Profile", key="nav_profile", use_container_width=True, type="primary" if st.session_state.current_page == 'profile' else "secondary"):
        st.session_state.current_page = 'profile'
        st.experimental_rerun()

with col5:
    if st.button("🔔 Notifications", key="nav_notif", use_container_width=True, type="primary" if st.session_state.current_page == 'notifications' else "secondary"):
        st.session_state.current_page = 'notifications'
        st.experimental_rerun()

with col_logout:
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/Volunteer_Login.py")

st.markdown("<br>", unsafe_allow_html=True)

if current_page == 'my_events':
    st.subheader("📅 My Events")
    try:
        # Fetch user's applications
        applications_ref = db.collection('applications').where('volunteer_id', '==', st.session_state.volunteer_id).get()
        
        if not applications_ref:
            st.info("🎯 You haven't applied to any events yet! 🔍")
        else:
            applications_list = []
            for app in applications_ref:
                app_data = app.to_dict()
                event_ref = db.collection('events').document(app_data['event_id']).get()
                if event_ref.exists:
                    event_data = event_ref.to_dict()
                    event_date = event_data.get('date')
                    current_status = app_data.get('status', 'Pending')
                    applications_list.append({
                        'event_title': app_data.get('event_title', 'Unknown Event'),
                        'event_date': format_date(event_date),
                        'event_location': event_data.get('location', 'No location'),
                        'org_name': app_data.get('organization_name', 'Unknown Organization'),
                        'status': get_event_status(event_date, current_status),
                        'applied_at': format_date(app_data.get('applied_at'))
                    })
            
            # Sort applications by date
            sorted_applications = sorted(
                applications_list,
                key=lambda x: x['event_date'],
                reverse=True
            )
            
            # Display applications
            for app in sorted_applications:
                with st.container():
                    st.markdown(f"""
                    <div class="event-card">
                        <div class="event-title">{app['event_title']}</div>
                        <div class="event-details">
                            <p>🏢 <strong>Organization:</strong> {app['org_name']}</p>
                            <p>📍 <strong>Location:</strong> {app['event_location']}</p>
                            <p>📅 <strong>Event Date:</strong> {app['event_date']}</p>
                            <p>📝 <strong>Applied On:</strong> {app['applied_at']}</p>
                            <p>✨ <strong>Status:</strong> {app['status']}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.divider()
    except Exception as e:
        st.error(f"❌ Error loading events: {str(e)}")
    except Exception as e:
        st.error(f"Error loading applications: {str(e)}")

elif current_page == 'feed':
    st.subheader("📰 Event Feed")
    try:
        # Fetch all events
        events_ref = db.collection('events').stream()
        events_list = list(events_ref)
        
        if not events_list:
            st.info("🎯 No events available at the moment. Check back later!")
        else:
            # Filter out past events and sort remaining events by date
            current_events = []
            for event in events_list:
                event_data = event.to_dict()
                event_date = event_data.get('date')
                
                # Skip events that have already ended
                if event_date and isinstance(event_date, datetime):
                    if event_date.tzinfo is not None:
                        event_date = event_date.replace(tzinfo=None)
                    if event_date < datetime.now():
                        continue
                
                current_events.append(event)
            
            # Sort events by date
            sorted_events = sorted(
                current_events,
                key=lambda x: get_event_date(x),
                reverse=True
            )
            
            if not current_events:
                st.info("🎯 No upcoming events available at the moment. Check back later!")
            else:
                for event in sorted_events:
                    event_data = event.to_dict()
                    org_id = event_data.get('org_id')
                    org_name = get_org_name(org_id)
                    
                    st.markdown(f"""
                        <div class=\"event-card\">
                            <div class=\"event-title\">🎯 {event_data.get('title', 'Event Title')}</div>
                            <div class=\"event-details\">
                                <p>🏢 Organization: {org_name}</p>
                                <p>📅 Date: {format_date(event_data.get('date', ''))}</p>
                                <p>📍 Location: {event_data.get('location', 'Location TBD')}</p>
                                <p>👥 Volunteers Needed: {event_data.get('required_volunteers', 'Not specified')}</p>
                                <p>🔧 Required Skills: {', '.join(event_data.get('skills_required', ['No specific skills required']))}</p>
                                <p>📝 Description: {event_data.get('description', 'No description available.')}</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Generate a unique key for each apply button
                    unique_key = f"feed_apply_{event.id}_{st.session_state.volunteer_id}"
                    
                    if st.button(f"Apply for {event_data.get('title', 'Event')}", key=unique_key):
                        try:
                            # Check if already applied
                            application_ref = db.collection('applications').where('event_id', '==', event.id).where('volunteer_id', '==', st.session_state.volunteer_id).get()
                            
                            if not application_ref:
                                # Create application with timestamp
                                application_data = {
                                    'event_id': event.id,
                                    'volunteer_id': st.session_state.volunteer_id,
                                    'volunteer_name': st.session_state.volunteer_name,
                                    'volunteer_email': st.session_state.volunteer_email,
                                    'event_title': event_data.get('title', 'Untitled Event'),
                                    'org_id': org_id,
                                    'organization_name': org_name,
                                    'status': 'pending',
                                    'applied_at': datetime.now()
                                }
                                db.collection('applications').add(application_data)
                                
                                # Send confirmation email
                                from services.mail_service import EmailService
                                email_service = EmailService()
                                email_service.send_event_registration_confirmation(
                                    volunteer_email=st.session_state.volunteer_email,
                                    volunteer_name=st.session_state.volunteer_name,
                                    event_data=event_data,
                                    org_name=org_name
                                )
                                
                                # Send notification to organization
                                email_service.send_organization_event_notification(
                                    org_email=event_data.get('org_email'),
                                    volunteer_name=st.session_state.volunteer_name,
                                    event_name=event_data.get('title'),
                                    action='applied'
                                )
                                
                                st.success("Successfully applied for the event!")
                            else:
                                st.warning("You have already applied for this event.")
                        except Exception as e:
                            st.error(f"Error applying for event: {str(e)}")
    except Exception as e:
        st.error(f"❌ Error loading events: {str(e)}")

elif current_page == 'search':
    st.subheader("🔍 Search Events")
    search_query = st.text_input("🔎 Search for events", key=f"search_events_input_{st.session_state.volunteer_id}_{current_page}")
    if search_query:
        try:
            # Simple search implementation
            events_ref = db.collection('events').stream()
            found_events = False
            for event in events_ref:
                event_data = event.to_dict()
                if search_query.lower() in event_data.get('title', '').lower() or search_query.lower() in event_data.get('description', '').lower():
                    found_events = True
                    
                    # Get organization name
                    org_id = event_data.get('org_id')
                    org_name = "Unknown Organization"
                    if org_id:
                        try:
                            org_ref = db.collection('organizations').document(org_id).get()
                            if org_ref.exists:
                                org_data = org_ref.to_dict()
                                org_name = org_data.get('name', 'Unknown Organization')
                        except Exception as e:
                            st.error(f"❌ Error fetching organization details: {str(e)}")
                    
                    st.markdown(f"""
                        <div class="event-card">
                            <div class="event-title">🎯 {event_data.get('title', 'Event Title')}</div>
                            <div class="event-details">
                                <p>🏢 Organization: {org_name}</p>
                                <p>📅 Date: {format_date(event_data.get('date', ''))}</p>
                                <p>📍 Location: {event_data.get('location', 'Location TBD')}</p>
                                <p>📝 Description: {event_data.get('description', 'No description available.')}</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Apply for {event_data.get('title', 'Event')}", key=f"search_apply_{event.id}_{st.session_state.volunteer_id}_{current_page}"):
                        try:
                            # Check if already applied
                            application_ref = db.collection('applications').where('event_id', '==', event.id).where('volunteer_id', '==', st.session_state.volunteer_id).get()
                            
                            if not application_ref:
                                # Create application
                                application_data = {
                                    'event_id': event.id,
                                    'volunteer_id': st.session_state.volunteer_id,
                                    'volunteer_name': st.session_state.volunteer_name,
                                    'volunteer_email': st.session_state.volunteer_email,
                                    'event_title': event_data.get('title', 'Untitled Event'),
                                    'org_id': org_id,
                                    'organization_name': org_name,
                                    'status': 'pending',
                                    'applied_at': datetime.now()  # This will be timezone naive
                                }
                                
                                # Add application to database
                                db.collection('applications').add(application_data)

                                # Send confirmation email
                                try:
                                    from services.mail_service import MailService
                                    mail_service = MailService()
                                    mail_service.send_event_registration_confirmation(
                                        volunteer_email=st.session_state.volunteer_email,
                                        volunteer_name=st.session_state.volunteer_name,
                                        event_data=event_data,
                                        org_name=org_name
                                    )
                                except Exception as e:
                                    st.warning(f"⚠️ Application submitted but email notification failed: {str(e)}")
                                
                                # Create notification for organization
                                notification_data = {
                                    'org_id': org_id,
                                    'title': 'New Volunteer Application',
                                    'message': f"{st.session_state.volunteer_name} has applied for {event_data.get('title', 'Untitled Event')}",
                                    'timestamp': datetime.now(),
                                    'read': False,
                                    'type': 'new_application',
                                    'event_id': event_id
                                }
                                
                                db.collection('notifications').add(notification_data)
                                st.success("✅ Application submitted successfully!")
                            else:
                                st.warning("⚠️ You have already applied for this event")
                        except Exception as e:
                            st.error(f"❌ Error applying for event: {str(e)}")
            
            if not found_events:
                st.info("🔍 No events found matching your search.")
                
        except Exception as e:
            st.error(f"❌ Error searching events: {str(e)}")

elif current_page == 'profile':
    st.subheader("👤 My Profile")
    try:
        # Fetch volunteer profile
        volunteer_ref = db.collection('volunteers').document(st.session_state.volunteer_id).get()
        if volunteer_ref.exists:
            volunteer_data = volunteer_ref.to_dict()

            
            with st.form(f"update_profile_form_{st.session_state.volunteer_id}"):
                st.markdown("### 👤 Personal Information")
                name = st.text_input("📛 Full Name", value=volunteer_data.get('name', ''), key=f"profile_name_{st.session_state.volunteer_id}")
                email = st.text_input("📧 Email", value=volunteer_data.get('email', ''), disabled=True, key=f"profile_email_{st.session_state.volunteer_id}")
                phone = st.text_input("📱 Phone Number", value=volunteer_data.get('phone', ''), key=f"profile_phone_{st.session_state.volunteer_id}")
                
                st.markdown("### ℹ️ Additional Information")
                bio = st.text_area("📝 Bio", value=volunteer_data.get('bio', ''), key=f"profile_bio_{st.session_state.volunteer_id}")
                # Organize skills into categories
                st.markdown("#### 🎯 Skills & Expertise")
                leadership_skills = st.multiselect(
                    "Leadership & Management",
                    ["Team Leadership", "Event Planning", "Project Management", "Conflict Resolution", "Decision Making", "Fundraising"],
                    default=[skill for skill in volunteer_data.get('skills', []) if skill in ["Team Leadership", "Event Planning", "Project Management", "Conflict Resolution", "Decision Making", "Fundraising"]],
                    key=f"profile_leadership_skills_{st.session_state.volunteer_id}"
                )
                communication_skills = st.multiselect(
                    "Communication & Media",
                    ["Public Speaking", "Writing", "Social Media", "Photography", "Videography", "Translation", "Sign Language"],
                    default=[skill for skill in volunteer_data.get('skills', []) if skill in ["Public Speaking", "Writing", "Social Media", "Photography", "Videography", "Translation", "Sign Language"]],
                    key=f"profile_communication_skills_{st.session_state.volunteer_id}"
                )
                teaching_skills = st.multiselect(
                    "Education & Training",
                    ["Teaching", "Tutoring", "Mentoring", "Curriculum Development", "Special Education", "ESL Teaching"],
                    default=[skill for skill in volunteer_data.get('skills', []) if skill in ["Teaching", "Tutoring", "Mentoring", "Curriculum Development", "Special Education", "ESL Teaching"]],
                    key=f"profile_teaching_skills_{st.session_state.volunteer_id}"
                )
                technical_skills = st.multiselect(
                    "Technical & Professional",
                    ["First Aid", "CPR", "IT Support", "Web Development", "Data Analysis", "Graphic Design", "Legal Knowledge"],
                    default=[skill for skill in volunteer_data.get('skills', []) if skill in ["First Aid", "CPR", "IT Support", "Web Development", "Data Analysis", "Graphic Design", "Legal Knowledge"]],
                    key=f"profile_technical_skills_{st.session_state.volunteer_id}"
                )
                support_skills = st.multiselect(
                    "Support & Care",
                    ["Counseling", "Elder Care", "Child Care", "Animal Care", "Crisis Support", "Mental Health Support"],
                    default=[skill for skill in volunteer_data.get('skills', []) if skill in ["Counseling", "Elder Care", "Child Care", "Animal Care", "Crisis Support", "Mental Health Support"]],
                    key=f"profile_support_skills_{st.session_state.volunteer_id}"
                )
                
                # Combine all skills
                skills = leadership_skills + communication_skills + teaching_skills + technical_skills + support_skills
                
                if st.form_submit_button("💾 Update Profile"):
                    try:
                        # Update profile in Firestore
                        db.collection('volunteers').document(st.session_state.volunteer_id).update({
                            'name': name,
                            'phone': phone,
                            'bio': bio,
                            'skills': skills,
                            'updated_at': datetime.now()
                        })
                        st.success("✅ Profile updated successfully!")
                        st.session_state.volunteer_name = name
                    except Exception as e:
                        st.error(f"❌ Error updating profile: {str(e)}")
    except Exception as e:
        st.error(f"❌ Error loading profile: {str(e)}")

elif current_page == 'notifications':
    st.subheader("🔔 Notifications")
    try:
        # Fetch notifications without ordering in the query
        notifications_ref = db.collection('notifications').where('volunteer_id', '==', st.session_state.volunteer_id).stream()
        notifications_list = list(notifications_ref)
        
        if not notifications_list:
            st.info("📭 No notifications at the moment.")
        else:
            # Sort notifications by timestamp in memory
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

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
