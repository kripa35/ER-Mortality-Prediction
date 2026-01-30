import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from datetime import datetime
import os

def get_gsheets_connection():
    """Connect to Google Sheets using service account credentials"""
    try:
        # Clearing any previous messages
        if 'gsheet_debug' not in st.session_state:
            st.session_state.gsheet_debug = []
        
        # Defining the scope
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Trying to load credentials from JSON file
        json_files = ['google_credentials.json', 'service_account.json', 'credentials.json']
        credentials = None
        json_file_used = None
        
        for json_file in json_files:
            if os.path.exists(json_file):
                try:
                    credentials = Credentials.from_service_account_file(json_file, scopes=scope)
                    json_file_used = json_file
                    st.session_state.gsheet_debug.append(f"✅ Using credentials from: {json_file}")
                    break
                except Exception as e:
                    st.session_state.gsheet_debug.append(f"⚠️ Failed {json_file}: {str(e)}")
        
        if credentials is None:
            st.session_state.gsheet_debug.append("❌ No valid credentials file found")
            return None
        
        # Authorizing gspread
        client = gspread.authorize(credentials)
        st.session_state.gsheet_debug.append("✅ Google authentication successful")
        
        # Getting spreadsheet ID from secrets or use default
        if "gsheets" in st.secrets:
            spreadsheet_id = st.secrets["gsheets"]["spreadsheet_id"]
        else:
            spreadsheet_id = "1urV5GP7aH5bD-hcez7EUpECIRABQQ3QbgaHSAwNR4M0"
        
        # Opening the spreadsheet
        try:
            spreadsheet = client.open_by_key(spreadsheet_id)
            st.session_state.gsheet_debug.append(f"✅ Spreadsheet opened: '{spreadsheet.title}'")
        except Exception as e:
            st.session_state.gsheet_debug.append(f"❌ Failed to open spreadsheet: {str(e)}")
            return None
        
        # Getting worksheet name from secrets or use default
        if "gsheets" in st.secrets and "worksheet_name" in st.secrets["gsheets"]:
            target_worksheet_name = st.secrets["gsheets"]["worksheet_name"]
        else:
            target_worksheet_name = "streamlit-data_entry_er"
        
        st.session_state.gsheet_debug.append(f"Looking for worksheet: '{target_worksheet_name}'")
        
        # Listing all worksheets for debugging
        all_worksheets = spreadsheet.worksheets()
        st.session_state.gsheet_debug.append(f"Available worksheets ({len(all_worksheets)} total):")
        
        for i, ws in enumerate(all_worksheets):
            st.session_state.gsheet_debug.append(f"  {i+1}. '{ws.title}'")
        
        # Trying to find the worksheet - EXACT MATCH
        worksheet_found = None
        
        # First try: Exact match
        for ws in all_worksheets:
            if ws.title == target_worksheet_name:
                worksheet_found = ws
                st.session_state.gsheet_debug.append(f"✅ Found exact match: '{ws.title}'")
                break
        
        # Second try: Case-insensitive match
        if worksheet_found is None:
            for ws in all_worksheets:
                if ws.title.lower() == target_worksheet_name.lower():
                    worksheet_found = ws
                    st.session_state.gsheet_debug.append(f"✅ Found case-insensitive match: '{ws.title}'")
                    break
        
        # Third try: Contains match
        if worksheet_found is None:
            for ws in all_worksheets:
                if target_worksheet_name.lower() in ws.title.lower():
                    worksheet_found = ws
                    st.session_state.gsheet_debug.append(f"✅ Found partial match: '{ws.title}'")
                    break
        
        if worksheet_found is None:
            st.session_state.gsheet_debug.append(f"❌ Worksheet '{target_worksheet_name}' not found!")
            # Using first worksheet as fallback
            if all_worksheets:
                worksheet_found = all_worksheets[0]
                st.session_state.gsheet_debug.append(f"⚠️ Using first worksheet instead: '{worksheet_found.title}'")
            else:
                st.session_state.gsheet_debug.append("❌ No worksheets found in spreadsheet")
                return None
        
        return worksheet_found
    
    except Exception as e:
        error_msg = f"❌ Connection error: {str(e)}"
        if 'gsheet_debug' in st.session_state:
            st.session_state.gsheet_debug.append(error_msg)
        return None

def save_to_gsheets(data):
    """Save prediction data to Google Sheets"""
    try:
        # Clearing previous debug messages at start of save attempt
        st.session_state.gsheet_debug = []
        
        # Get worksheet connection
        worksheet = get_gsheets_connection()
        
        if worksheet:
            # Showing debug info
            with st.expander("🔧 Google Sheets Connection Debug Info", expanded=False):
                for msg in st.session_state.gsheet_debug:
                    if "✅" in msg:
                        st.success(msg)
                    elif "❌" in msg or "Failed" in msg:
                        st.error(msg)
                    elif "⚠️" in msg:
                        st.warning(msg)
                    else:
                        st.info(msg)
            
            # Preparing data row - MATCHING YOUR GOOGLE SHEETS COLUMNS
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # TimeStamp
                str(data.get("lactate", "")),                  # Lactate (in ABG)
                str(data.get("urea", "")),                     # Urea (mg/dl)
                str(data.get("creatinine", "")),               # Creatinine (mg/dl)
                str(data.get("platelets", "")),                # Platelets (10 ^ 6)
                data.get("resuscitation", "None"),             # Resuscitation Received
                data.get("prediction", ""),                    # Prediction
                str(data.get("probability", "")),              # Probability Score
                data.get("risk_level", "")                     # Risk Level
            ]
            
            st.info(f"📤 Saving data to row {len(worksheet.get_all_values()) + 1}")
            
            # Appendding the row
            worksheet.append_row(row_data)
            
            # Verifying the save
            all_data = worksheet.get_all_values()
            last_row = all_data[-1] if all_data else []
            
            if last_row and last_row[0].startswith(datetime.now().strftime("%Y-%m-%d")):
                return True
            else:
                st.warning("⚠️ Data might not have saved correctly")
                return False
        else:
            st.error("❌ Could not connect to Google Sheets")
            return False
            
    except Exception as e:
        st.error(f"❌ Error saving to Google Sheets: {str(e)}")
        return False
