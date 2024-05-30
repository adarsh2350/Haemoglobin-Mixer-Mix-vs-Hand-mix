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
from datetime import datetime


def main():

    # Connecting sheets
    SERVICE_ACCOUNT_FILE = 'mobilabhemoglobinhandvsmixer-215a0e65c2f2.json'
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open('GNRC_info')
    info = spreadsheet.get_worksheet(0)

    
    st.title("Sample ID Extractor")

    uploaded_file = st.file_uploader("Choose a zip file", type="zip")

    if uploaded_file is not None:
        with zipfile.ZipFile(uploaded_file, 'r') as z:
            z.extractall('temp_dir')

            uploaded_zip_date = os.path.basename(uploaded_file.name).split('.')[0]

            temp_dir = 'temp_dir'
            for items in os.listdir(temp_dir):
                if items == uploaded_zip_date:  
                    if st.button("Extract"):
                        for item in os.listdir(os.path.join(temp_dir, items)):
                            file_path = os.path.join(temp_dir, items, item)
                            if os.path.isfile(file_path):
                                    date = items
                                    sample_id = file_path[29:34]

                                    suffixes = [".", "t", "xt", "txt", ".txt"]
                                    for suffix in suffixes:
                                        if sample_id.endswith(suffix):
                                            sample_id =  sample_id[:-len(suffix)]
                                    info.append_row([date, sample_id])
                                    info.sort((1, 'asc'))
                                    st.success('Extracted successfully')
                            

            


def GNRC():
    main()