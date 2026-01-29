import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from datetime import datetime

def get_gsheets_connection():
    """Connect to Google Sheets using service account credentials"""
    try:
        # Clear previous debug messages
        st.session_state.gsheet_debug = []
        
        # Check if secrets exist
        if "gsheets" not in st.secrets:
            st.session_state.gsheet_debug.append("❌ No Google Sheets secrets found")
            return None
        
        config = st.secrets.gsheets
        
        # Verify all required secrets
        required = ["spreadsheet_id", "worksheet_name", "private_key", "client_email"]
        for field in required:
            if field not in config:
                st.session_state.gsheet_debug.append(f"❌ Missing required field: {field}")
                return None
        
        st.session_state.gsheet_debug.append("✅ All required secrets found")
        
        # Create credentials
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        
        # Fix private key formatting
        private_key = config.private_key.replace('\\n', '\n').strip()
        
        credentials_dict = {
            "type": "service_account",
            "project_id": "ed-prediction",
            "private_key": private_key,
            "client_email": config.client_email,
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        st.session_state.gsheet_debug.append("🔄 Creating credentials...")
        
        try:
            credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
            st.session_state.gsheet_debug.append("✅ Credentials created")
        except Exception as e:
            st.session_state.gsheet_debug.append(f"❌ Credential creation failed: {str(e)}")
            return None
        
        # Authorize
        try:
            client = gspread.authorize(credentials)
            st.session_state.gsheet_debug.append("✅ Google Sheets authorized")
        except Exception as e:
            st.session_state.gsheet_debug.append(f"❌ Authorization failed: {str(e)}")
            return None
        
        # Open spreadsheet
        try:
            spreadsheet = client.open_by_key(config.spreadsheet_id)
            st.session_state.gsheet_debug.append(f"✅ Spreadsheet opened: {spreadsheet.title}")
        except Exception as e:
            st.session_state.gsheet_debug.append(f"❌ Could not open spreadsheet: {str(e)}")
            st.session_state.gsheet_debug.append("Check: 1) Spreadsheet ID, 2) Service account has access")
            return None
        
        # Get worksheet
        try:
            worksheet = spreadsheet.worksheet(config.worksheet_name)
            st.session_state.gsheet_debug.append(f"✅ Worksheet found: {worksheet.title}")
            return worksheet
        except Exception as e:
            st.session_state.gsheet_debug.append(f"❌ Worksheet error: {str(e)}")
            # List available worksheets
            try:
                all_worksheets = spreadsheet.worksheets()
                st.session_state.gsheet_debug.append("Available worksheets:")
                for ws in all_worksheets:
                    st.session_state.gsheet_debug.append(f"  - '{ws.title}'")
                
                # Try first worksheet as fallback
                worksheet = all_worksheets[0]
                st.session_state.gsheet_debug.append(f"⚠️ Using first worksheet: '{worksheet.title}'")
                return worksheet
            except:
                st.session_state.gsheet_debug.append("❌ Could not list worksheets")
                return None
    
    except Exception as e:
        if 'gsheet_debug' not in st.session_state:
            st.session_state.gsheet_debug = []
        st.session_state.gsheet_debug.append(f"❌ Unexpected error: {str(e)}")
        return None

def save_to_gsheets(data):
    """Save prediction data to Google Sheets - WITHOUT probability and risk level"""
    try:
        # Initialize debug if not exists
        if 'gsheet_debug' not in st.session_state:
            st.session_state.gsheet_debug = []
        else:
            st.session_state.gsheet_debug = []
        
        # Get connection
        worksheet = get_gsheets_connection()
        
        if worksheet:
            # Show debug info
            with st.expander("🔍 Google Sheets Connection Debug", expanded=True):
                for msg in st.session_state.gsheet_debug:
                    if "✅" in msg:
                        st.success(msg)
                    elif "❌" in msg:
                        st.error(msg)
                    elif "⚠️" in msg:
                        st.warning(msg)
                    else:
                        st.info(msg)
            
            # Prepare data row - ONLY 7 COLUMNS (no probability, no risk_level)
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # TimeStamp
                str(data.get("lactate", "")),                  # Lactate (in ABG)
                str(data.get("urea", "")),                     # Urea (mg/dl)
                str(data.get("creatinine", "")),               # Creatinine (mg/dl)
                str(data.get("platelets", "")),                # Platelets (10 ^ 6)
                data.get("resuscitation", "None"),             # Resuscitation Received
                data.get("prediction", "")                     # Prediction ONLY
            ]
            
            st.info(f"📤 Preparing to save: {row_data}")
            
            # Save data
            worksheet.append_row(row_data)
            
            st.success("✅ Data saved to Google Sheets!")
            return True
        else:
            st.error("❌ Could not connect to Google Sheets")
            return False
            
    except Exception as e:
        st.error(f"❌ Error saving to Google Sheets: {str(e)}")
        return False
