import streamlit as st
import pandas as pd
import os
# import pdfkit
from datetime import datetime
from datetime import date 
from io import BytesIO
import base64
# -----------importing local files -----------
from helperfunctions import *
from html_contents import *
# --------------------------------------------

def manager_dashboard(username):
 
    st.title("Manager Dashboard")
    
    # Fetch all requests
    requests = fetch_all_employee_requests()
    # requests.reverse()
    tab1, tab2, tab3 = st.tabs(["Pending Leave Requests", "Employee Contract", "Employee Details"])

    with tab1:
        def display_pdf(pdf_data):
            if pdf_data:
                base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.write("No PDF available")
    
    #--------->
        # def generate_request_pdf(request_data, action):
        #     html_content = sick_leave_request_html(request_data, action)
        #     options = {
        #         'page-size': 'A4',
        #         'margin-top': '0.5in',
        #         'margin-right': '0.5in',
        #         'margin-bottom': '0.5in',
        #         'margin-left': '0.5in',
        #         'encoding': "UTF-8",
        #         'no-outline': None
        #     }
        #     pdf_data = pdfkit.from_string(html_content, False, options=options)
        #     return pdf_data
    #--------->

        def get_binary_file_downloader_html(bin_data, file_name='file.pdf', btn_label='Download PDF'):
            bin_str = base64.b64encode(bin_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_name}">{btn_label}</a>'
            return href

        # Display pending leave requests
        requests = fetch_all_employee_requests_under_me(username)
        if requests:
            st.write("### Pending Leave Requests")

            request_data = []
            for req in requests:
                status = get_leave_status(req[2], req[5], req[6], req[7])
                if status is None:
                    request_data.append({
                        "Name": req[1],
                        "Employee ID": req[2],
                        "Job Title": req[3],
                        "Leave Days": req[4],
                        "From": req[5],
                        "To": req[6],
                        "Leave Type": req[7],
                        "Reason": req[8],
                        "Main Type": req[9],
                        "Status": "Pending",
                        "Request ID": f"{req[2]}_{req[5]}_{req[6]}_{req[7]}",
                        "Appointment_from_date": req[10],
                        "Appointment_to_date": req[11],
                        "sick_from_date": req[12],
                        "sick_to_date": req[13],
                        "appointment_letter_PDF": req[14],
                        "sick_letter_PDF": req[15],
                        "other_reason": req[16]
                    })

            if request_data:
                for index, row in enumerate(request_data):
                    with st.container(border=True):
                        st.write(f"### {row['Name']}")
                        st.write(f"**Employee ID:** {row['Employee ID']}")
                        st.write(f"**Job Title:** {row['Job Title']}")
                        st.write(f"**Leave Type:** {row['Leave Type']}")
                        st.write(f"**From:** {row['From']} **To:** {row['To']}")
                        st.write(f"**Leave Days:** {row['Leave Days']}")
                        st.write(f"**Main Type:** {row['Main Type']}")

                        if row['Main Type'] == 'Appointment':
                            st.write(f"**Appointment From:** {row['Appointment_from_date']}")
                            st.write(f"**Appointment To:** {row['Appointment_to_date']}")
                            if row['appointment_letter_PDF']:
                                if st.button(f"View Appointment Letter for {row['Name']}", key=f"view_appointment_{index}"):
                                    display_pdf(row['appointment_letter_PDF'])

                        elif row['Main Type'] == 'Sick':
                            st.write(f"**Sick From:** {row['sick_from_date']}")
                            st.write(f"**Sick To:** {row['sick_to_date']}")
                            if row['sick_letter_PDF']:
                                if st.button(f"View Sick Leave Letter for {row['Name']}", key=f"view_sick_{index}"):
                                    display_pdf(row['sick_letter_PDF'])

                        elif row['Main Type'] == 'Other':
                            st.write("**Other Reason:**")
                            col1, col2 = st.columns(2)
                            with col1:
                                with st.container(height = 120, border=True):
                                    with st.container(border=True):
                                        st.write(row['other_reason'])

                        st.write("**Reason for leave:**")
                        col1, col2 = st.columns(2)
                        with col1:
                            with st.container(height = 120, border=True):
                                st.write(row['Reason'])

                        action_key = f"action_{index}"
                        action = st.radio(f"Choose an action for {row['Name']}:", ("Approve", "Reject"), key=action_key)
                        if st.button(f"Process Request for {row['Name']}", key=f"process_{index}"):
                            insert_leave_status(username, row["Name"], row["Employee ID"], action, row["From"], row["To"], row["Leave Type"])

                            pdf_path = generate_leave_request_pdf(row, action)
        
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="Download Leave Request PDF",
                                    data=pdf_file,
                                    file_name=f"Leave_Request_{row['Employee ID']}.pdf",
                                    mime="application/pdf"
                                )
                    



                            st.success(f"Leave request for {row['Name']} processed successfully.")
                        
                        #--------->
                            # pdf_content = generate_request_pdf(row, action)
                            # st.markdown(get_binary_file_downloader_html(pdf_content, f'Leave_Request_{row["Employee ID"]}.pdf', 'Download PDF'), unsafe_allow_html=True)
                        #--------->

                    st.write("---")
            else:
                st.info("No pending leave requests found.")
        else:
            st.info("No leave requests found.")


        st.write("**All Leave Requests**")

        with st.expander("View All Requests", expanded=False):
            all_requests = fetch_all_employee_requests_under_me(username)
            if all_requests:
                all_requests_reversed = all_requests[::-1]
                df = pd.DataFrame(all_requests_reversed, columns=[
                    "Username", "Name", "Employee ID", "Job Title", "Leave Days", 
                    "From Date", "To Date", "Leave Type", "Reason", "Main Type",
                    "Appointment From", "Appointment To", "Sick From", "Sick To", 
                    "Appointment Letter PDF", "Sick Letter PDF", "Other Reason"
                ])
                df = df.drop(['Appointment Letter PDF', 'Sick Letter PDF'], axis=1)

                st.dataframe(df)
            else:
                st.info("No requests found.")



        with tab2:
            st.header("Contract Details")
            first_party = st.text_input("Employer Name")
            second_party = st.text_input("Employee Name")
            date_of_contract = st.date_input("Date of Contract", value=datetime.today())
        
            st.header("Contract Terms")
            num_agreements = st.number_input("Number of Terms", min_value=1, value=5, step=1)
        
            agreements = []
            for i in range(num_agreements):
                agreement_content = st.text_area(f"Term {i + 1}", height=100)
                agreements.append({'content': agreement_content})
        
            if st.button("Generate Contract"):
                if all([first_party, second_party, date_of_contract]) and all(agreement['content'] for agreement in agreements):
                    pdf_path = generate_contract_pdf(agreements, first_party, second_party, date_of_contract)
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button("Download Employment Contract", pdf_file, "employment_contract.pdf")
                else:
                    st.error("Please fill in all required fields and ensure all terms have content.")

        with tab3:
            employee_usernames = get_employee_username_by_hr_username(username)
            if employee_usernames:
                st.write("Employees under your management:")
                for emp_username in employee_usernames:
                    st.write(f"- {emp_username}")
            else:
                st.write("No employees found under your management.")   