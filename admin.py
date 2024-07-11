import streamlit as st
from helperfunctions import *

def admin_dashboard(username):
    st.title("Admin Dashboard")
    # Add admin functionalities here, such as:
    # - Generating subscription keys
    # - Viewing all companies and their subscription status
    # - Managing other admins
    # etc.

    # Example: Generate Subscription Key
    tab1, tab2 = st.tabs(["Generate Subscription Key", "Subscription Keys"])
    with tab1:
        st.header("Generate Subscription Key")
        duration_options = ["3 Months", "6 Months", "1 Year", "Other"]
        duration = st.selectbox("Select Plan Duration", duration_options)
        # price = st.number_input("Enter Price", min_value=0.0, step=0.01)

        days = 0

        if duration == "Other":
            custom_days = st.number_input("Enter Custom Days", min_value=1, step=30)
            days = custom_days

        else:
            days = 90 if duration == "3 Months" else 180 if duration == "6 Months" else 365
        if st.button("Generate Key"):
            key = generate_subscription_key(days)
            st.success(f"Generated Subscription Key: {key}")
    with tab2:
        subscriptions = get_all_subscriptions()
    
        if subscriptions:
            # Convert to DataFrame
            df = pd.DataFrame(subscriptions, columns=['ID', 'Key', 'Duration (days)', 'Created At', 'Used At'])

            # Format the DataFrame
            df['Created At'] = pd.to_datetime(df['Created At'])
            df['Used At'] = pd.to_datetime(df['Used At'])

            # Display the DataFrame
            st.dataframe(df)

            # Optional: Add download button for CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Subscriptions CSV",
                data=csv,
                file_name="subscriptions.csv",
                mime="text/csv",
            )
        else:
            st.info("No subscription keys found.")

        # Add more admin functionalities as needed