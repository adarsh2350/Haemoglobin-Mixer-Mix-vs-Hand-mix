import re
import os
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import zipfile
from io import BytesIO
import matplotlib.pyplot as plt
from functions.upload import upload_to_sheet
from functions.plot import plots
from functions.status import update_status, isupdated
from functions.parse import parse_file
from functions.report import create_report


def main():

    # Connecting sheets
    SERVICE_ACCOUNT_FILE = 'mobilabhemoglobinhandvsmixer-215a0e65c2f2.json'
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    spreadsheet1 = gc.open('GNRC_info')
    spreadsheet2 = gc.open('Haemoglobin extracted data')
    
    sheet1 = spreadsheet1.sheet1
    haemoglobin_sample = sheet1.col_values(2)
    actual_val = sheet1.col_values(3)
    extraction_sheet = spreadsheet2.get_worksheet(0)  
    report = spreadsheet2.get_worksheet(1)
    status = spreadsheet2.get_worksheet(2)



    # Creating report
    if st.button("Update Report"):
        create_report(extraction_sheet, report)
        st.success('Report updated')



    factor = st.number_input('Enter the factor value:', value=1.0, format="%.2f")

    st.title("Zip File Processor")

    uploaded_file = st.file_uploader("Choose a zip file", type="zip")

    if uploaded_file is not None:
        with zipfile.ZipFile(uploaded_file, 'r') as z:
            z.extractall('temp_dir')

        # Extract the uploaded zip file date
        uploaded_zip_date = os.path.basename(uploaded_file.name).split('.')[0]
        current_date = uploaded_file.name[0:7]
        day, month, year = current_date.split('-')
        year = '20' + year
        current_date = f'{year}-{month.zfill(2)}-{day.zfill(2)}'
        
        isUpdated = False

        # check status
        isUpdated = isupdated(current_date, status)

        base_data_columns = [f'Base Data {i + 1}' for i in range(15)]
        test_data_columns = [f'Test Data {i + 1}' for i in range(180)]
        columns = ['Sample ID', 'Device ID', 'Date', 'Repetition No.', 'Case'] + ['base_data_mod_avg', 'test_data_mod_avg', 'actual', 'absorption', 'concentration', 'error%'] + base_data_columns + test_data_columns
        df = pd.DataFrame(columns=columns)

        temp_dir = 'temp_dir'
        for items in os.listdir(temp_dir):
            if items == uploaded_zip_date:  
                for item in os.listdir(os.path.join(temp_dir, items)):
                    file_path = os.path.join(temp_dir, items, item)
                    if os.path.isfile(file_path):
                        date = items
                        df = parse_file(file_path, date, df, haemoglobin_sample, actual_val, factor)

        st.subheader("Processed DataFrame:")
        st.dataframe(df)

        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        st.download_button(
            label="Download Excel file",
            data=output.getvalue(),
            file_name=f"{uploaded_zip_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


        # Plotting graph
        df['actual'] = df['actual'].astype(float)

        # Calculate the average absorption and concentration for each actual value
        df_avg = df.groupby(['actual', 'Case']).agg({'absorption': 'mean', 'concentration': 'mean'}).reset_index()

        df_mixer = df_avg[df_avg['Case'] == 'Mixer Mix']
        df_hand = df_avg[df_avg['Case'] == 'Hand Mix']

        unique_actual_sorted = sorted(df_avg['actual'].unique())
        st.title("Scatter Plots of Absorption and Concentration vs Actual")
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        fig4, ax4 = plt.subplots(figsize=(6, 4))

        # Plot for Mixer Mix - Absorption vs Actual
        plots(ax1, df_mixer['actual'], df_mixer['absorption'], 'Mixer Mix - Absorption vs Actual', 'Actual', 'Absorption', 'blue')
        ax1.set_xticks(unique_actual_sorted)
        st.pyplot(fig1)

        # Plot for Mixer Mix - Concentration vs Actual
        plots(ax2, df_mixer['actual'], df_mixer['concentration'], 'Mixer Mix - Concentration vs Actual', 'Actual', 'Concentration', 'green')
        ax2.set_xticks(unique_actual_sorted)
        st.pyplot(fig2)

        # Plot for Hand Mix - Absorption vs Actual
        plots(ax3, df_hand['actual'], df_hand['absorption'], 'Hand Mix - Absorption vs Actual', 'Actual', 'Absorption', 'red')
        ax3.set_xticks(unique_actual_sorted)
        st.pyplot(fig3)

        # Plot for Hand Mix - Concentration vs Actual
        plots(ax4, df_hand['actual'], df_hand['concentration'], 'Hand Mix - Concentration vs Actual', 'Actual', 'Concentration', 'orange')
        ax4.set_xticks(unique_actual_sorted)
        st.pyplot(fig4)


        # Outputs   
        if st.button("Upload Data"):
            if isUpdated == 0:
                upload_to_sheet(df, extraction_sheet)
                update_status(current_date, status)
            else :
                st.warning("Data already exists. Skipping upload.")



def extraction():
    main()

