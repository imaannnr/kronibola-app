import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
ADMIN_WHATSAPP = "60126183827" 
ADMIN_PASSWORD = "bola123"      

# --- PAGE SETUP ---
st.set_page_config(page_title="KroniBola", page_icon="⚽", layout="centered")

# --- THEME COLORS ---
NEON_GREEN = "#CCFF00"
DARK_BG = "#121212"
CARD_BG = "#1E1E1E"

# --- CUSTOM CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {DARK_BG}; }}
    
    .css-1r6slb0, .css-keje6w, .stForm {{
        background-color: {CARD_BG};
        border: 1px solid #333;
        box-shadow: 0 4px 20px rgba(0,0,0,0.6);
        border-radius: 15px;
        padding: 20px;
    }}
    
    h1, h2, h3 {{
        color: {NEON_GREEN} !important;
        font-family: 'Arial Black', sans-serif;
        text-transform: uppercase;
    }}
    
    p, label, .stMarkdown, .stCaption {{ color: #E0E0E0 !important; }}
    
    .stTextInput input, .stDateInput input {{
        background-color: #2D2D2D !important;
        color: white !important;
        border: 1px solid #555 !important;
    }}

    div.stButton > button {{
        background-color: {NEON_GREEN} !important;
        color: #000000 !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        padding: 15px 30px !important;
        border-radius: 10px !important;
        border: 2px solid {NEON_GREEN} !important;
        text-transform: uppercase;
        width: 100%;
        box-shadow: 0 0 15px rgba(204, 255, 0, 0.4);
        transition: all 0.3s ease;
    }}
    
    div.stButton > button:hover {{
        background-color: black !important;
        color: {NEON_GREEN} !important;
        border: 2px solid {NEON_GREEN} !important;
        box-shadow: 0 0 25px rgba(204, 255, 0, 0.9);
        transform: scale(1.02);
    }}

    div.stLinkButton > a {{
        background-color: #25D366 !important;
        color: white !important;
        border: none;
        font-weight: bold;
        text-align: center;
        padding: 10px;
    }}
    
    [data-testid="stDataFrame"] {{ background-color: {CARD_BG}; }}
    </style>
""", unsafe_allow_html=True)

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

# --- HEADER ---
st.title("KRONI BOLA")
st.write("___")

# --- SIDEBAR ---
with st.sidebar:
    st.header("MENU")
    mode = st.radio("Navigate", ["⚽ New Registration", "📝 Player List", "🔒 Admin Panel"])

# ==========================================
# PAGE 1: REGISTRATION
# ==========================================
if mode == "⚽ New Registration":
    st.subheader("Join the Squad")
    
    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("#### 1. SCAN QR")
            try:
                st.image("pay.jpg", use_container_width=True)
            except:
                st.warning("Upload pay.jpg")
        with col2:
            st.markdown("#### 2. DETAILS")
            with st.form("entry_form", clear_on_submit=True):
                player_name = st.text_input("Your Nickname")
                session_date = st.date_input("Match Date")
                st.write("") 
                submitted = st.form_submit_button("✅ CONFIRM SLOT")

                if submitted and player_name:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    row_data = [str(session_date), player_name, "Pending", "15", timestamp]
                    sheet.append_row(row_data)
                    st.success(f"DONE! {player_name} is in.")
                    
                    msg = f"Hi Admin, I registered for {session_date}. Name: {player_name}."
                    wa_link = f"https://wa.me/{ADMIN_WHATSAPP}?text={msg}"
                    st.link_button("📤 SEND RECEIPT (WHATSAPP)", wa_link)
                elif submitted:
                    st.error("Name Required")

# ==========================================
# PAGE 2: PLAYER LIST
# ==========================================
elif mode == "📝 Player List":
    st.subheader("TEAM SHEET")
    try:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            display_df = df[["Session Date", "Player Name", "Payment Status"]]
            
            def highlight_status(val):
                if val == 'Paid': return f'background-color: {NEON_GREEN}; color: black; font-weight: bold;'
                elif val == 'Pending': return 'background-color: #444; color: orange; font-weight: bold;'
                return ''

            st.dataframe(display_df.style.applymap(highlight_status, subset=['Payment Status']), use_container_width=True)
        else:
            st.info("No players yet.")
    except:
        st.write("List is empty.")

# ==========================================
# PAGE 3: ADMIN PANEL (WITH DELETE)
# ==========================================
elif mode == "🔒 Admin Panel":
    st.subheader("ADMIN ACCESS")
    password = st.text_input("Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("ACCESS GRANTED")
        
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # 1. ADD "DELETE" COLUMN (Default False)
        if "Delete?" not in df.columns:
            df.insert(0, "Delete?", False)
        
        st.write("Tick 'Delete?' to remove a player, then click Save.")
        
        # 2. SHOW EDITOR
        edited_df = st.data_editor(
            df, 
            num_rows="dynamic",
            column_config={
                "Delete?": st.column_config.CheckboxColumn(
                    "Delete?",
                    help="Check this box to remove this player",
                    default=False,
                ),
                "Payment Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Pending", "Paid", "Rejected"],
                    required=True
                )
            },
            use_container_width=True
        )
        
        # 3. SAVE LOGIC
        if st.button("💾 SAVE CHANGES (DELETE CHECKED)"):
            # Filter OUT the rows where 'Delete?' is True
            rows_to_keep = edited_df[edited_df["Delete?"] == False]
            
            # Remove the 'Delete?' column before saving to Google Sheets
            # (Because Google Sheets doesn't need that column)
            final_data = rows_to_keep.drop(columns=["Delete?"])
            
            # Update Sheet
            sheet.clear()
            sheet.append_row(final_data.columns.tolist())
            sheet.append_rows(final_data.values.tolist())
            
            st.toast("Updated! Deleted rows removed.", icon="🗑️")
            st.rerun()
