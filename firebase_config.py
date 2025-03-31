import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st
import json

def initialize_firebase():
    """Initialize Firebase with credentials from JSON file"""
    try:
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            # Look for the service account file in the config directory
            cred_path = os.path.join(os.path.dirname(__file__), 'config', 'serviceAccountKey.json')
            
            if not os.path.exists(cred_path):
                st.error("""
                Firebase configuration file not found!
                
                Please follow these steps to set up Firebase:
                1. Go to Firebase Console (https://console.firebase.google.com)
                2. Select your project
                3. Go to Project Settings (⚙️ icon) > Service Accounts
                4. Click 'Generate New Private Key'
                5. Save the downloaded file as 'serviceAccountKey.json' in the 'config' directory
                """)
                return None
            
            try:
                # Try to load and validate the JSON file
                with open(cred_path, 'r') as f:
                    cred_json = json.load(f)
                
                # Verify required fields
                required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
                missing_fields = [field for field in required_fields if field not in cred_json]
                
                if missing_fields:
                    st.error(f"Missing required fields in serviceAccountKey.json: {', '.join(missing_fields)}")
                    return None
                
                # Ensure private_key is properly formatted
                if not cred_json['private_key'].startswith('-----BEGIN PRIVATE KEY-----'):
                    st.error("Invalid private key format in serviceAccountKey.json")
                    return None
                
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            
            except json.JSONDecodeError:
                st.error("Invalid JSON format in serviceAccountKey.json")
                return None
            except Exception as e:
                st.error(f"Error reading serviceAccountKey.json: {str(e)}")
                return None
        
        return firestore.client()
    except Exception as e:
        st.error(f"Error initializing Firebase: {str(e)}")
        return None

# Initialize Firestore database
db = initialize_firebase()
