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
    
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px; border-radius: 12px; backdrop-filter: blur(10px);
    }
    
    div[data-testid="stExpander"] {
        border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1);
        background-color: rgba(0, 0, 0, 0.2);
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

# --- SECURITY FEATURE: AUTHORIZED GOV EMAILS ---
# Any email in this list OR ending in @gov.in will automatically become a Govt Worker
AUTHORIZED_GOV_EMAILS = [
    "jshaurya753@gmail.com", 
    "mayor@city.gov"
]

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
    sender_email = "jshaurya753@gmail.com" # ⚠️ REPLACE THIS
    app_password = "rgbvxpuhiofvnnix" # ⚠️ REPLACE THIS
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
        "jshaurya753@gmail.com": {"password": "admin", "role": "Government Worker", "dept": "System Admin (All)"}
    }

if 'requests' not in st.session_state:
    st.session_state['requests'] = {
        "REQ-1024": {
            "citizen": "Alice Johnson", "citizen_email": "alice@gmail.com", 
            "type": "Residential Building Permit", "location": "Sector 4, Jaipur",
            "status": "In Progress", "is_closed": False, "has_proof": False, "proof_bytes": None, 
            "departments": {"Zoning Board": "Approved", "Fire Safety": "In Progress"}
        }
    }

if 'auth_stage' not in st.session_state: st.session_state['auth_stage'] = 'step1_pass'
if 'temp_user_data' not in st.session_state: st.session_state['temp_user_data'] = {}
if 'user_role' not in st.session_state: st.session_state['user_role'] = None
if 'user_email' not in st.session_state: st.session_state['user_email'] = None
if 'worker_dept' not in st.session_state: st.session_state['worker_dept'] = None
if 'actual_otp' not in st.session_state: st.session_state['actual_otp'] = None
if 'password_reset_success' not in st.session_state: st.session_state['password_reset_success'] = False

