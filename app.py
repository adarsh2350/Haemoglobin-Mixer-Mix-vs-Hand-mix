import streamlit as st
import zipfile
import re
import os
import pandas as pd
from io import BytesIO
from statistics import mode

def parse_file(file_path, date, df):
    
    with open(file_path, 'r') as file:
        lines = file.readlines()

    sample_id = file_path[26:34]
    device_id = re.search(r'Device ID:(\w+)', lines[1]).group(1)
    base_readings = []
    test_readings = []
    current_case = None
    repetition_no = None
    collecting_test_data = False
    
    for i, line in enumerate(lines):

        if 'Collecting base data' in line:
            for j in range(i + 1, i + 16):
                base_readings = [int(lines[j].split(',')[0]) for j in range(i + 1, i + 16)]

        
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
                    test_readings = [int(lines[j].split(',')[0]) for j in range(i + 1, i + 181)]

    
                row = {
                    'Sample ID': sample_id,
                    'Device ID': device_id,
                    'Date': date,
                    'Repetition No.': repetition_no,
                    'Case': current_case
                }
                    
                row.update({f'Base Data {i+1}': base_readings[i] for i in range(15)})
                row.update({f'Test Data {i+1}': test_readings[i] for i in range(180)})
                row.update({f'base_data_mod_avg': mode(base_readings)})
                row.update({f'test_data_mod_avg': mode(test_readings[-15:])})
                temp_df = pd.DataFrame([row])
                
                df = pd.concat([df, temp_df], ignore_index=True)

                collecting_test_data = False
                test_readings = []
    return df




def main():
    st.title("Zip File Processor")

    uploaded_file = st.file_uploader("Choose a zip file", type="zip")
    
    if uploaded_file is not None:
        with zipfile.ZipFile(uploaded_file, 'r') as z:
            z.extractall('temp_dir')

        base_data_columns = [f'Base Data {i+1}' for i in range(15)]
        test_data_columns = [f'Test Data {i+1}' for i in range(180)]
        columns = ['Sample ID', 'Device ID', 'Date', 'Repetition No.', 'Case'] + base_data_columns + test_data_columns + ['base_data_mod_avg', 'test_data_mod_avg']
        df = pd.DataFrame(columns=columns)

        temp_dir = 'temp_dir'
        for items in os.listdir(temp_dir):
            for item in os.listdir(os.path.join(temp_dir, items)):
                file_path = os.path.join(temp_dir, items, item)
                if os.path.isfile(file_path):  
                    date = items  
                    df = parse_file(file_path, date, df)
        
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
