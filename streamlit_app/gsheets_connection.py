import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from datetime import datetime

def save_to_gsheets(data):
    """Save prediction data to Google Sheets with detailed debugging"""
    try:
        # Show start of process
        st.info("🔄 Starting Google Sheets save process...")
        
        # 1. Check secrets
        if "gsheets" not in st.secrets:
            st.error("❌ ERROR: No 'gsheets' section in secrets")
            return False
        
        config = st.secrets.gsheets
        st.success(f"✅ Secrets loaded: Spreadsheet ID: {config.spreadsheet_id}")
        
        # 2. Create credentials
        try:
            scope = ['https://www.googleapis.com/auth/spreadsheets']
            
            # Show private key info (first part only)
            pk_preview = config.private_key[:50] if config.private_key else "None"
            st.info(f"🔑 Private key preview: {pk_preview}...")
            
            # Prepare credentials
            creds_dict = {
                "type": "service_account",
                "project_id": "ed-prediction",
                "private_key": config.private_key.replace('\\n', '\n'),
                "client_email": config.client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
            st.success("✅ Credentials created successfully")
            
        except Exception as e:
            st.error(f"❌ ERROR creating credentials: {str(e)}")
            return False
        
        # 3. Authorize
        try:
            client = gspread.authorize(credentials)
            st.success("✅ Google Sheets client authorized")
        except Exception as e:
            st.error(f"❌ ERROR authorizing client: {str(e)}")
            return False
        
        # 4. Open spreadsheet
        try:
            spreadsheet = client.open_by_key(config.spreadsheet_id)
            st.success(f"✅ Spreadsheet opened: '{spreadsheet.title}'")
        except gspread.exceptions.SpreadsheetNotFound:
            st.error(f"❌ ERROR: Spreadsheet not found with ID: {config.spreadsheet_id}")
            st.info("Check: 1) Spreadsheet ID is correct 2) Service account has access")
            return False
        except Exception as e:
            st.error(f"❌ ERROR opening spreadsheet: {str(e)}")
            return False
        
        # 5. Get worksheet
        try:
            worksheet = spreadsheet.worksheet(config.worksheet_name)
            st.success(f"✅ Worksheet found: '{worksheet.title}'")
        except gspread.exceptions.WorksheetNotFound:
            st.error(f"❌ ERROR: Worksheet '{config.worksheet_name}' not found")
            
            # List available worksheets
            st.info("📋 Available worksheets:")
            try:
                all_worksheets = spreadsheet.worksheets()
                for i, ws in enumerate(all_worksheets):
                    st.info(f"  {i+1}. '{ws.title}'")
                
                # Try first worksheet
                worksheet = all_worksheets[0]
                st.warning(f"⚠️ Using first worksheet instead: '{worksheet.title}'")
            except Exception as e:
                st.error(f"❌ Could not list worksheets: {str(e)}")
                return False
        except Exception as e:
            st.error(f"❌ ERROR accessing worksheet: {str(e)}")
            return False
        
        # 6. Prepare data
        row_data = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # TimeStamp
            str(data.get("lactate", "")),                  # Lactate (in ABG)
            str(data.get("urea", "")),                     # Urea (mg/dl)
            str(data.get("creatinine", "")),               # Creatinine (mg/dl)
            str(data.get("platelets", "")),                # Platelets (10 ^ 6)
            data.get("resuscitation", "None"),             # Resuscitation Received
            data.get("prediction", "")                     # Prediction
        ]
        
        st.info(f"📊 Data to save: {row_data}")
        
        # 7. Save data
        try:
            # Get current row count before save
            current_rows = len(worksheet.get_all_values())
            st.info(f"📈 Current rows in sheet: {current_rows}")
            
            # Append row
            worksheet.append_row(row_data)
            st.success("✅ Row appended to worksheet")
            
            # Verify save
            new_rows = len(worksheet.get_all_values())
            if new_rows > current_rows:
                st.success(f"✅ VERIFIED: New row count: {new_rows} (Added {new_rows - current_rows} row)")
                return True
            else:
                st.warning("⚠️ Row count didn't increase - data may not have saved")
                return False
                
        except Exception as e:
            st.error(f"❌ ERROR saving data: {str(e)}")
            return False
            
    except Exception as e:
        st.error(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False
