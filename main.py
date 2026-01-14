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
    
    p, label, .stMarkdown, .stCaption, .stText {{ color: #E0E0E0 !important; }}
    
    .stTextInput input, .stDateInput input, .stTimeInput input {{
        background-color: #2D2D2D !important;
        color: white !important;
        border: 1px solid #555 !important;
    }}

    div.stButton > button {{
        background-color: {NEON_GREEN} !important;
        color: #000000 !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        border: 2px solid {NEON_GREEN} !important;
        width: 100%;
        transition: all 0.3s ease;
    }}
    
    div.stButton > button:hover {{
        background-color: black !important;
        color: {NEON_GREEN} !important;
        box-shadow: 0 0 15px {NEON_GREEN};
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
    # Open Sheets
    db = client.open("KroniBola DB")
    sheet_regs = db.worksheet("Registrations")
    sheet_config = db.worksheet("Config") # NEW SHEET
except Exception as e:
    st.error(f"⚠️ Error: Could not find 'Config' tab in Google Sheets. Please create it! Error: {e}")
    st.stop()

# --- HELPER: GET / SET CONFIG ---
def get_config():
    records = sheet_config.get_all_records()
    # Convert list of dicts to a single key-value dict
    config = {row['Key']: row['Value'] for row in records}
    return config

def update_config(name, date, time, loc, fee):
    # We just overwrite the cells B2:B6 directly for speed
    sheet_config.update_acell("B2", name)
    sheet_config.update_acell("B3", str(date)) # Ensure string
    sheet_config.update_acell("B4", str(time))
    sheet_config.update_acell("B5", loc)
    sheet_config.update_acell("B6", fee)

# --- LOAD CURRENT SESSION INFO ---
try:
    current_conf = get_config()
    SESSION_NAME = current_conf.get("Session Name", "Football")
    SESSION_DATE = current_conf.get("Date", "TBD")
    SESSION_TIME = current_conf.get("Time", "TBD")
    SESSION_LOC  = current_conf.get("Location", "TBD")
    SESSION_FEE  = current_conf.get("Fee", "15")
except:
    st.error("Config data format is wrong. Check headers 'Key' and 'Value' in Config tab.")
    st.stop()

# --- HEADER ---
st.title("KRONI BOLA")
st.write("___")

# --- SIDEBAR ---
with st.sidebar:
    st.header("MENU")
    mode = st.radio("Navigate", ["⚽ Register for Match", "📝 Player List", "🔒 Admin Panel"])
    
    # Show Session Info in Sidebar
    st.divider()
    st.caption("UPCOMING MATCH:")
    st.markdown(f"**{SESSION_NAME}**")
    st.markdown(f"📅 {SESSION_DATE}")
    st.markdown(f"⏰ {SESSION_TIME}")
    st.markdown(f"📍 {SESSION_LOC}")

# ==========================================
# PAGE 1: REGISTRATION (AUTO-FILLED)
# ==========================================
if mode == "⚽ Register for Match":
    st.subheader(f"NEXT MATCH: {SESSION_DATE}")
    
    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"#### 1. PAY: RM {SESSION_FEE}")
            try:
                st.image("pay.jpg", use_container_width=True)
            except:
                st.warning("Upload pay.jpg")
        with col2:
            st.markdown("#### 2. DETAILS")
            
            # DISPLAY MATCH INFO CARD
            st.info(f"📍 {SESSION_LOC} | ⏰ {SESSION_TIME}")
            
            with st.form("entry_form", clear_on_submit=True):
                player_name = st.text_input("Your Nickname")
                
                # Hidden Date Field (User doesn't pick anymore)
                st.caption(f"Registering for: {SESSION_NAME} ({SESSION_DATE})")
                
                st.write("") 
                submitted = st.form_submit_button("✅ CONFIRM SLOT")

                if submitted and player_name:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # Using the Global Session Date/Fee
                    row_data = [str(SESSION_DATE), player_name, "Pending", str(SESSION_FEE), timestamp]
                    sheet_regs.append_row(row_data)
                    st.success(f"DONE! {player_name} is in.")
                    
                    msg = f"Hi Admin, I registered for {SESSION_NAME} on {SESSION_DATE}. Name: {player_name}."
                    wa_link = f"https://wa.me/{ADMIN_WHATSAPP}?text={msg}"
                    st.link_button("📤 SEND RECEIPT (WHATSAPP)", wa_link)
                elif submitted:
                    st.error("Name Required")

# ==========================================
# PAGE 2: PLAYER LIST
# ==========================================
elif mode == "📝 Player List":
    st.subheader(f"LINEUP: {SESSION_DATE}")
    try:
        data = sheet_regs.get_all_records()
        if data:
            df = pd.DataFrame(data)
            
            # FILTER: Only show players for the CURRENT configured date
            # Convert both columns to string to ensure they match
            df['Session Date'] = df['Session Date'].astype(str)
            active_df = df[df['Session Date'] == str(SESSION_DATE)]
            
            display_df = active_df[["Player Name", "Payment Status", "Amount"]]
            
            def highlight_status(val):
                if val == 'Paid': return f'background-color: {NEON_GREEN}; color: black; font-weight: bold;'
                elif val == 'Pending': return 'background-color: #444; color: orange; font-weight: bold;'
                return ''

            if not display_df.empty:
                st.dataframe(display_df.style.applymap(highlight_status, subset=['Payment Status']), use_container_width=True)
                st.caption(f"Showing players for {SESSION_DATE} only.")
            else:
                st.info(f"No players registered for {SESSION_DATE} yet.")
        else:
            st.info("Database empty.")
    except Exception as e:
        st.write(f"Error loading list: {e}")

# ==========================================
# PAGE 3: ADMIN PANEL (MANAGE SESSION)
# ==========================================
elif mode == "🔒 Admin Panel":
    st.subheader("ADMIN ACCESS")
    password = st.text_input("Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("ACCESS GRANTED")
        
        tab_session, tab_players = st.tabs(["⚙️ MATCH SETTINGS", "👥 MANAGE PLAYERS"])
        
        # --- TAB 1: SET THE MATCH DETAILS ---
        with tab_session:
            st.markdown("### UPDATE UPCOMING MATCH")
            with st.form("config_form"):
                new_name = st.text_input("Session Name", value=SESSION_NAME)
                new_date = st.text_input("Date (YYYY-MM-DD)", value=SESSION_DATE)
                new_time = st.text_input("Time", value=SESSION_TIME)
                new_loc = st.text_input("Location", value=SESSION_LOC)
                new_fee = st.text_input("Fee (RM)", value=SESSION_FEE)
                
                if st.form_submit_button("💾 UPDATE SESSION INFO"):
                    update_config(new_name, new_date, new_time, new_loc, new_fee)
                    st.toast("Settings Updated! Reloading...", icon="🔄")
                    st.rerun()

        # --- TAB 2: MANAGE PLAYERS (DELETE/PAID) ---
        with tab_players:
            st.markdown("### PLAYER STATUS")
            data = sheet_regs.get_all_records()
            df = pd.DataFrame(data)
            
            # Filter for current date (Optional, or show all)
            # We show ALL here so you can clean up old data if needed
            
            if "Delete?" not in df.columns:
                df.insert(0, "Delete?", False)
            
            edited_df = st.data_editor(
                df, 
                num_rows="dynamic",
                column_config={
                    "Delete?": st.column_config.CheckboxColumn("Delete?", default=False),
                    "Payment Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Paid", "Rejected"], required=True)
                },
                use_container_width=True
            )
            
            if st.button("💾 SAVE PLAYER CHANGES"):
                rows_to_keep = edited_df[edited_df["Delete?"] == False]
                final_data = rows_to_keep.drop(columns=["Delete?"])
                sheet_regs.clear()
                sheet_regs.append_row(final_data.columns.tolist())
                sheet_regs.append_rows(final_data.values.tolist())
                st.toast("Database Updated!", icon="✅")
                st.rerun()
