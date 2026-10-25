import streamlit as st
import smtplib
import random
from email.mime.text import MIMEText
import time

# --- PAGE CONFIGURATION & CUSTOM CSS ---
st.set_page_config(page_title="GovTech Central", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
    div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white; border: none; border-radius: 8px; padding: 0.5rem 1rem;
        font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stButton"] button:hover {
        transform: translateY(-2px); box-shadow: 0 6px 12px rgba(99, 102, 241, 0.3);
    }
    .hero-text {
        font-size: 3rem; font-weight: 700; margin-bottom: 0px;
        background: -webkit-linear-gradient(45deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .sub-hero { color: #94a3b8; font-size: 1.2rem; font-weight: 300; margin-bottom: 2rem; }
    .closed-badge { background: #334155; color: white; padding: 4px 8px; border-radius: 6px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# --- MULTILINGUAL DICTIONARY ---
LANGUAGES = {
    "English": {
        "title": "GovTech Central",
        "subtitle": "Seamless, unified cross-departmental workflows.",
        "login": "🔒 Login",
        "signup": "📝 Sign Up",
        "email": "Email Address",
        "pass": "Password",
        "login_btn": "Login ➔",
        "forgot_btn": "Forgot Password?",
        "create_acc": "Create Account ➔",
        "my_apps": "📋 My Applications",
        "track_id": "🎯 Track Specific ID",
        "new_req": "✨ Create New Request",
        "app_name": "Applicant Name",
        "proj_title": "Project / Application Title",
        "loc": "Address / Location",
        "route_dept": "Routing Departments (Select Multiple)",
        "upload": "Upload Documents & Photos (PDF, JPG, PNG)",
        "submit": "Launch Request 🚀"
    },
    "Hindi": {
        "title": "गवर्नटेक सेंट्रल",
        "subtitle": "निर्बाध, एकीकृत क्रॉस-डिपार्टमेंटल वर्कफ़्लो।",
        "login": "🔒 लॉगिन",
        "signup": "📝 साइन अप",
        "email": "ईमेल पता",
        "pass": "पासवर्ड",
        "login_btn": "लॉगिन करें ➔",
        "forgot_btn": "पासवर्ड भूल गए?",
        "create_acc": "खाता बनाएं ➔",
        "my_apps": "📋 मेरे आवेदन",
        "track_id": "🎯 विशिष्ट आईडी ट्रैक करें",
        "new_req": "✨ नया अनुरोध बनाएं",
        "app_name": "आवेदक का नाम",
        "proj_title": "परियोजना / आवेदन शीर्षक",
        "loc": "पता / स्थान",
        "route_dept": "रूटिंग विभाग (कई चुनें)",
        "upload": "दस्तावेज़ और तस्वीरें अपलोड करें (PDF, JPG, PNG)",
        "submit": "अनुरोध सबमिट करें 🚀"
    }
}

with st.sidebar:
    st.write("### 🌐 Language / भाषा")
    selected_lang = st.selectbox("Select Language", ["English", "Hindi"], label_visibility="collapsed")
t = LANGUAGES[selected_lang]

# --- SECURITY FEATURE: STRICT DEPARTMENT MAPPING ---
AUTHORIZED_GOV_USERS = {
    "admin@gov.in": "System Admin (All)",
    "zoning@gov.in": "Zoning Board",
    "fire@gov.in": "Fire Safety",
    "water@gov.in": "Water & Sanitation",
    "health@gov.in": "Health Department",
    "police@gov.in": "City Police",
    "tax@gov.in": "Tax Authority",
    "jshaurya753@gmail.com": "System Admin (All)",
    "kavyaj8843@gmail.com": "Zoning Board" # Added your test email here
}

# --- EMAIL FUNCTIONS ---
def send_real_otp(receiver_email, otp_code):
    sender_email = "jshaurya753@gmail.com" # ⚠️ REPLACE THIS
    app_password = "rgbvxpuhiofvnnix" # ⚠️ REPLACE THIS
    msg = MIMEText(f"Your secure GovTech OTP is: {otp_code}")
    msg['Subject'] = 'GovTech Security Verification'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception:
        return False

def send_status_email(receiver_email, req_id, new_status):
    sender_email = "jshaurya753@gmail.com"
    app_password = "rgbvxpuhiofvnnix"
    action = "APPROVED ✅" if new_status == "Approved" else "REJECTED ❌"
    body = f"Hello,\n\nYour GovTech Service Request (ID: {req_id}) has been updated.\n\nOverall Status: {action}\n\nPlease log in to the portal for details."
    msg = MIMEText(body)
    msg['Subject'] = f'Update: {req_id} {action}'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception:
        return False

# --- SESSION STATE INITIALIZATION ---
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "kavyaj8843@gmail.com": {"password": "admin", "role": "Government Worker", "dept": "Zoning Board"},
        "admin@gov.in": {"password": "admin", "role": "Government Worker", "dept": "System Admin (All)"}
    }

# ADDED PRE-LOADED DUMMY DATA SO THE QUEUE IS NEVER BLANK ON STARTUP
if 'requests' not in st.session_state:
    st.session_state['requests'] = {
        "REQ-1024": {
            "citizen": "Demo Citizen", "citizen_email": "demo@gmail.com", 
            "type": "Commercial Shop License", "location": "Malviya Nagar, Jaipur", 
            "status": "Pending", "is_closed": False, 
            "files": [],
            "departments": {"Zoning Board": "Pending", "Tax Authority": "Pending"}
        }
    }

if 'auth_stage' not in st.session_state: st.session_state['auth_stage'] = 'step1_pass'
if 'temp_user_data' not in st.session_state: st.session_state['temp_user_data'] = {}
if 'user_role' not in st.session_state: st.session_state['user_role'] = None
if 'user_email' not in st.session_state: st.session_state['user_email'] = None
if 'worker_dept' not in st.session_state: st.session_state['worker_dept'] = None
if 'actual_otp' not in st.session_state: st.session_state['actual_otp'] = None

# --- AUTHENTICATION PIPELINE ---
if st.session_state['auth_stage'] != 'logged_in':
    st.markdown(f'<p class="hero-text">{t["title"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-hero">{t["subtitle"]}</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state['auth_stage'] == 'step1_pass':
            tab_login, tab_signup = st.tabs([t["login"], t["signup"]])
            
            with tab_login:
                log_email = st.text_input(t["email"], key="log_email")
                log_pass = st.text_input(t["pass"], type="password", key="log_pass")
                
                c1_log, c2_log = st.columns([1, 1])
                with c1_log:
                    if st.button(t["login_btn"]):
                        if log_email in st.session_state['users_db']:
                            if st.session_state['users_db'][log_email]['password'] == log_pass:
                                generated_otp = str(random.randint(100000, 999999))
                                st.session_state['actual_otp'] = generated_otp
                                with st.spinner("Sending 2FA Code..."):
                                    success = send_real_otp(log_email, generated_otp)
                                if success:
                                    st.session_state['temp_user_data'] = {
                                        'email': log_email, 'role': st.session_state['users_db'][log_email]['role'],
                                        'dept': st.session_state['users_db'][log_email].get('dept', None)
                                    }
                                    st.session_state['auth_stage'] = 'step2_otp'
                                    st.rerun()
                            else: st.error("Incorrect Password.")
                        else: st.error("Account not found.")
                with c2_log:
                    if st.button(t["forgot_btn"], type="secondary"):
                        st.session_state['auth_stage'] = 'forgot_pass_email'
                        st.rerun()

            with tab_signup:
                su_email = st.text_input(t["email"] + " ", key="su_email")
                su_pass = st.text_input(t["pass"] + " ", type="password", key="su_pass")
                su_role = "Citizen"
                su_dept = None
                
                if su_email:
                    if su_email in AUTHORIZED_GOV_USERS:
                        su_role = "Government Worker"
                        su_dept = AUTHORIZED_GOV_USERS[su_email]
                        st.info(f"🏛️ Government Email Recognized. Authorized for: **{su_dept}**")
                
                if st.button(t["create_acc"]):
                    if su_email in st.session_state['users_db']: st.error("Account exists.")
                    elif not su_email or not su_pass: st.error("Fill all fields.")
                    else:
                        st.session_state['users_db'][su_email] = {"password": su_pass, "role": su_role, "dept": su_dept}
                        generated_otp = str(random.randint(100000, 999999))
                        st.session_state['actual_otp'] = generated_otp
                        with st.spinner("Sending Email Verification Code..."):
                            success = send_real_otp(su_email, generated_otp)
                        if success:
                            st.session_state['temp_user_data'] = {'email': su_email, 'role': su_role, 'dept': su_dept}
                            st.session_state['auth_stage'] = 'step2_otp'
                            st.rerun()

        # STEP 2: OTP VERIFICATION
        elif st.session_state['auth_stage'] == 'step2_otp':
            st.write("### Two-Step Verification 🔐")
            st.info(f"OTP sent to **{st.session_state['temp_user_data']['email']}**")
            otp_input = st.text_input("Enter 6-digit OTP", type="password")
            if st.button("Verify & Enter Dashboard 🚀"):
                if otp_input == st.session_state['actual_otp']:
                    st.session_state['user_email'] = st.session_state['temp_user_data']['email']
                    st.session_state['user_role'] = st.session_state['temp_user_data']['role']
                    st.session_state['worker_dept'] = st.session_state['temp_user_data']['dept']
                    st.session_state['auth_stage'] = 'logged_in'
                    st.rerun()
                else: st.error("Invalid OTP.")
                
        # FORGOT PASSWORD FLOW
        elif st.session_state['auth_stage'] == 'forgot_pass_email':
            st.write("### Reset Password")
            fp_email = st.text_input("Enter your registered email address")
            c1_fp, c2_fp = st.columns([1, 1])
            with c1_fp:
                if st.button("Send Reset OTP 📧"):
                    if fp_email in st.session_state['users_db']:
                        generated_otp = str(random.randint(100000, 999999))
                        st.session_state['actual_otp'] = generated_otp
                        with st.spinner("Sending Reset Code..."):
                            success = send_real_otp(fp_email, generated_otp)
                        if success:
                            st.session_state['temp_user_data'] = {'email': fp_email}
                            st.session_state['auth_stage'] = 'forgot_pass_otp'
                            st.rerun()
                    else: st.error("Email not found.")
            with c2_fp:
                if st.button("Back to Login"):
                    st.session_state['auth_stage'] = 'step1_pass'
                    st.rerun()
                    
        elif st.session_state['auth_stage'] == 'forgot_pass_otp':
            st.info(f"OTP sent to **{st.session_state['temp_user_data']['email']}**")
            fp_otp = st.text_input("Enter 6-digit OTP", type="password")
            if st.button("Verify OTP ✔️"):
                if fp_otp == st.session_state['actual_otp']:
                    st.session_state['auth_stage'] = 'forgot_pass_reset'
                    st.rerun()
                else: st.error("Invalid OTP.")
                    
        elif st.session_state['auth_stage'] == 'forgot_pass_reset':
            new_pass = st.text_input("Enter New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            if st.button("Save New Password 💾"):
                if new_pass and new_pass == confirm_pass:
                    st.session_state['users_db'][st.session_state['temp_user_data']['email']]['password'] = new_pass
                    st.session_state['auth_stage'] = 'step1_pass'
                    st.rerun()
                else: st.error("Passwords do not match.")

# --- MAIN DASHBOARD (AFTER LOGIN) ---
else:
    col_logo, col_logout = st.columns([9, 1])
    with col_logo:
        st.markdown(f'<p class="hero-text" style="font-size: 2rem;">{t["title"]}</p>', unsafe_allow_html=True)
        dept_str = f" • {st.session_state['worker_dept']}" if st.session_state['worker_dept'] else ""
        st.caption(f"Logged in as **{st.session_state['user_role']}**{dept_str} ({st.session_state['user_email']})")
    with col_logout:
        st.write("") 
        if st.button("Log Out 🚪"):
            st.session_state['auth_stage'] = 'step1_pass'
            st.rerun()

    st.divider()

    # --- CITIZEN VIEW ---
    if st.session_state['user_role'] == "Citizen":
        tab1, tab2, tab3 = st.tabs([t["my_apps"], t["track_id"], t["new_req"]])
        
        with tab1:
            user_reqs = {k: v for k, v in st.session_state['requests'].items() if v.get('citizen_email') == st.session_state['user_email']}
            if not user_reqs: st.info("No applications found.")
            for req_id, req in user_reqs.items():
                with st.expander(f"{req_id} — {req['type']} | Status: {req['status']}"):
                    st.write(f"**Location:** {req.get('location', 'N/A')}")
                    for dept, status in req['departments'].items():
                        st.write(f"- **{dept}**: {status}")

        with tab2:
            st.markdown(f"### {t['track_id']}")
            req_id = st.text_input("Search Specific Tracking ID", placeholder="e.g., REQ-1024")
            if req_id:
                if req_id in st.session_state['requests']:
                    req = st.session_state['requests'][req_id]
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Applicant", req['citizen'])
                    c2.metric("Location", req.get('location', 'N/A'))
                    c3.metric("Overall Status", req['status'])
                    
                    st.markdown("#### Department Route")
                    for dept, status in req['departments'].items():
                        icon = "✅" if status == "Approved" else "❌" if status == "Rejected" else "⏳"
                        st.info(f"{icon} **{dept}**: {status}")
                else:
                    st.warning("Tracking ID not found.")

        with tab3:
            with st.form("citizen_submission_form"):
                cit_name = st.text_input(t["app_name"])
                req_type = st.text_input(t["proj_title"])
                location = st.text_input(t["loc"])
                
                target_depts = st.multiselect(t["route_dept"], ["Zoning Board", "Fire Safety", "Water & Sanitation", "Health Department", "City Police", "Tax Authority"])
                
                st.caption("💡 Tip: Hold **Ctrl** (Windows) or **Cmd** (Mac) in the file window to select multiple documents at once.")
                uploaded_files = st.file_uploader(t["upload"], type=['png', 'jpg', 'jpeg', 'pdf', 'docx'], accept_multiple_files=True)
                
                submit_btn = st.form_submit_button(t["submit"])
                
                if submit_btn:
                    if cit_name and req_type and location and target_depts:
                        new_id = f"REQ-{random.randint(1000,9999)}"
                        
                        file_data = []
                        if uploaded_files:
                            for file in uploaded_files:
                                file_data.append({"name": file.name, "type": file.type, "bytes": file.read()})
                                
                        st.session_state['requests'][new_id] = {
                            "citizen": cit_name, "citizen_email": st.session_state['user_email'],
                            "type": req_type, "location": location, "status": "Pending", "is_closed": False, 
                            "files": file_data,
                            "departments": {dept: "Pending" for dept in target_depts}
                        }
                        st.success(f"Application Initialized! Tracking ID: **{new_id}**")
                    else:
                        st.error("Please fill all fields and select at least one department.")

    # --- GOVERNMENT WORKER VIEW ---
    elif st.session_state['user_role'] == "Government Worker":
        my_dept = st.session_state['worker_dept']
        
        st.markdown("### Active Queue")
        relevant_reqs = {k: v for k, v in st.session_state['requests'].items() if (my_dept == "System Admin (All)" or my_dept in v['departments']) and not v.get('is_closed')}
        
        # ADDED: Failsafe text if the queue is empty
        if not relevant_reqs:
            st.info("No active requests currently in your queue. (Have a citizen submit one!)")
            
        for r_id, req in relevant_reqs.items():
            with st.expander(f"📄 {r_id} — {req['type']} | Status: {req['status']}"):
                st.write(f"**Applicant:** {req['citizen']} | **Location:** {req.get('location', 'N/A')}")
                
                if req.get('files'):
                    st.write("📎 **Attached Documents:**")
                    for file in req['files']:
                        if 'image' in file['type']:
                            st.image(file['bytes'], caption=file['name'], width=250)
                        else:
                            st.download_button(label=f"Download {file['name']}", data=file['bytes'], file_name=file['name'], mime=file['type'], key=f"dl_{r_id}_{file['name']}")
                
                new_dept = {}
                cols = st.columns(len(req['departments']))
                for idx, (dept, status) in enumerate(req['departments'].items()):
                    with cols[idx]:
                        if dept == my_dept or my_dept == "System Admin (All)":
                            opts = ["Pending", "In Progress", "Approved", "Rejected"]
                            new_dept[dept] = st.selectbox(f"{dept}", opts, index=opts.index(status), key=f"{r_id}_{dept}")
                        else:
                            st.write(f"**{dept}**"); st.caption(status)
                            new_dept[dept] = status 
                
                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("Commit Changes", key=f"save_{r_id}"):
                        st.session_state['requests'][r_id]['departments'] = new_dept
                        vals = new_dept.values()
                        new_overall = "Approved" if all(v == "Approved" for v in vals) else "Rejected" if "Rejected" in vals else "In Progress"
                        st.session_state['requests'][r_id]['status'] = new_overall
                        st.rerun()
                with c2:
                    if req['status'] in ["Approved", "Rejected"] and st.button("🔒 Close File", key=f"close_{r_id}"):
                        st.session_state['requests'][r_id]['is_closed'] = True
                        st.rerun()