# --- AUTHENTICATION PIPELINE ---
if st.session_state['auth_stage'] != 'logged_in':
    st.markdown('<p class="hero-text">GovTech Central</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-hero">Seamless, unified cross-departmental workflows.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state['auth_stage'] == 'step1_pass':
            if st.session_state['password_reset_success']:
                st.success("✅ Password successfully reset. You may now log in.")
                st.session_state['password_reset_success'] = False
                
            tab_login, tab_signup = st.tabs(["🔒 Login", "📝 Sign Up"])
            
            with tab_login:
                st.write("### Access Your Account")
                log_email = st.text_input("Email Address", key="log_email")
                log_pass = st.text_input("Password", type="password", key="log_pass")
                
                c1_log, c2_log = st.columns([1, 1])
                with c1_log:
                    if st.button("Login ➔"):
                        if log_email in st.session_state['users_db']:
                            if st.session_state['users_db'][log_email]['password'] == log_pass:
                                generated_otp = str(random.randint(100000, 999999))
                                st.session_state['actual_otp'] = generated_otp
                                with st.spinner("Sending 2FA Code..."):
                                    success = send_real_otp(log_email, generated_otp)
                                if success:
                                    st.session_state['temp_user_data'] = {
                                        'email': log_email,
                                        'role': st.session_state['users_db'][log_email]['role'],
                                        'dept': st.session_state['users_db'][log_email].get('dept', None)
                                    }
                                    st.session_state['auth_stage'] = 'step2_otp'
                                    st.rerun()
                            else:
                                st.error("Incorrect Password.")
                        else:
                            st.error("Account not found. Please Sign Up.")
                with c2_log:
                    if st.button("Forgot Password?", type="secondary"):
                        st.session_state['auth_stage'] = 'forgot_pass_email'
                        st.rerun()

            with tab_signup:
                st.write("### Create New Account")
                su_email = st.text_input("Email Address", key="su_email")
                su_pass = st.text_input("Create Password", type="password", key="su_pass")
                
                # NEW: Automatically detect role based on the entered email
                su_role = "Citizen"
                su_dept = None
                
                if su_email:
                    if su_email in AUTHORIZED_GOV_EMAILS or su_email.endswith("@gov.in"):
                        su_role = "Government Worker"
                        st.info("🏛️ Government Account detected.")
                        su_dept = st.selectbox("Assign Department", [
                            "Zoning Board", "Fire Safety", "Water & Sanitation", 
                            "Health Department", "City Police", "Tax Authority", "System Admin (All)"
                        ])
                    else:
                        st.info("👤 Citizen Account detected.")
                
                if st.button("Create Account & Verify Email ➔"):
                    if su_email in st.session_state['users_db']:
                        st.error("An account with this email already exists. Please login.")
                    elif not su_email or not su_pass:
                        st.error("Please fill in all fields.")
                    else:
                        st.session_state['users_db'][su_email] = {
                            "password": su_pass, "role": su_role, "dept": su_dept
                        }
                        generated_otp = str(random.randint(100000, 999999))
                        st.session_state['actual_otp'] = generated_otp
                        
                        with st.spinner("Sending Email Verification Code..."):
                            success = send_real_otp(su_email, generated_otp)
                            
                        if success:
                            st.session_state['temp_user_data'] = {
                                'email': su_email, 'role': su_role, 'dept': su_dept
                            }
                            st.session_state['auth_stage'] = 'step2_otp'
                            st.success("Account created! Verifying email...")
                            st.rerun()

        # STEP 2: OTP VERIFICATION
        elif st.session_state['auth_stage'] == 'step2_otp':
            st.write("### Two-Step Verification 🔐")
            st.info(f"An authentication code has been sent to **{st.session_state['temp_user_data']['email']}**")
            
            otp_input = st.text_input("Enter 6-digit OTP", type="password", placeholder="••••••")
            
            c1_otp, c2_otp = st.columns([1, 1])
            with c1_otp:
                if st.button("Verify & Enter Dashboard 🚀"):
                    if otp_input == st.session_state['actual_otp']:
                        st.session_state['user_email'] = st.session_state['temp_user_data']['email']
                        st.session_state['user_role'] = st.session_state['temp_user_data']['role']
                        st.session_state['worker_dept'] = st.session_state['temp_user_data']['dept']
                        st.session_state['auth_stage'] = 'logged_in'
                        st.rerun()
                    else:
                        st.error("Invalid OTP.")
            with c2_otp:
                if st.button("Cancel & Go Back"):
                    st.session_state['auth_stage'] = 'step1_pass'
                    st.rerun()
                    
        # --- FORGOT PASSWORD FLOW ---
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
                    else:
                        st.error("Email not found in our system.")
            with c2_fp:
                if st.button("Back to Login"):
                    st.session_state['auth_stage'] = 'step1_pass'
                    st.rerun()
                    
        elif st.session_state['auth_stage'] == 'forgot_pass_otp':
            st.write("### Verify Email to Reset Password")
            st.info(f"OTP sent to **{st.session_state['temp_user_data']['email']}**")
            fp_otp = st.text_input("Enter 6-digit OTP", type="password")
            
            c1_fo, c2_fo = st.columns([1, 1])
            with c1_fo:
                if st.button("Verify OTP ✔️"):
                    if fp_otp == st.session_state['actual_otp']:
                        st.session_state['auth_stage'] = 'forgot_pass_reset'
                        st.rerun()
                    else:
                        st.error("Invalid OTP.")
            with c2_fo:
                if st.button("Cancel Reset"):
                    st.session_state['auth_stage'] = 'step1_pass'
                    st.rerun()
                    
        elif st.session_state['auth_stage'] == 'forgot_pass_reset':
            st.write("### Create New Password")
            st.write(f"Resetting password for: **{st.session_state['temp_user_data']['email']}**")
            new_pass = st.text_input("Enter New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            
            if st.button("Save New Password 💾"):
                if new_pass and new_pass == confirm_pass:
                    email_to_reset = st.session_state['temp_user_data']['email']
                    st.session_state['users_db'][email_to_reset]['password'] = new_pass
                    st.session_state['auth_stage'] = 'step1_pass'
                    st.session_state['password_reset_success'] = True
                    st.rerun()
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                else:
                    st.error("Password cannot be empty.")

# --- MAIN DASHBOARD (AFTER LOGIN) ---
else:
    col_logo, col_logout = st.columns([9, 1])
    with col_logo:
        st.markdown('<p class="hero-text" style="font-size: 2rem;">GovTech WorkSpace</p>', unsafe_allow_html=True)
        dept_str = f" • {st.session_state['worker_dept']}" if st.session_state['worker_dept'] else ""
        st.caption(f"Logged in as **{st.session_state['user_role']}**{dept_str} ({st.session_state['user_email']})")
    with col_logout:
        st.write("") 
        if st.button("Log Out 🚪"):
            st.session_state['auth_stage'] = 'step1_pass'
            for key in ['user_role', 'user_email', 'worker_dept', 'actual_otp', 'temp_user_data']:
                st.session_state[key] = None
            st.rerun()

    st.divider()

    # ==========================================
    #             CITIZEN VIEW
    # ==========================================
    if st.session_state['user_role'] == "Citizen":
        tab1, tab2, tab3 = st.tabs(["📋 My Applications", "🎯 Track Specific ID", "✨ Create New Request"])
        
        with tab1:
            st.markdown("### Your Submitted Requests")
            user_reqs = {k: v for k, v in st.session_state['requests'].items() if v.get('citizen_email') == st.session_state['user_email']}
            
            if not user_reqs:
                st.info("You haven't submitted any applications yet.")
            else:
                for req_id, req in user_reqs.items():
                    with st.expander(f"{req_id} — {req['type']} | Status: {req['status']}"):
                        st.write(f"**Location:** {req.get('location', 'N/A')}")
                        if req.get('is_closed'):
                            st.markdown('<span class="closed-badge">🔒 File Closed by Authority</span>', unsafe_allow_html=True)
                        st.markdown("#### Department Route")
                        for dept, status in req['departments'].items():
                            icon = "✅" if status == "Approved" else "❌" if status == "Rejected" else "⏳"
                            st.write(f"{icon} **{dept}**: {status}")

        with tab2:
            req_id = st.text_input("Search Specific Tracking ID", placeholder="e.g., REQ-1024")
            if req_id:
                if req_id in st.session_state['requests']:
                    req = st.session_state['requests'][req_id]
                    st.write(f"### {req['type']}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Applicant", req['citizen'])
                    c2.metric("Location", req.get('location', 'N/A'))
                    c3.metric("Overall Status", req['status'])
                    
                    if req.get('is_closed'):
                        st.warning("🔒 This file has been officially closed and archived.")
                        
                    st.markdown("#### Department Route")
                    for dept, status in req['departments'].items():
                        icon = "✅" if status == "Approved" else "❌" if status == "Rejected" else "⏳"
                        st.info(f"{icon} **{dept}**: {status}")
                else:
                    st.warning("Tracking ID not found.")

        with tab3:
            st.markdown("### Initialize New Clearance Workflow")
            with st.form("citizen_submission_form"):
                cit_name = st.text_input("Applicant Name")
                req_type = st.text_input("Project / Application Title")
                location = st.text_input("Address / Location")
                target_dept = st.selectbox("Primary Routing Department", [
                    "Zoning Board", "Fire Safety", "Water & Sanitation", 
                    "Health Department", "City Police", "Tax Authority"
                ])
                proof_file = st.file_uploader("Upload Supporting Documents (Images)", type=['png', 'jpg', 'jpeg'])
                submit_btn = st.form_submit_button("Launch Request 🚀")
                
                if submit_btn and cit_name and req_type and location:
                    new_id = f"REQ-{random.randint(1000,9999)}"
                    proof_bytes = proof_file.read() if proof_file else None
                    
                    st.session_state['requests'][new_id] = {
                        "citizen": cit_name, "citizen_email": st.session_state['user_email'],
                        "type": req_type, "location": location, "status": "Pending",
                        "is_closed": False, 
                        "has_proof": proof_file is not None, "proof_bytes": proof_bytes,
                        "departments": {target_dept: "Pending"}
                    }
                    st.success(f"Application Initialized! Tracking ID: **{new_id}**")

    # ==========================================
    #          GOVERNMENT WORKER VIEW
    # ==========================================
    elif st.session_state['user_role'] == "Government Worker":
        my_dept = st.session_state['worker_dept']
        
        relevant_reqs = {k: v for k, v in st.session_state['requests'].items() if my_dept == "System Admin (All)" or my_dept in v['departments']}
        active_reqs = {k: v for k, v in relevant_reqs.items() if not v.get('is_closed')}
        closed_reqs = {k: v for k, v in relevant_reqs.items() if v.get('is_closed')}
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Active Tasks", len(active_reqs))
        m2.metric("Archived Records", len(closed_reqs))
        m3.metric("Department", my_dept)
        
        tab_active, tab_closed = st.tabs(["🟢 Active Queue", "📁 Archived Records"])
        
        with tab_active:
            if not active_reqs: st.success("No active requests in queue.")
            for r_id, req in active_reqs.items():
                with st.expander(f"📄 {r_id} — {req['type']} | Status: {req['status']}"):
                    st.write(f"**Applicant:** {req['citizen']} ({req.get('citizen_email', 'No email')}) | **Location:** {req.get('location', 'N/A')}")
                    
                    if req.get('has_proof') and req.get('proof_bytes'):
                        st.image(req['proof_bytes'], caption="Attached Evidence", width=300)
                    
                    new_dept = {}
                    cols = st.columns(len(req['departments']))
                    for idx, (dept, status) in enumerate(req['departments'].items()):
                        with cols[idx]:
                            if dept == my_dept or my_dept == "System Admin (All)":
                                opts = ["Pending", "In Progress", "Approved", "Rejected"]
                                new_dept[dept] = st.selectbox(f"{dept}", opts, index=opts.index(status), key=f"{r_id}_{dept}")
                            else:
                                st.write(f"**{dept}**")
                                st.caption(f"Status: {status} (Read-Only)")
                                new_dept[dept] = status 
                    
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        if st.button("Commit Changes", key=f"save_{r_id}"):
                            old_overall = req['status']
                            st.session_state['requests'][r_id]['departments'] = new_dept
                            vals = new_dept.values()
                            new_overall = "Approved" if all(v == "Approved" for v in vals) else "Rejected" if "Rejected" in vals else "In Progress"
                            st.session_state['requests'][r_id]['status'] = new_overall
                            
                            if new_overall != old_overall and new_overall in ["Approved", "Rejected"] and req.get('citizen_email'):
                                send_status_email(req['citizen_email'], r_id, new_overall)
                            st.rerun()
                            
                    with c2:
                        if req['status'] in ["Approved", "Rejected"]:
                            if st.button("🔒 Close & Archive File", key=f"close_{r_id}", type="primary"):
                                st.session_state['requests'][r_id]['is_closed'] = True
                                st.rerun()

        with tab_closed:
            if not closed_reqs: st.info("No archived records found.")
            for r_id, req in closed_reqs.items():
                with st.expander(f"🔒 {r_id} — {req['type']} | Final Status: {req['status']}"):
                    st.write(f"**Applicant:** {req['citizen']} | **Location:** {req.get('location', 'N/A')}")
                    st.success("This file is permanently closed and locked from further edits.")
                    for dept, status in req['departments'].items():
                        st.write(f"- **{dept}**: {status}")