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
TNG_BLUE = "#005EB8"
WAITLIST_COLOR = "#00C4FF"

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
    
    .stTextInput input, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] {{
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

    div.stButton > button:disabled {{
        background-color: #555 !important;
        color: #888 !important;
        border: 2px solid #555 !important;
        cursor: not-allowed;
    }}

    .tng-btn {{
        background-color: {TNG_BLUE};
        color: white !important;
        text-decoration: none;
        padding: 12px 20px;
        border-radius: 8px;
        display: block;
        text-align: center;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 10px;
        border: 1px solid white;
    }}
    
    .guide-box {{
        background-color: #333;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid {NEON_GREEN};
        margin-bottom: 20px;
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
    db = client.open("KroniBola DB")
    sheet_regs = db.worksheet("Registrations")
    sheet_sessions = db.worksheet("Sessions")
except Exception as e:
    st.error(f"⚠️ CONNECTION ERROR: {e}")
    st.stop()

# --- HEADER ---
st.title("KRONI BOLA")
st.write("___")

# --- SIDEBAR ---
with st.sidebar:
    st.header("MENU")
    mode = st.radio("Navigate", ["⚽ Register & Lineup", "🔒 Admin Panel"])

# ==========================================
# PAGE 1: REGISTRATION + LIST
# ==========================================
if mode == "⚽ Register & Lineup":
    st.subheader("SELECT A MATCH")
    
    st.markdown(f"""
    <div class="guide-box">
        <h4 style="color:{NEON_GREEN}; margin:0;">📝 HOW TO REGISTER</h4>
        <p style="font-size:14px; margin-top:5px;">
        <b>1. Screenshot</b> the QR Code below.<br>
        <b>2. Click</b> Blue Button (TNG).<br>
        <b>3. Register</b> Name & Phone.<br>
        <b>4. Send</b> Receipt via WhatsApp.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        sessions_data = sheet_sessions.get_all_records()
        sessions_df = pd.DataFrame(sessions_data)
        
        reg_data = sheet_regs.get_all_records()
        reg_df = pd.DataFrame(reg_data)

        if sessions_df.empty:
            st.warning("No sessions found.")
            st.stop()
            
        if "Status" not in sessions_df.columns: sessions_df["Status"] = "Open"
        if "Max Players" not in sessions_df.columns: st.error("Add 'Max Players' column."); st.stop()

        open_sessions = sessions_df[sessions_df["Status"] == "Open"]
        
        if open_sessions.empty:
            st.info("No open games.")
            st.stop()
            
        session_options = open_sessions.apply(lambda x: f"{x['Session Name']} ({x['Date']})", axis=1).tolist()
        selected_option = st.selectbox("Choose Session:", session_options)
        
        selected_row = open_sessions[open_sessions.apply(lambda x: f"{x['Session Name']} ({x['Date']})", axis=1) == selected_option].iloc[0]
        
        S_NAME = selected_row['Session Name']
        S_DATE = selected_row['Date']
        S_TIME = selected_row['Time']
        S_LOC = selected_row['Location']
        S_FEE = selected_row['Fee']
        S_MAX = int(selected_row['Max Players']) if str(selected_row['Max Players']).isdigit() else 20
        
        current_count = 0
        if not reg_df.empty:
            reg_df['Session Date'] = reg_df['Session Date'].astype(str)
            active_players = reg_df[
                (reg_df['Session Date'] == str(S_DATE)) & 
                (reg_df['Payment Status'].isin(['Pending', 'Paid']))
            ]
            current_count = len(active_players)
            
        spots_left = S_MAX - current_count
        is_full = spots_left <= 0

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        st.stop()

    st.write("")
    
    with st.container():
        st.caption(f"SPOTS FILLED: {current_count} / {S_MAX}")
        progress = min(current_count / S_MAX, 1.0)
        st.progress(progress)
        
        if is_full:
            st.info("ℹ️ FULLY BOOKED! Joining Waitlist...")
        else:
            st.success(f"🔥 {spots_left} SPOTS LEFT!")

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"#### FEE: RM {S_FEE}")
            if not is_full:
                try: st.image("pay.jpg", use_container_width=True)
                except: st.warning("Upload pay.jpg")
                st.markdown(f"""<a href="tngdwallet://" class="tng-btn">🔵 Open Touch 'n Go</a>""", unsafe_allow_html=True)
            else:
                st.write("🚫 **DO NOT PAY YET**")
                st.caption("Waitlist players pay only when a slot opens.")

        with col2:
            st.markdown("#### MATCH DETAILS")
            st.info(f"📍 {S_LOC}\n\n⏰ {S_TIME}\n\n📅 {S_DATE}")
            
            with st.form("entry_form", clear_on_submit=False): 
                player_name = st.text_input("Your Nickname")
                player_phone = st.text_input("Phone (e.g. 0123456789)")
                
                if is_full:
                    submitted = st.form_submit_button("⏳ JOIN WAITLIST")
                    new_status = "Waitlist"
                else:
                    submitted = st.form_submit_button("✅ CONFIRM SLOT")
                    new_status = "Pending"

                if submitted:
                    # --- 1. BASIC INPUT CHECK ---
                    if not player_name or not player_phone:
                        st.error("⚠️ Please fill in both Name and Phone Number.")
                        st.stop()
                    
                    # --- 2. PHONE NUMBER VALIDATION ---
                    # Remove dashes and spaces
                    clean_phone = player_phone.replace("-", "").replace(" ", "")
                    
                    if not clean_phone.isdigit():
                        st.error("⚠️ Invalid Phone: Digits only please (e.g. 0123456789).")
                        st.stop()
                        
                    if len(clean_phone) < 10 or len(clean_phone) > 13:
                        st.error("⚠️ Invalid Phone: Number seems too short/long. Please check.")
                        st.stop()

                    # --- 3. DUPLICATE NAME CHECK ---
                    if not reg_df.empty:
                        current_session_regs = reg_df[reg_df['Session Date'] == str(S_DATE)]
                        taken_names = current_session_regs['Player Name'].astype(str).str.lower().str.strip().tolist()
                        
                        if player_name.lower().strip() in taken_names:
                            st.error(f"⚠️ Name '{player_name}' taken! Please add initials.")
                            st.stop()
                    
                    # --- 4. SAVE ---
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # Save clean phone with ' prefix to force text in sheets
                    row_data = [str(S_DATE), player_name, "'" + str(clean_phone), new_status, str(S_FEE), timestamp]
                    sheet_regs.append_row(row_data)
                    
                    if new_status == "Waitlist":
                        st.warning(f"You are on the WAITLIST.")
                        msg = f"Hi Admin, I joined WAITLIST for {S_NAME} on {S_DATE}. Name: {player_name}."
                    else:
                        st.balloons()
                        st.success(f"Success! {player_name} secured a spot.")
                        msg = f"Hi Admin, I registered for {S_NAME} on {S_DATE}. Name: {player_name}."
                    
                    wa_link = f"https://wa.me/{ADMIN_WHATSAPP}?text={msg}"
                    st.link_button("📤 NOTIFY ADMIN (WHATSAPP)", wa_link)
                    st.rerun() 

    st.divider()
    st.subheader("CURRENT LINEUP")
    
    if not reg_df.empty:
        reg_df['Session Date'] = reg_df['Session Date'].astype(str)
        display_df
