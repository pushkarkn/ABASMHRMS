import streamlit as st
from helperfunctions import *
from employee import employee_dashboard
from admin import admin_dashboard
from manager import manager_dashboard
from database import init_db
import time
import random
import secrets
import string

def main():
    st.set_page_config(page_title="HR Management System", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_type = None

    init_db()
    companies = get_companies()
    
    with st.container(border=False):
        col1, col2, col3 = st.columns([.5, 3, .5])
        with col1:
            st.write("")
        with col2:
            if not st.session_state.logged_in:
                st.markdown('<h1 class="auth-title">HR Management System</h1>', unsafe_allow_html=True)

                tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Admins"])

                with tab1:
                    user_type = st.selectbox("I am a", ["Employee", "HR Manager"], key="login_user_type")
                    company_names = [company[1] for company in companies]
                    selected_company = st.selectbox("Select Company", company_names, key="login_company")
                    username = st.text_input("Username", key="login_username")
                    password = st.text_input("Password", type="password", key="login_password")

                    if st.button("Log In"):
                        if user_type == "HR Manager":
                            login_successful = login_hr(username, password)
                        else:
                            login_successful = login_user(username, password)

                        if login_successful:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.user_type = user_type
                            st.success(f"Logged in as {user_type}: {username}")
                            st.experimental_rerun()
                        else:
                            st.error("Incorrect username or password")

                with tab2:
                    if 'signup_stage' not in st.session_state:
                        st.session_state.signup_stage = 'initial'
                
                    if st.session_state.signup_stage == 'initial':
                        user_type = st.selectbox("I want to register as", ["Employee", "HR Manager"], key="signup_user_type")
                        
                        if user_type == "HR Manager":
                            company_option = st.radio("Company", ["Existing Company", "New Company"])
                            if company_option == "Existing Company":
                                if companies:
                                    company_names = [company[1] for company in companies]
                                    selected_company = st.selectbox("Select Company", company_names, key="signup_company")
                                    company_id = next(company[0] for company in companies if company[1] == selected_company)
                                else:
                                    st.error("No existing companies. Please register a new company.")
                                    company_option = "New Company"
                            if company_option == "New Company":
                                new_company_name = st.text_input("New Company Name")
                                subscription_key = st.text_input("Enter Subscription Key")
                        else:
                            if companies:
                                company_names = [company[1] for company in companies]
                                selected_company = st.selectbox("Select Company", company_names, key="signup_company")
                                company_id = next(company[0] for company in companies if company[1] == selected_company)
                            else:
                                st.error("No companies available. Please contact an HR Manager to create a company first.")
                                st.stop()
                        
                        username = st.text_input("New Username", key="signup_username")
                        email = st.text_input("Email", key="signup_email")
                        password = st.text_input("New Password", type="password", key="signup_password")
                
                        if st.button("Register"):
                            if user_type == "HR Manager" and company_option == "New Company":
                                company_id, message = register_company_with_key(new_company_name, subscription_key)
                                if company_id is None:
                                    st.error("Company registration failed. Company name may already exist.")
                                    st.stop()
                            
                            # Check if username already exists
                            if user_exists(username):
                                st.error("Username already exists. Please choose a different username.")
                            else:
                                # Generate and send OTP
                                otp = generate_otp()
                                if send_otp_email(email, otp):
                                    st.session_state.otp = otp
                                    st.session_state.signup_stage = 'otp_verification'
                                    st.session_state.signup_data = {
                                        'user_type': user_type,
                                        'company_id': company_id,
                                        'username': username,
                                        'email': email,
                                        'password': password
                                    }
                                    st.success("OTP sent to your email. Please check and enter below.")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to send OTP. Please try again.")
                
                    elif st.session_state.signup_stage == 'otp_verification':
                        st.write("Please enter the OTP sent to your email.")
                        entered_otp = st.text_input("Enter OTP", key="entered_otp")

                        if st.button("Verify OTP"):
                            st.write(f"Stored OTP: {st.session_state.otp}")
                            st.write(f"Entered OTP: {entered_otp}")
                            if verify_otp(st.session_state.otp, entered_otp):
                                st.write("OTP verified successfully")
                                st.write(f"Debug: signup_data = {st.session_state.signup_data}")
                                # Perform registration
                                if st.session_state.signup_data['user_type'] == "HR Manager":
                                    success, message = register_hr(
                                        st.session_state.signup_data['username'],
                                        st.session_state.signup_data['password'],
                                        st.session_state.signup_data['company_id'],
                                        st.session_state.signup_data['email']
                                    )
                                else:
                                    success, message = register_user(
                                        st.session_state.signup_data['username'],
                                        st.session_state.signup_data['password'],
                                        st.session_state.signup_data['company_id'],
                                        st.session_state.signup_data['email']
                                    )

                                st.write(f"Registration result: {message}")

                                if success:
                                    st.success(f"{st.session_state.signup_data['user_type']} registered successfully!")
                                    st.session_state.logged_in = True
                                    st.session_state.username = st.session_state.signup_data['username']
                                    st.session_state.user_type = st.session_state.signup_data['user_type']
                                    st.session_state.signup_stage = 'initial'  # Reset for future signups
                                    del st.session_state.signup_data  # Clean up
                                    st.experimental_rerun()
                                else:
                                    st.error(f"Registration failed. Reason: {message}")
                            else:
                                st.error("Invalid OTP. Please try again.")
                
                        if st.button("Resend OTP"):
                            otp = generate_otp()
                            if send_otp_email(st.session_state.signup_data['email'], otp):
                                st.session_state.otp = otp
                                st.success("New OTP sent to your email. Please check and enter above.")
                            else:
                                st.error("Failed to send OTP. Please try again.")
                
                    # Add a way to go back to the initial signup stage
                    if st.session_state.signup_stage == 'otp_verification':
                        if st.button("Start Over"):
                            st.session_state.signup_stage = 'initial'
                            if 'signup_data' in st.session_state:
                                del st.session_state.signup_data
                            st.experimental_rerun()

                with tab3:

                    tab1, tab2 = st.tabs(["Admin Login", "Admin Signup"])

                    with tab1:
                        st.header("Admin Login")
                        admin_username = st.text_input("Admin Username", key="admin_username")
                        admin_password = st.text_input("Admin Password", type="password", key="admin_password")
                        if st.button("Login"):
                            if authenticate_admin(admin_username, admin_password):
                                st.session_state.logged_in = True
                                st.session_state.username = admin_username
                                st.session_state.user_type = "Admin"
                                st.success(f"Login successful!: {admin_username}")
                                st.experimental_rerun()
                            else:
                                st.error("Invalid admin username or password.")
                    with tab2:
                        st.header("Admin Signup")
                        admin_username = st.text_input("Admin Username ", key="admin_username ")
                        admin_password = st.text_input("Admin Password ", type="password", key="admin_password ")
                        if st.button("Signup"):
                            if create_initial_admin(admin_username, admin_password):
                                st.session_state.logged_in = True
                                st.session_state.username = admin_username
                                st.session_state.user_type = "Admin"
                                st.success(f"Signup successful!: {admin_username}")
                                st.experimental_rerun()
                            else:
                                st.error("Username already exists. Please choose a different username.")
                                
                st.markdown('</div>', unsafe_allow_html=True)

            else:
                st.title("HR Management System")
                st.write(f"Welcome, {st.session_state.username}")

                if st.sidebar.button("Logout"):
                    st.session_state.logged_in = False
                    st.session_state.username = None
                    st.session_state.user_type = None
                    st.experimental_rerun()

                if st.session_state.user_type == "HR Manager":
                    manager_dashboard(st.session_state.username)
                elif st.session_state.user_type == "Admin":
                    admin_dashboard(st.session_state.username)
                else:
                    employee_dashboard(st.session_state.username)
        with col3:
            st.write("")

if __name__ == "__main__":
    main()