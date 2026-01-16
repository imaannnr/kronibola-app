import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
# 🔒 SECURE PASSWORD FETCH
try:
    if "admin_password" in st.secrets:
        ADMIN_PASSWORD = st.secrets["admin_password"]
    else:
        st.error("🚨 Key 'admin_password' missing in Secrets.")
        st.stop()
    ADMIN_WHATSAPP = "60126183827" 
except Exception as e:
    st.error(f"🚨 Security Error: {e}")
    st.stop()

# --- PAGE SETUP ---
st.set_page_config(page_title="KroniBola", page_icon="⚽", layout="centered")

# --- 🎨 THEME & DESIGN VARIABLES ---
NEON_GREEN = "#CCFF00"
TNG_BLUE = "#005EB8"
WAITLIST_COLOR = "#00C4FF"
# High Quality Stadium Background URL (Free to use from Unsplash)
BG_IMAGE_URL = "https://images.unsplash.com/photo-1518091043644-c1d4457512c6?q=80&w=2548&auto=format&fit=crop"

# --- 🖌️ CUSTOM CSS (GLASS UI + BACKGROUND) ---
st.markdown(f"""
    <style>
    /* 1. MAIN BACKGROUND IMAGE */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{BG_IMAGE_URL}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* 2. DARK OVERLAY (To make text readable) */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.65); /* Dark tint */
        z-index: -1;
    }}

    /* 3. GLASSMOPHISM CARDS (Frosted Glass Effect) */
    .stForm, [data-testid="stDataFrame"], .guide-box, .css-1r6slb0, .stTabs {{
        background-color: rgba(30, 30, 30, 0.6) !important; /* Semi-transparent black */
        backdrop-filter: blur(12px); /* Blur effect */
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1); /* Thin white border */
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        border-radius: 15px;
        padding: 20px;
    }}

    /* 4. TYPOGRAPHY */
    h1, h2, h3 {{
        color: {NEON_GREEN} !important;
        font-family: 'Arial Black', sans-serif;
        text-transform: uppercase;
        text-shadow: 0 0 10px rgba(204, 255, 0, 0.3);
    }}
    
    p, label, .stMarkdown, .stCaption, .stText, h4 {{ color: #FFFFFF !important; }}
    
    /* 5. INPUT FIELDS */
    .stTextInput input, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: white !important;
        border: 1px solid #555 !important;
    }}

    /* 6. NEON BUTTONS */
    div.stButton > button {{
        background-color: {NEON_GREEN} !important;
        color: #000000 !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        border: 2px solid {NEON_GREEN} !important;
        width: 100%;
        transition: all 0.3s ease;
        border-radius: 8px;
    }}
    div.stButton > button:hover {{
        background-color: white !important;
        color: black !important;
        box-shadow: 0 0 20px {NEON_GREEN};
        transform: scale(1.02);
    }}
    
    /* Disabled Button */
    div.stButton > button:disabled {{
        background-color: rgba(255,255,255,0.1) !important;
        color: #aaa !important;
        border: 1px solid #555 !important;
        box-shadow: none;
    }}

    /* 7. TNG BUTTON */
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
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(5px);
    }}

    /* 8. GUIDE BOX SPECIFIC */
    .guide-box {{
        border-left: 5px solid {NEON_GREEN};
        margin-bottom: 20px;
    }}
    
    /* Sidebar Transparent */
    [data-testid="stSidebar"] {{
        background-color: rgba(10, 10, 10, 0.9);
        border-right: 1px solid #333;
    }}
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

# --- 🖼️ LOGO & HEADER ---
col_logo, col_title = st.columns([1, 3])

with col_logo:
    try:
        # ⚠️ MAKE SURE YOU UPLOAD 'logo.png' TO GITHUB
        st.image("logo.png", width=110) 
    except:
        st.write("⚽") # Fallback emoji if logo missing

with col_title:
    st.title("KRONI BOLA")
    st.caption("EST. 2026")

st.write("___")

# --- SIDEBAR ---
with st.sidebar:
    st.header("MENU")
    mode = st.radio("Navigate", ["⚽ Register & Lineup", "🔒 Admin Panel"])

# ==========================================
# PAGE 1: REGISTRATION + LIST
# ==========================================
if mode == "⚽ Register & Lineup":
    st.subheader("Match Day")
    
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
    
    # --- GLASS CARD FORM ---
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
                    if not player_name or not player_phone:
                        st.error("⚠️ Please fill in both Name and Phone Number.")
                        st.stop()
                    
                    clean_phone = player_phone.replace("-", "").replace(" ", "")
                    if not clean_phone.isdigit():
                        st.error("⚠️ Invalid Phone: Digits only please.")
                        st.stop()
                    if len(clean_phone) < 10 or len(clean_phone) > 13:
                        st.error("⚠️ Invalid Phone: Length incorrect.")
                        st.stop()

                    if not reg_df.empty:
                        current_session_regs = reg_df[reg_df['Session Date'] == str(S_DATE)]
                        taken_names = current_session_regs['Player Name'].astype(str).str.lower().str.strip().tolist()
                        
                        if player_name.lower().strip() in taken_names:
                            st.error(f"⚠️ Name '{player_name}' taken! Please add initials.")
                            st.stop()
                    
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        display_df = reg_df[reg_df['Session Date'] == str(S_DATE)]
        
        if not display_df.empty:
            status_order = {'Paid': 1, 'Pending': 2, 'Waitlist': 3, 'Rejected': 4}
            display_df['Sort'] = display_df['Payment Status'].map(status_order)
            display_df = display_df.sort_values('Sort').drop(columns=['Sort'])
            
            if "Player Name" in display_df.columns and "Payment Status" in display_df.columns:
                display_df = display_df[["Player Name", "Payment Status"]]
            
            def highlight_status(val):
                if val == 'Paid': return f'background-color: {NEON_GREEN}; color: black; font-weight: bold;'
                elif val == 'Pending': return 'background-color: #444; color: orange; font-weight: bold;'
                elif val == 'Waitlist': return f'background-color: {WAITLIST_COLOR}; color: black; font-weight: bold;'
                return ''

            st.dataframe(display_df.style.applymap(highlight_status, subset=['Payment Status']), use_container_width=True)
        else:
            st.info("Pitch is empty... Be the first to join!")
    else:
        st.info("No players yet.")


# ==========================================
# PAGE 2: ADMIN PANEL
# ==========================================
elif mode == "🔒 Admin Panel":
    st.subheader("ADMIN ACCESS")
    password = st.text_input("Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("ACCESS GRANTED")
        
        tab_schedule, tab_players = st.tabs(["📅 MANAGE SCHEDULE", "👥 MANAGE PLAYERS"])
        
        with tab_schedule:
            st.write("Edit upcoming games here.")
            try:
                s_data = sheet_sessions.get_all_records()
                s_df = pd.DataFrame(s_data)
                
                if s_df.empty:
                     s_df = pd.DataFrame(columns=["Session Name", "Date", "Time", "Location", "Fee", "Status", "Max Players"])

                if "Date" in s_df.columns:
                     s_df["Date"] = pd.to_datetime(s_df["Date"], errors='coerce').dt.date

                edited_schedule = st.data_editor(
                    s_df,
                    num_rows="dynamic",
                    column_config={
                        "Status": st.column_config.SelectboxColumn("Status", options=["Open", "Closed"]),
                        "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                        "Max Players": st.column_config.NumberColumn("Max Players", min_value=1, max_value=100, step=1, default=15)
                    },
                    use_container_width=True
                )
                
                if st.button("💾 SAVE SCHEDULE"):
                    save_df = edited_schedule.copy()
                    save_df["Date"] = save_df["Date"].astype(str)
                    sheet_sessions.clear()
                    sheet_sessions.append_row(save_df.columns.tolist())
                    sheet_sessions.append_rows(save_df.values.tolist())
                    st.toast("Schedule Updated!", icon="✅")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_players:
            st.markdown("### 🔍 MANAGE PLAYERS")
            
            p_data = sheet_regs.get_all_records()
            p_df = pd.DataFrame(p_data)
            
            if p_df.empty:
                st.info("No players yet.")
            else:
                p_df['Session Date'] = p_df['Session Date'].astype(str)
                available_dates = p_df['Session Date'].unique().tolist()
                
                selected_filter = st.selectbox("Filter by Game:", available_dates)
                filtered_view = p_df[p_df['Session Date'] == selected_filter].copy()

                filtered_view["Timestamp"] = pd.to_datetime(filtered_view["Timestamp"], errors='coerce')
                now = datetime.now()
                filtered_view["Hours_Ago"] = (now - filtered_view["Timestamp"]).dt.total_seconds() / 3600
                filtered_view["Overdue"] = (filtered_view["Payment Status"] == "Pending") & (filtered_view["Hours_Ago"] > 1.0)
                
                if "Delete?" not in filtered_view.columns:
                    filtered_view.insert(0, "Delete?", False)

                display_df = filtered_view.drop(columns=["Hours_Ago"])
                if "Phone" not in display_df.columns: display_df["Phone"] = ""

                edited_players = st.data_editor(
                    display_df, 
                    num_rows="dynamic",
                    column_config={
                        "Delete?": st.column_config.CheckboxColumn("Delete?", default=False),
                        "Overdue": st.column_config.CheckboxColumn("Overdue (>1h?)", disabled=True),
                        "Payment Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Paid", "Waitlist", "Rejected"]),
                        "Phone": st.column_config.TextColumn("Phone"),
                        "Timestamp": st.column_config.DatetimeColumn("Registered At", format="h:mm a")
                    },
                    use_container_width=True
                )
                
                if st.button("💾 SAVE CHANGES (THIS GAME ONLY)"):
                    rows_to_update = edited_players[edited_players["Delete?"] == False]
                    other_dates_df = p_df[p_df['Session Date'] != selected_filter]
                    
                    rows_to_update = rows_to_update.drop(columns=["Delete?", "Overdue"])
                    rows_to_update["Timestamp"] = rows_to_update["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
                    
                    final_combined_df = pd.concat([other_dates_df, rows_to_update], ignore_index=True)
                    
                    sheet_regs.clear()
                    sheet_regs.append_row(final_combined_df.columns.tolist())
                    sheet_regs.append_rows(final_combined_df.values.tolist())
                    st.toast("Database Updated Successfully!", icon="✅")
                    st.rerun()
