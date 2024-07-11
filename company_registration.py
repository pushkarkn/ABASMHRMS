import streamlit as st
from helperfunctions import *

def company_registration_dashboard():
    st.header("Company Registration")
    
    company_name = st.text_input("Company Name")
    hr_username = st.text_input("HR Username")
    hr_password = st.text_input("HR Password", type="password")
    subscription_key = st.text_input("Subscription Key")
    
    if st.button("Register Company"):
        company_id, message = register_company_with_key(company_name, subscription_key)
        if company_id:
            if register_hr(hr_username, hr_password, company_id):
                st.success("Company and HR registered successfully!")
                if st.button("Complete Registration"):
                    if login_hr(hr_username, hr_password):
                        st.session_state.logged_in = True
                        st.session_state.username = hr_username
                        st.session_state.user_type = "HR"
                        st.experimental_rerun()
            else:
                st.error("HR registration failed. Username may already exist.")
        else:
            st.error(f"Company registration failed. {message}")