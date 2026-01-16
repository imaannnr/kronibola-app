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
TNG_BLUE = "#005EB8" # TNG Corporate Color

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
    
    h1, h2, h3 {{ color: {NEON_GREEN} !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }}
    p, label, .stMarkdown, .stCaption {{ color: #E0E0E0 !important; }}
    
    .stTextInput input, .stDateInput input {{
        background-color: #2D2D2D !important; color: white !important; border: 1px solid #555 !important;
    }}

    /* MAIN ACTION BUTTON */
    div.stButton > button {{
        background-color: {NEON_GREEN} !important; color: black !important;
        font-weight: 900 !important; text-transform: uppercase; border: none;
        padding: 15px 0px; width: 100%; transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{
        box-shadow: 0 0 15px {NEON_GREEN}; transform: scale(1.02);
    }}

    /* TNG BUTTON STYLE */
    .tng-btn {{
        background-color: {TNG_BLUE}; color: white; text-decoration: none;
        padding: 10px 20px; border-radius: 8px; display: block; text-align: center;
        font-weight: bold; margin-bottom: 10px; border: 1px solid white;
    }}
    .tng-btn:hover {{ background-color: #004ca3; color: white; }}

    [data-testid="stDataFrame"] {{ background-color: {CARD_BG}; }}
    </style>
""", unsafe_allow_html=True)

# --- CONNECT TO GOOGLE SHEETS ---
try:
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    db = client.open("KroniBola DB")
    sheet_regs = db.worksheet("Registrations")
    sheet_sessions = db.worksheet("Sessions")
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

# --- HEADER ---
st.title("KRONI BOLA")
st.write("___")

# --- SIDEBAR ---
with st.sidebar:
    st.header("MENU")
    mode = st.radio("Navigate", ["⚽ Register for Match", "📝 Player List", "🔒 Admin Panel"])

# ==========================================
# PAGE 1: REGISTRATION (TNG ENHANCED)
# ==========================================
if mode == "⚽ Register for Match":
    st.subheader("SELECT MATCH")
    
    try:
        sessions_data = sheet_sessions.get_all_records()
        sessions_df = pd.DataFrame(sessions_data)
        if "Status" not in sessions_df.columns: sessions_df["Status"] = "Open"
        open_sessions = sessions_df[sessions_df["Status"] == "Open"]
        
        if open_sessions.empty:
            st.info("No games available.")
            st.stop()
            
        session_options = open_sessions.apply(lambda x: f"{x['Session Name']} ({x['Date']})", axis=1).tolist()
        selected_option = st.selectbox("Choose Session:", session_options)
        selected_row = open_sessions[open_sessions.apply(lambda x: f"{x['Session Name']} ({x['Date']})", axis=1) == selected_option].iloc[0]
        
        S_DATE = selected_row['Date']
        S_FEE = selected_row['Fee']
        S_NAME = selected_row['Session Name']
        
    except:
        st.error("Error loading sessions.")
        st.stop()

    st.write("")
    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"#### 1. PAY: RM {S_FEE}")
            try:
                st.image("pay.jpg", use_container_width=True)
            except:
                st.warning("Upload pay.jpg")
            
            # --- NEW TNG BUTTONS ---
            st.caption("On Mobile? Screenshot the QR above, then click below:")
            st.markdown(f"""
                <a href="tngdwallet://" class="tng-btn">
                    🔵 Open Touch 'n Go App
                </a>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("#### 2. CONFIRM")
            with st.form("entry_form", clear_on_submit=True):
                player_name = st.text_input("Your Nickname")
                submitted = st.form_submit_button("✅ CONFIRM SLOT")

                if submitted and player_name:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    row_data = [str(S_DATE), player_name, "Pending", str(S_FEE), timestamp]
                    sheet_regs.append_row(row_data)
                    st.success(f"Success! {player_name} added.")
                    
                    msg = f"Hi Admin, I paid RM{S_FEE} for {S_NAME} via TNG. Name: {player_name}."
                    wa_link = f"https://wa.me/{ADMIN_WHATSAPP}?text={msg}"
                    st.link_button("📤 SEND RECEIPT (WHATSAPP)", wa_link)
                elif submitted:
                    st.error("Name Required")

# ==========================================
# PAGE 2 & 3 (Keep existing logic)
# ==========================================
elif mode == "📝 Player List":
    # ... (Copy the Player List logic from previous code) ...
    st.subheader("PLAYER LIST")
    # (Just use the standard logic here, no changes needed for TNG)
    try:
        reg_data = sheet_regs.get_all_records()
        reg_df = pd.DataFrame(reg_data)
        st.dataframe(reg_df[["Session Date", "Player Name", "Payment Status"]], use_container_width=True)
    except:
        st.info("No data.")

elif mode == "🔒 Admin Panel":
    # ... (Copy the Admin logic from previous code) ...
    st.subheader("ADMIN")
    password = st.text_input("Password", type="password")
    if password == ADMIN_PASSWORD:
        st.success("Unlocked")
        # (Admin logic goes here)
