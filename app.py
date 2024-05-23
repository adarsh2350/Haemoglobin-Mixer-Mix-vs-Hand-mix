import re
import os
import pandas as pd
from collections import Counter
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import math
import zipfile
from io import BytesIO

# Calulating mod avg.
def mod_avg(numbers):
    frequency = Counter(numbers)
    max_frequency = max(frequency.values())
    modes = [num for num, freq in frequency.items() if freq == max_frequency]
    average_mode = sum(modes) / len(modes)
    return int(average_mode)

def parse_file(file_path, date, df, haemoglobin_sample, factor):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    sample_id = file_path[29:34]
    device_id = re.search(r'Device ID:(\w+)', lines[1]).group(1)
    base_readings = []
    test_readings = []
    current_case = None
    repetition_no = None
    collecting_test_data = False

    for i, line in enumerate(lines):
        if 'Collecting base data' in line:
            for j in range(i + 1, i + 16):
                base_readings.append(int(lines[j].split(',')[0]))

        elif 'Repetition No. :' in line:
            repetition_no = int(line.split(':')[1].strip())

        elif '[Mixer Mix]' in line:
            current_case = 'Mixer Mix'
            collecting_test_data = True

        elif '[Hand-MIX]' in line:
            current_case = 'Hand Mix'
            collecting_test_data = True

        elif 'Collecting test data' in line:
            if collecting_test_data:
                for j in range(i + 1, i + 181):
                    test_readings.append(int(lines[j].split(',')[0]))

                # Extracting the numeric part of the sample ID
                numeric_sample_id = re.search(r'\d+', sample_id).group(0)

                # Adding sample id, device id, date, repetition no., case
                row = {
                    'Sample ID': sample_id,
                    'Device ID': device_id,
                    'Date': date,
                    'Repetition No.': repetition_no,
                    'Case': current_case
                }

                # Adding mod_avg_base_data
                row.update({f'base_data_mod_avg': mod_avg(base_readings)})
                # Adding mod_avg_test_data
                row.update({f'test_data_mod_avg': mod_avg(test_readings[-15:])})
                # Adding actual conc.
                row.update({f'actual': haemoglobin_sample[int(numeric_sample_id) + 1]})
                # Adding absorption
                row.update({f'absorption': round(math.log10(row['base_data_mod_avg'] / row['test_data_mod_avg']), 4)})
                # Adding concentration
                row.update({f'concentration': round(factor * row['absorption'], 2)})
                # Adding error%
                row.update({f'error%': round((abs(float(row['actual']) - row['concentration']) / float(row['actual'])) * 100, 2)})
                # Adding base readings
                row.update({f'Base Data {i + 1}': base_readings[i] for i in range(15)})
                # Adding test readings
                row.update({f'Test Data {i + 1}': test_readings[i] for i in range(180)})

                temp_df = pd.DataFrame([row])
                df = pd.concat([df, temp_df], ignore_index=True)
                collecting_test_data = False
                test_readings = []

    return df

def main():
    factor = st.number_input('Enter the factor value:', value=1.0, format="%.2f")

    st.title("Zip File Processor")

    uploaded_file = st.file_uploader("Choose a zip file", type="zip")

    if uploaded_file is not None:
        with zipfile.ZipFile(uploaded_file, 'r') as z:
            z.extractall('temp_dir')

        # Connecting sheets
        SERVICE_ACCOUNT_FILE = 'mobilabhemoglobinhandvsmixer-215a0e65c2f2.json'
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(credentials)

        spreadsheet1 = gc.open('Haemoglobin Sample ID info')
        sheet1 = spreadsheet1.sheet1
        haemoglobin_sample = sheet1.col_values(17)

        spreadsheet2 = gc.open('sample')
        output_sheet = spreadsheet2.sheet1

        base_data_columns = [f'Base Data {i + 1}' for i in range(15)]
        test_data_columns = [f'Test Data {i + 1}' for i in range(180)]
        columns = ['Sample ID', 'Device ID', 'Date', 'Repetition No.', 'Case'] + ['base_data_mod_avg', 'test_data_mod_avg', 'actual', 'absorption', 'concentration', 'error%'] + base_data_columns + test_data_columns
        df = pd.DataFrame(columns=columns)

        temp_dir = 'temp_dir'
        for items in os.listdir(temp_dir):
            for item in os.listdir(os.path.join(temp_dir, items)):
                file_path = os.path.join(temp_dir, items, item)
                if os.path.isfile(file_path):
                    date = items
                    df = parse_file(file_path, date, df, haemoglobin_sample, factor)

        st.subheader("Processed DataFrame:")
        st.dataframe(df)

        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        st.download_button(
            label="Download Excel file",
            data=output.getvalue(),
            file_name=f"{os.listdir(temp_dir)[0]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
