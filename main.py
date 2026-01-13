import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="Football Registration", page_icon="⚽")
st.title("⚽ Kajang Football Registration")

# --- CONNECT TO GOOGLE SHEETS ---
# We use st.secrets to keep your key safe
try:
    # UPDATED SCOPES (Fixes the 403 error)
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Open the sheet - MAKE SURE YOUR SHEET IS NAMED "KroniBola DB"
    sheet = client.open("KroniBola DB").worksheet("Registrations")

except Exception as e:
    st.error(f"Here is the real error: {e}")
    st.stop()

# --- THE REGISTRATION FORM ---
st.subheader("Join the next game!")

with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        player_name = st.text_input("Your Name")
    with col2:
        session_date = st.date_input("Session Date")
    
    # Simple dropdown for status
    status = "Pending"
    
    submitted = st.form_submit_button("⚽ Register Now")

    if submitted and player_name:
        # Prepare the row to add
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_data = [str(session_date), player_name, status, "15", timestamp]
        
        # Send to Google Sheet
        sheet.append_row(row_data)
        st.success(f"Nice! {player_name} is registered for {session_date}!")
    elif submitted and not player_name:
        st.warning("Please enter your name.")

# --- SHOW THE LIST ---
st.divider()
st.subheader("Current Player List")

# Fetch data and show it
try:
    all_data = sheet.get_all_records()
    if all_data:
        df = pd.DataFrame(all_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No players registered yet.")
except:
    st.info("List is empty or headers are missing in Sheet.")
