import requests
import streamlit as st
from datetime import datetime, time
import time
import os
import bcrypt

from dotenv import load_dotenv
load_dotenv()

# METU
# LAMBDA_URL = "https://ngohy4i3pcv5j36nejdmjbcgpq0egfou.lambda-url.eu-central-1.on.aws/"

# Goaltech
LAMBDA_URL = "https://wrbpo5x2jap3crtgxxhpaxufdm0dacub.lambda-url.eu-central-1.on.aws/"

def get_ai_suggestion(user_text):
    payload = {
        "input": {
            "query": user_text
        }
    }
    try:
        response = requests.post(LAMBDA_URL, json=payload)
        response.raise_for_status()
        # Adjust 'text' key based on your actual Lambda JSON response structure
        return response.json().get("result", "AI Suggestion received, but output key was missing.")
    except Exception as e:
        return f"Error connecting to AI Agent: {e}"

# 1. Setup Page Config
st.set_page_config(page_title="MockMail", page_icon="📧", layout="wide")

# 2. Simple Authentication System
# Load credentials from environment variables or Streamlit secrets
def get_users_from_env():
    """Load user credentials from environment variables or Streamlit secrets."""
    users = {}
    
    # Try to get from Streamlit secrets first (for Streamlit Cloud)
    # Then fall back to os.environ (for local development)
    env_source = {}
    
    try:
        # Check if we're on Streamlit Cloud (secrets are available)
        if hasattr(st, 'secrets') and st.secrets:
            # Streamlit Cloud uses st.secrets which is a dict-like object
            for key in st.secrets.keys():
                if key.startswith('USER_'):
                    env_source[key] = st.secrets[key]
    except:
        pass
    
    # Also check os.environ (for local development or if secrets not available)
    for key in os.environ:
        if key.startswith('USER_') and key not in env_source:
            env_source[key] = os.environ[key]
    
    # Parse user data from environment variables
    # Format: USER_ADMIN_NAME, USER_ADMIN_EMAIL, USER_ADMIN_PASSWORD_HASH
    user_prefixes = set()
    for key in env_source:
        if key.startswith('USER_') and key.endswith('_NAME'):
            prefix = key.replace('_NAME', '')
            user_prefixes.add(prefix)
    
    for prefix in user_prefixes:
        username = prefix.replace('USER_', '').lower()
        name = env_source.get(f'{prefix}_NAME')
        email = env_source.get(f'{prefix}_EMAIL', '')
        password_hash = env_source.get(f'{prefix}_PASSWORD_HASH')
        
        if name and password_hash:
            users[username] = {
                'name': name,
                'email': email or '',
                'password_hash': password_hash
            }
    
    return users

# Load users from environment variables, fallback to default for development
USERS = get_users_from_env()

# Development fallback - only used if no environment variables are set
if not USERS:
    st.warning("⚠️ No users found in environment variables. Using development defaults.")
    # Use a fixed hash for development (password: password123)
    # This hash was generated once and is reused so the password always works
    # Hash for 'password123': $2b$12$eOE.V.ef3pL.ctWcUepXE.XegxGNQZGEbwBT03HPsOqDSvTvNHRCS
    default_hash = '$2b$12$eOE.V.ef3pL.ctWcUepXE.XegxGNQZGEbwBT03HPsOqDSvTvNHRCS'
    USERS = {
        'admin': {
            'password_hash': default_hash,
            'name': 'Admin User',
            'email': 'admin@metu.edu.tr'
        }
    }

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'name' not in st.session_state:
    st.session_state['name'] = None

