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
    mode = st.radio("Navigate", ["⚽ Register for Match", "📝 Player List", "🔒 Admin Panel"])

# ==========================================
# PAGE 1: REGISTRATION (MULTI-SESSION)
# ==========================================
if mode == "⚽ Register for Match":
    st.subheader("SELECT A MATCH")
    
    try:
        sessions_data = sheet_sessions.get_all_records()
        sessions_df = pd.DataFrame(sessions_data)
        
        if sessions_df.empty:
            st.warning("No sessions found. Admin: Add sessions in Admin Panel.")
            st.stop()
            
        # Ensure 'Status' column exists
        if "Status" not in sessions_df.columns:
             # Create dummy status if missing to prevent crash
             sessions_df["Status"] = "Open"

        open_sessions = sessions_df[sessions_df["Status"] == "Open"]
        
        if open_sessions.empty:
            st.info("No open games right now.")
            st.stop()
            
        session_options = open_sessions.apply(lambda x: f"{x['Session Name']} ({x['Date']})", axis=1).tolist()
        
        selected_option = st.selectbox("Choose Session:", session_options)
        
        selected_row = open_sessions[open_sessions.apply(lambda x: f"{x['Session Name']} ({x['Date']})", axis=1) == selected_option].iloc[0]
        
        S_NAME = selected_row['Session Name']
        S_DATE = selected_row['Date']
        S_TIME = selected_row['Time']
        S_LOC = selected_row['Location']
        S_FEE = selected_row['Fee']

    except Exception as e:
        st.error(f"⚠️ Error loading sessions: {e}")
        st.stop()

    st.write("")
    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"#### FEE: RM {S_FEE}")
            try:
                st.image("pay.jpg", use_container_width=True)
            except:
                st.warning("Upload pay.jpg")
        with col2:
            st.markdown("#### MATCH DETAILS")
            st.info(f"📍 {S_LOC}\n\n⏰ {S_TIME}\n\n📅 {S_DATE}")
            
            with st.form("entry_form", clear_on_submit=True):
                player_name = st.text_input("Your Nickname")
                
                submitted = st.form_submit_button("✅ CONFIRM SLOT")

                if submitted and player_name:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    row_data = [str(S_DATE), player_name, "Pending", str(S_FEE), timestamp]
                    sheet_regs.append_row(row_data)
                    st.success(f"See you there, {player_name}!")
                    
                    msg = f"Hi Admin, I registered for {S_NAME} on {S_DATE}. Name: {player_name}."
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
        reg_data = sheet_regs.get_all_records()
        reg_df = pd.DataFrame(reg_data)
        
        sessions_data = sheet_sessions.get_all_records()
        sessions_df = pd.DataFrame(sessions_data)
        
        if not sessions_df.empty and "Date" in sessions_df.columns:
            available_dates = sessions_df['Date'].unique().tolist()
            selected_date_view = st.selectbox("View Players For:", available_dates)
        else:
            selected_date_view = None

        if not reg_df.empty and selected_date_view:
            reg_df['Session Date'] = reg_df['Session Date'].astype(str)
            display_df = reg_df[reg_df['Session Date'] == str(selected_date_view)]
            display_df = display_df[["Player Name", "Payment Status"]]
            
            def highlight_status(val):
                if val == 'Paid': return f'background-color: {NEON_GREEN}; color: black; font-weight: bold;'
                elif val == 'Pending': return 'background-color: #444; color: orange; font-weight: bold;'
                return ''

            if not display_df.empty:
                st.dataframe(display_df.style.applymap(highlight_status, subset=['Payment Status']), use_container_width=True)
            else:
                st.info(f"No players found for {selected_date_view}.")
        else:
            st.info("No data available.")
    except Exception as e:
        st.write(f"Loading Error: {e}")

# ==========================================
# PAGE 3: ADMIN PANEL (FIXED)
# ==========================================
elif mode == "🔒 Admin Panel":
    st.subheader("ADMIN ACCESS")
    password = st.text_input("Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("ACCESS GRANTED")
        
        tab_schedule, tab_players = st.tabs(["📅 MANAGE SCHEDULE", "👥 MANAGE PLAYERS"])
        
        # --- TAB 1: SCHEDULE MANAGEMENT ---
        with tab_schedule:
            st.write("Edit upcoming games here.")
            
            try:
                s_data = sheet_sessions.get_all_records()
                s_df = pd.DataFrame(s_data)
                
                if s_df.empty:
                     s_df = pd.DataFrame(columns=["Session Name", "Date", "Time", "Location", "Fee", "Status"])

                # --- ⚠️ THE FIX IS HERE ⚠️ ---
                # We convert the 'Date' column from Text to Date Objects
                if "Date" in s_df.columns:
                     s_df["Date"] = pd.to_datetime(s_df["Date"], errors='coerce').dt.date

                edited_schedule = st.data_editor(
                    s_df,
                    num_rows="dynamic",
                    column_config={
                        "Status": st.column_config.SelectboxColumn("Status", options=["Open", "Closed"]),
                        "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD")
                    },
                    use_container_width=True
                )
                
                if st.button("💾 SAVE SCHEDULE"):
                    # We must convert Date BACK to String before saving to Google Sheets
                    # otherwise Google Sheets gets confused
                    save_df = edited_schedule.copy()
                    save_df["Date"] = save_df["Date"].astype(str)
                    
                    sheet_sessions.clear()
                    sheet_sessions.append_row(save_df.columns.tolist())
                    sheet_sessions.append_rows(save_df.values.tolist())
                    st.toast("Schedule Updated!", icon="✅")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

        # --- TAB 2: PLAYERS MANAGEMENT ---
        with tab_players:
            p_data = sheet_regs.get_all_records()
            p_df = pd.DataFrame(p_data)
            
            if "Delete?" not in p_df.columns:
                p_df.insert(0, "Delete?", False)
            
            edited_players = st.data_editor(
                p_df, 
                num_rows="dynamic",
                column_config={
                    "Delete?": st.column_config.CheckboxColumn("Delete?", default=False),
                    "Payment Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Paid", "Rejected"])
                },
                use_container_width=True
            )
            
            if st.button("💾 SAVE PLAYER STATUS"):
                rows_to_keep = edited_players[edited_players["Delete?"] == False]
                final_data = rows_to_keep.drop(columns=["Delete?"])
                sheet_regs.clear()
                sheet_regs.append_row(final_data.columns.tolist())
                sheet_regs.append_rows(final_data.values.tolist())
                st.toast("Players Updated!", icon="✅")
                st.rerun()
