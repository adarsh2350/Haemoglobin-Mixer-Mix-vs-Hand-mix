import re
import pandas as pd
import math
from functions.stat import mod_avg

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