# Authentication check
if not st.session_state['authenticated']:
    st.title("🔐 Login Required")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login")
        
        if submit:
            # Normalize username to lowercase for matching
            username_lower = username.lower().strip()
            
            if username_lower in USERS:
                # Verify password against stored hash
                stored_hash = USERS[username_lower]['password_hash']
                try:
                    # Try to verify the password
                    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username_lower
                        st.session_state['name'] = USERS[username_lower]['name']
                        st.success(f"Welcome, {USERS[username_lower]['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                except Exception as e:
                    st.error(f"Authentication error: {e}")
                    st.error(f"Debug: username='{username_lower}', hash exists={bool(stored_hash)}")
            else:
                st.error("Invalid username or password")
                st.error(f"Debug: Available usernames: {list(USERS.keys())}, entered: '{username_lower}'")
    
    st.stop()

# User is authenticated - show logout button and continue with app
with st.sidebar:
    st.write(f"Welcome *{st.session_state['name']}*")
    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        st.session_state['name'] = None
        st.rerun()

# 3. Initialize "Database" in Session State (only accessible after authentication)
if "outbox" not in st.session_state:
    st.session_state.outbox = []
if "selected_example" not in st.session_state:
    st.session_state.selected_example = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Compose"

# --- Sidebar Navigation ---
st.sidebar.title("📧 MockMail")
page_options = ["Compose", "Incoming", "About"]
try:
    page_index = page_options.index(st.session_state.current_page)
except ValueError:
    page_index = 0
page = st.sidebar.radio("Navigate", page_options, index=page_index)
st.session_state.current_page = page
st.sidebar.write("---")
st.sidebar.subheader("Example Questions")

# Define example questions
example_questions = [
    {
        "label": "Intructor Change",
        "to": "hotline@metu.edu.tr",
        "subject": "Intructor Change Request",
        "body": "Merhaba. Bu Dönem emekli olan bölümümüz hocalarından Prof.Dr. Ali Eryılmazın\nöğrencisi 2599686 numaralı öğrencisi Semra Sıkıra'ın Danışman değişikliği\nyapması gerekmektedir. Ali hocamız sisteme giremediği için öğrenciyi\nbırakamıyor. Nasıl yapabiliriz?\n\n\nKevser Özkan \n\n4049"
    },
    {
        "label": "VPN Connection Problem",
        "to": "hotline@metu.edu.tr",
        "subject": "VPN Connection Problem",
        "body": "Merhaba hocam,\n\nİyi günler, VPN indirdiğim masaüstü bilgisayarımda eklerde belirttiğim gibi bir uyarı alıyorum ve indirmek istediğim lisanslı uygulamaların olduğu “https:\/\/software.cc.metu.edu.tr\/download.php” linke ulaşamıyorum. VPN bağlandığı halde bu linke tıkladığımda güvenli bulunmadığından yine bağlanamıyorum. Yardımcı olursanız çok sevinirim.\n\nTeşekkürler,\nAzra"
    },
    {
        "label": "Internet Connection Problem",
        "to": "hotline@metu.edu.tr",
        "subject": "Internet Connection Problem",
        "body": "Merhaba hocam,\n\nİyi günler, eduroma nasıl bağlanabilirim? İyi çalışmalar, Mert Ali Yalçın"
    },
    {
        "label": "Academic Calendar",
        "to": "academic@metu.edu.tr",
        "subject": "Academic Calendar Request",
        "body": "Dear Academic Office,\n\nCould you please share the academic calendar for this academic year, including important dates for exams, holidays, and registration periods?\n\nBest regards."
    },
    {
        "label": "Library Access",
        "to": "library@metu.edu.tr",
        "subject": "Library Access and Resources",
        "body": "Hello,\n\nI would like to know about library access hours, online resources, and how to access digital databases. Could you provide this information?\n\nThank you."
    }
]

# Display example questions as buttons
for example in example_questions:
    if st.sidebar.button(example["label"], key=f"example_{example['label']}"):
        st.session_state.selected_example = example
        st.session_state.current_page = "Compose"
        st.rerun()


# --- Compose Page ---
if page == "Compose":
    st.header("Compose New Message")
    
    # Update session state with example values if an example was selected
    if st.session_state.selected_example:
        st.session_state.compose_to = st.session_state.selected_example["to"]
        st.session_state.compose_subject = st.session_state.selected_example["subject"]
        st.session_state.compose_body = st.session_state.selected_example["body"]
        # Clear the selected example after using it
        st.session_state.selected_example = None
    
    # Get default values from session state or use empty strings
    default_recipient = st.session_state.get("compose_to", "")
    default_subject = st.session_state.get("compose_subject", "")
    default_body = st.session_state.get("compose_body", "")
    
    with st.form("composer", clear_on_submit=True):
        recipient = st.text_input("To:", value=default_recipient, placeholder="example@email.com", key="compose_to")
        subject = st.text_input("Subject:", value=default_subject, placeholder="Hello!", key="compose_subject")
        body = st.text_area("Message:", value=default_body, placeholder="Type your message here...", height=200, key="compose_body")
        
        submit = st.form_submit_button("Send Message")
        
        if submit:
            # Get values from session state (form fields store values in session state when using keys)
            recipient_val = st.session_state.get("compose_to", "").strip()
            subject_val = st.session_state.get("compose_subject", "").strip()
            body_val = st.session_state.get("compose_body", "").strip()
            
            if recipient_val and subject_val and body_val:
                # Create the email object
                new_email = {
                    "to": recipient_val,
                    "subject": subject_val,
                    "body": body_val,
                    "time": datetime.now().strftime("%H:%M:%S")
                }
                # "Send" it by saving to our list
                st.session_state.outbox.append(new_email)
                # Clear the selected example after successful submission
                st.session_state.selected_example = None
                st.success(f"Message sent to {recipient_val}!")
            else:
                st.error("Please fill out all fields.")

# --- Sent Folder Page ---
elif page == "Incoming":
    st.header("Incoming Messages")
    
    if not st.session_state.outbox:
        st.info("Your inbox is empty.")
    else:
        # Display emails in reverse order (newest first)
        for idx, email in enumerate(reversed(st.session_state.outbox)):
            with st.expander(f"To: {email['to']} | {email['subject']} ({email['time']})"):
                st.write(f"**Subject:** {email['subject']}")
                st.write(f"**Body:**")
                st.info(email['body'])

                st.write("---")
                st.write("**✨ AI Suggestion:**")
                
                # Check if we already have the suggestion stored
                print("email", email)
                with st.spinner("Agent is thinking..."):
                    # Call your Lambda URL
                    suggestion = get_ai_suggestion(email['body'])
                    # Store it so it doesn't call the API again on next rerun
                    email["ai_hint"] = suggestion
                
                st.warning(email["ai_hint"])

                if st.button(f"Delete Message {idx}", key=f"del_{idx}"):
                    # Logic to remove could go here
                    pass

# --- About Page ---
else:
    st.header("About This App")
    st.write("This is a 'dummy' frontend application built with Streamlit.")