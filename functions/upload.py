import pandas as pd
import streamlit as st

def upload_to_sheet(df, sheet):
    import streamlit as st

    # Convert date column to string for comparison
    df['Date'] = df['Date'].astype(str)
    
    # Get all records from the sheet
    existing_data = sheet.get_all_records()
    existing_df = pd.DataFrame(existing_data)

    if existing_df.empty:
        # If sheet is empty, create columns and upload all data
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.success("Uploaded successfully")
    else:
        # Check if any date in df already exists in the sheet
        existing_dates = existing_df['Date'].tolist()
        new_dates = df['Date'].tolist()

        if any(date in existing_dates for date in new_dates):
            st.warning("Data with the same date already exists. Skipping upload.")
        else:
            # Append new data to the existing data while maintaining order
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df['Date'] = pd.to_datetime(combined_df['Date'], format='%d-%m-%y')
            combined_df = combined_df.sort_values(by=['Date','actual', 'Repetition No.'], kind='stable')
            combined_df['Date'] = combined_df['Date'].dt.strftime('%d-%m-%y')  # Convert date back to string
            
            sheet.clear()  # Clear the sheet before updating
            sheet.update([combined_df.columns.values.tolist()] + combined_df.values.tolist())
            st.success("Uploaded successfully")