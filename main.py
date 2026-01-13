import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
# Replace this with your own phone number (Format: 601xxxx)
ADMIN_WHATSAPP = "60123456789" 
ADMIN_PASSWORD = "bola123"  # Change this to a secret password

# --- PAGE SETUP ---
st.set_page_config(page_title="KroniBola App", page_icon="⚽", layout="wide")
st.title("⚽ KroniBola Registration")

# --- CONNECT TO GOOGLE SHEETS ---
try:
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("KroniBola DB").worksheet("Registrations")
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")
    st.stop()

# --- SIDEBAR (ADMIN & INFO) ---
with st.sidebar:
    st.header("📋 Menu")
    mode = st.radio("Select Mode", ["Player Registration", "Admin Panel"])
    
    st.divider()
    st.info("ℹ️ Payments are non-refundable.")

# ==========================================
# MODE 1: PLAYER REGISTRATION
# ==========================================
if mode == "Player Registration":
    col1, col2 = st.columns([1, 2])
    
    # --- SECTION A: QR CODE ---
    with col1:
        st.subheader("Step 1: Pay Here")
        try:
            # Displays the image you uploaded to GitHub
            st.image("pay.jpg", caption="Scan with TNG/Bank App", width=250)
        except:
            st.warning("⚠️ Admin: Please upload 'pay.jpg' to GitHub.")

    # --- SECTION B: FORM ---
    with col2:
        st.subheader("Step 2: Register Details")
        with st.form("entry_form", clear_on_submit=True):
            player_name = st.text_input("Your Name / Nickname")
            session_date = st.date_input("Session Date")
            
            submitted = st.form_submit_button("✅ Register Now")

            if submitted and player_name:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Format: Date, Name, Status, Amount, Time
                row_data = [str(session_date), player_name, "Pending", "15", timestamp]
                sheet.append_row(row_data)
                
                st.success(f"Success! {player_name} is on the list.")
                
                # --- WHATSAPP LINK GENERATOR ---
                # Creates a pre-filled WhatsApp link
                msg = f"Hi Admin, I have registered for {session_date}. Here is my receipt for {player_name}."
                wa_link = f"https://wa.me/{ADMIN_WHATSAPP}?text={msg}"
                st.link_button("📤 Click here to Send Receipt on WhatsApp", wa_link)
                
            elif submitted:
                st.error("Please enter your name.")

    # --- SECTION C: PUBLIC LIST ---
    st.divider()
    st.subheader("📝 Registered Players")
    try:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            # Filter to show only Date, Name, Status
            public_df = df[["Session Date", "Player Name", "Payment Status"]]
            st.dataframe(public_df, use_container_width=True)
        else:
            st.info("No players yet.")
    except:
        st.write("List is empty.")

# ==========================================
# MODE 2: ADMIN PANEL (SECURE)
# ==========================================
elif mode == "Admin Panel":
    st.header("🔒 Admin Area")
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Access Granted")
        
        # Load Data
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        st.subheader("Manage Payments")
        st.write("Edit the 'Payment Status' below and click Save.")
        
        # 1. EDITABLE TABLE
        edited_df = st.data_editor(
            df, 
            num_rows="dynamic",
            column_config={
                "Payment Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Pending", "Paid", "Rejected"],
                    required=True
                )
            }
        )
        
        # 2. SAVE BUTTON
        if st.button("💾 Save Changes to Google Sheet"):
            # Clear old sheet and upload new data
            sheet.clear()
            # Add headers back
            sheet.append_row(df.columns.tolist())
            # Add new data
            sheet.append_rows(edited_df.values.tolist())
            st.toast("✅ Database Updated!")
            st.rerun()
            
    elif password:
        st.error("Wrong Password!")
