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

# --- THEME CONFIGURATION (MATCHING YOUR LOGO) ---
NEON_GREEN = "#CCFF00"  # The specific lime green from your logo
DARK_BG = "#121212"     # Matte black
CARD_BG = "#1E1E1E"     # Slightly lighter dark for cards
TEXT_COLOR = "#FFFFFF"

# --- CUSTOM CSS ---
st.markdown(f"""
    <style>
    /* 1. FORCE DARK BACKGROUND */
    .stApp {{
        background-color: {DARK_BG};
    }}
    
    /* 2. CUSTOM CARDS (Dark Grey with Neon Border) */
    .css-1r6slb0, .css-keje6w, .stForm {{
        background-color: {CARD_BG};
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #333;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}
    
    /* 3. NEON GREEN HEADERS */
    h1, h2, h3 {{
        color: {NEON_GREEN} !important;
        font-family: 'Arial Black', sans-serif; /* Bold Sporty Font */
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* 4. TEXT COLOR FIX */
    p, label, .stMarkdown {{
        color: {TEXT_COLOR} !important;
    }}
    
    /* 5. INPUT FIELDS (Dark Mode) */
    .stTextInput input, .stDateInput input {{
        background-color: #2b2b2b !important;
        color: white !important;
        border: 1px solid #444 !important;
    }}
    
    /* 6. BUTTONS (Neon Green with Black Text) */
    div.stButton > button {{
        background-color: {NEON_GREEN} !important;
        color: black !important; /* Black text on neon green is easier to read */
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        font-weight: 800; /* Extra Bold */
        text-transform: uppercase;
        width: 100%;
        transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{
        background-color: white !important; /* Flash white on hover */
        color: black !important;
        box-shadow: 0 0 10px {NEON_GREEN};
    }}

    /* 7. WHATSAPP BUTTON */
    div.stLinkButton > a {{
        background-color: #25D366 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        border: none;
    }}
    
    /* 8. DATAFRAME FIXES */
    [data-testid="stDataFrame"] {{
        background-color: {CARD_BG};
    }}
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

# --- HEADER SECTION ---
col_logo, col_title = st.columns([1, 4])
with col_title:
    # Centered Title
    st.title("KRONI BOLA")
st.write("___")

# --- SIDEBAR ---
with st.sidebar:
    st.header("MENU")
    mode = st.radio("Select Option", ["⚽ New Registration", "📝 Player List", "🔒 Admin Panel"])

# ==========================================
# PAGE 1: REGISTRATION
# ==========================================
if mode == "⚽ New Registration":
    st.subheader("Join the Squad")
    
    # CARD LAYOUT
    with st.container():
        # Using columns to create layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"<h4 style='color:white'>1. SCAN QR</h4>", unsafe_allow_html=True)
            try:
                st.image("pay.jpg", use_container_width=True)
            except:
                st.warning("Admin: Upload pay.jpg to GitHub")

        with col2:
            st.markdown(f"<h4 style='color:white'>2. DETAILS</h4>", unsafe_allow_html=True)
            with st.form("entry_form", clear_on_submit=True):
                player_name = st.text_input("Your Nickname")
                session_date = st.date_input("Match Date")
                
                submitted = st.form_submit_button("CONFIRM SLOT")

                if submitted and player_name:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    row_data = [str(session_date), player_name, "Pending", "15", timestamp]
                    sheet.append_row(row_data)
                    
                    st.success(f"✅ {player_name} added to the lineup!")
                    
                    # WhatsApp Button
                    msg = f"Hi Admin, I just registered for the game on {session_date}. Name: {player_name}. Here is my receipt:"
                    wa_link = f"https://wa.me/{ADMIN_WHATSAPP}?text={msg}"
                    st.link_button("📤 SEND RECEIPT (WHATSAPP)", wa_link)
                    
                elif submitted:
                    st.error("Please enter your name.")

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
            
            # Custom Highlighter for Dark Mode
            def highlight_status(val):
                if val == 'Paid':
                    return f'background-color: {NEON_GREEN}; color: black; font-weight: bold;'
                elif val == 'Pending':
                    return 'background-color: #333333; color: orange; font-weight: bold;'
                return ''

            st.dataframe(
                display_df.style.applymap(highlight_status, subset=['Payment Status']),
                use_container_width=True,
                height=500
            )
        else:
            st.info("No players yet.")
    except Exception as e:
        st.write("List is empty or loading error.")

# ==========================================
# PAGE 3: ADMIN PANEL
# ==========================================
elif mode == "🔒 Admin Panel":
    st.subheader("ADMIN ACCESS")
    password = st.text_input("Enter Password", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("ACCESS GRANTED")
        
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        st.write("Update Status:")
        edited_df = st.data_editor(
            df, 
            num_rows="dynamic",
            column_config={
                "Payment Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Pending", "Paid", "Rejected"],
                    required=True
                )
            },
            use_container_width=True
        )
        
        if st.button("💾 SAVE CHANGES"):
            sheet.clear()
            sheet.append_row(df.columns.tolist())
            sheet.append_rows(edited_df.values.tolist())
            st.toast("Database Updated!", icon="✅")
            st.rerun()
