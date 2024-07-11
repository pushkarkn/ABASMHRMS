import streamlit as st
from helperfunctions import *
from datetime import date, datetime
import pandas as pd
import base64

def employee_dashboard(username):

    st.title("Employee Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["Vacation Leave Request","Absence Leave Request", "View Leave Status"])
    
    with tab1:
        # today_date = str(date.today().strftime("%Y-%m-%d"))
        today_date = str(date.today().strftime("%Y-%m-%d %A"))
        main_type = "Vacation Leave"
        left, right = st.columns(2, vertical_alignment="bottom")
        left.header("Vacation Leave Request")
        right.info(f"**{main_type} requesting on:** {today_date}")

        # name = st.text_input("Name")
        name = username
        st.write(f"**Name:** {username}")
        employee_id = st.text_input("Employee ID")
        job_title = st.text_input("Job title")
        leave_days = st.number_input("Leave request Days", min_value=1, value=1)
        from_date = st.date_input("Dates of absence: From")
        to_date = st.date_input("To")
        leave_type = st.selectbox("Type of leave", ["Paid Leave", "Unpaid Leave", "Other"])
        reason = st.text_area("Reason for the Leave")

        if st.button("Submit request"):
            insert_employee_request(username, name, employee_id, job_title, str(leave_days), str(from_date), str(to_date), leave_type, reason, main_type)
            st.success("Request submitted successfully")
    with tab2:
        today_date = str(date.today().strftime("%Y-%m-%d %A"))
        main_type = "Absence Leave"
        left, right = st.columns(2, vertical_alignment="bottom")
        left.header("Absence Leave Request")
        right.info(f"**{main_type} requesting on:** {today_date}")

        # name = st.text_input("Name ")
        name = username
        st.write(f"**Name:** {username}")
        employee_id = st.text_input("Employee ID ")
        job_title = st.text_input("Job title ")
        type_of_absence = st.selectbox("Type of Absence", ["Paid Leave", "Unpaid Leave", "Sick", "Appointment", "Other"])


        Appointment_from_date = None
        Appointment_to_date = None
        sick_from_date = None
        sick_to_date = None
        appointment_letter_PDF = None
        sick_letter_PDF = None
        other_reason = None

        if(type_of_absence == "Appointment"):
            st.write("Please provide the following Appointment information:")
            Appointment_from_date = st.date_input("Appointment from")
            Appointment_to_date = st.date_input("Appointment till")
            appointment_letter_PDF = st.file_uploader("Upload Appointment Letter")
        elif (type_of_absence == "Sick"):
            st.write("Please provide the following Sick information:")
            sick_from_date = st.date_input("Sick from")
            sick_to_date = st.date_input("Sick till")
            sick_letter_PDF = st.file_uploader("Upload Sick Letter")
        elif (type_of_absence == "Other"):
            st.write("Please provide the following Other information:")
            other_reason = st.text_area("Reason for the Absence")
        from_date = st.date_input("From ")
        to_date = st.date_input("To ")
        reason = st.text_area("Reason for the Absence ")

        if st.button("Submit request "):
            insert_employee_request(username, name, employee_id, job_title, "0", str(from_date), str(to_date), type_of_absence, reason, main_type, str(Appointment_from_date), str(Appointment_to_date), str(sick_from_date), str(sick_to_date), appointment_letter_PDF, sick_letter_PDF, other_reason)

            st.success("Request submitted successfully")
    with tab3:
        st.header("My Leave Requests")
        requests = fetch_all_employee_requests()
        my_requests = [req for req in requests if req[0] == username]
        my_requests.reverse()
        # st.write(requests)
        if my_requests:

            def get_pdf_download_link(pdf_data, filename):
                if pdf_data:
                    b64 = base64.b64encode(pdf_data).decode()
                    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download {filename}</a>'
                return None

            def get_pdf_display_html(pdf_data):
                if pdf_data:
                    b64 = base64.b64encode(pdf_data).decode()
                    pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="800" height="500" type="application/pdf"></iframe>'
                    return pdf_display
                return None
            

            for req in my_requests[:4]:
                with st.container(border=True):
                    status = get_leave_status(req[2], req[5], req[6], req[7])

                    def should_display(value):
                        return value is not None and value != "" and value != "None"

                    if should_display(req[1]):
                        st.write(f"**Request for: {req[1].strip()}**")

                    if should_display(req[9]):
                        st.write(f"**Request Type:** {req[9]}")

                    if should_display(req[5]) and should_display(req[6]):
                        st.write(f"**From: {req[5]} To: {req[6]}**")

                    if req[7] == "Appointment" and (should_display(req[10]) or should_display(req[11])):
                        st.write("**Appointment Details:**")
                        if should_display(req[10]):
                            st.write(f"From: {req[10]}")
                        if should_display(req[11]):
                            st.write(f"To: {req[11]}")
                        if should_display(req[14]):
                            pdf_html = get_pdf_display_html(req[14])
                            if pdf_html:
                                with st.expander("View Appointment Letter"):
                                    st.markdown(pdf_html, unsafe_allow_html=True)
                            else:
                                st.write("Appointment Letter: Not available")

                    if req[7] == "Sick" and (should_display(req[12]) or should_display(req[13])):
                        st.write("**Sick Leave Details:**")
                        if should_display(req[12]):
                            st.write(f"From: {req[12]}")
                        if should_display(req[13]):
                            st.write(f"To: {req[13]}")
                        if should_display(req[15]):
                            pdf_html = get_pdf_display_html(req[15])
                            if pdf_html:
                                with st.expander("View Sick Letter"):
                                    st.markdown(pdf_html, unsafe_allow_html=True)
                            else:
                                st.write("Sick Letter: Not available")

                    if should_display(req[8]):
                        st.write("**Reason:**")
                        with st.container(height=120, border=True):
                            st.write(req[8])

                    if req[9] == "VacationLeave" and should_display(req[4]):
                        st.write(f"**Leave Days:** {req[4]}")

                    if req[7] == "Appointment" and (should_display(req[10]) or should_display(req[11])):
                        st.write("**Appointment Details:**")
                        if should_display(req[10]):
                            st.write(f"From: {req[10]}")
                        if should_display(req[11]):
                            st.write(f"To: {req[11]}")
                        if should_display(req[14]):
                            pdf_link = get_pdf_download_link(req[14], "appointment_letter.pdf")
                            if pdf_link:
                                st.markdown(pdf_link, unsafe_allow_html=True)
                            else:
                                st.write("Appointment Letter: Not available")

                    if req[7] == "Sick" and (should_display(req[12]) or should_display(req[13])):
                        st.write("**Sick Leave Details:**")
                        if should_display(req[12]):
                            st.write(f"From: {req[12]}")
                        if should_display(req[13]):
                            st.write(f"To: {req[13]}")
                        if should_display(req[15]):
                            pdf_link = get_pdf_download_link(req[15], "sick_letter.pdf")
                            if pdf_link:
                                st.markdown(pdf_link, unsafe_allow_html=True)
                            else:
                                st.write("Sick Letter: Not available")

                    if req[7] == "Other" and should_display(req[16]):
                        st.write("**Other Reason:**")
                        st.write(req[16])

                    if status == "Approve":
                        st.write("**:green-background[Status: :green[Approved]]**")
                    elif status == "Reject":
                        st.write("**:red-background[Status: :red[Rejected]]**")
                    else:
                        st.write("**:orange-background[Status: :orange[Pending]]**")

            
            st.write("---")
            st.write("**My leave requests history**")
            history_data = []
            for req in my_requests:
                status = get_leave_status(req[2], req[5], req[6], req[7])
                history_data.append(tuple(req) + (status,))

            columns = [
                "Username", "Name", "Employee ID", "Job Title", "Leave Request Days",
                "From Date", "To Date", "Type of Leave", "Reason", "Main Type",
                "Appointment From Date", "Appointment To Date", "Sick From Date", "Sick To Date",
                "Appointment Letter PDF", "Sick Letter PDF", "Other Reason", "Leave Status"
            ]

            history_data = []
            for req in my_requests:
                status = get_leave_status(req[2], req[5], req[6], req[7])
                history_data.append(req + (status,))

            df = pd.DataFrame(history_data, columns=columns)
            df = df.drop(['Appointment Letter PDF', 'Sick Letter PDF'], axis=1)

            with st.expander("Click to see requests history"):
                st.dataframe(df, use_container_width=True)


        else:
            st.info("You haven't submitted any leave requests yet.")
            