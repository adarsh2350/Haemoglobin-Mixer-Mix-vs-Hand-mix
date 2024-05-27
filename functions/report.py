import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
import streamlit as sns

def create_report(data, report):
    df = data.get_all_values()
    df = pd.DataFrame(df[1:], columns=df[0])

    df['error%'] = pd.to_numeric(df['error%'])
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%y')

    hand_mix_avg_error = df[df['Case'] == 'Hand Mix'].groupby(df['Date'].dt.date)['error%'].mean().round(2)
    mixer_mix_avg_error = df[df['Case'] == 'Mixer Mix'].groupby(df['Date'].dt.date)['error%'].mean().round(2)

    avg_error_df = pd.DataFrame({
        'Date': hand_mix_avg_error.index,
        'avg. error%(Hand mix)': hand_mix_avg_error.values,
        'avg. error%(Mix mix)': mixer_mix_avg_error.values
    })

    overall_avg_error_hand = df[df['Case'] == 'Hand Mix']['error%'].mean().round(2)
    overall_avg_error_mixer = df[df['Case'] == 'Mixer Mix']['error%'].mean().round(2)

    avg_error_df['Date'] = avg_error_df['Date'].astype(str)

    df['binary_error'] = df['error%'] < 10

    hand_mix = df[df['Case'] == 'Hand Mix']
    hand_tp = (hand_mix['binary_error'] == 1).sum()
    hand_tn = (hand_mix['binary_error'] == 0).sum()
    hand_fp = (hand_mix['binary_error'] == 0).sum()
    hand_fn = (hand_mix['binary_error'] == 1).sum()
    
    hand_se = hand_tp / (hand_tp + hand_fn) if (hand_tp + hand_fn) != 0 else 0
    hand_sp = hand_tn / (hand_tn + hand_fp) if (hand_tn + hand_fp) != 0 else 0
    hand_ppv = hand_tp / (hand_tp + hand_fp) if (hand_tp + hand_fp) != 0 else 0
    hand_npv = hand_tn / (hand_tn + hand_fn) if (hand_tn + hand_fn) != 0 else 0
    hand_da = (hand_tp + hand_tn) / len(hand_mix) if len(hand_mix) != 0 else 0


    mixer_mix = df[df['Case'] == 'Mixer Mix']
    mixer_tp = (mixer_mix['binary_error'] == 1).sum()
    mixer_tn = (mixer_mix['binary_error'] == 0).sum()
    mixer_fp = (mixer_mix['binary_error'] == 0).sum()
    mixer_fn = (mixer_mix['binary_error'] == 1).sum()
    
    mixer_se = mixer_tp / (mixer_tp + mixer_fn) if (mixer_tp + mixer_fn) != 0 else 0
    mixer_sp = mixer_tn / (mixer_tn + mixer_fp) if (mixer_tn + mixer_fp) != 0 else 0
    mixer_ppv = mixer_tp / (mixer_tp + mixer_fp) if (mixer_tp + mixer_fp) != 0 else 0
    mixer_npv = mixer_tn / (mixer_tn + mixer_fn) if (mixer_tn + mixer_fn) != 0 else 0
    mixer_da = (mixer_tp + mixer_tn) / len(mixer_mix) if len(mixer_mix) != 0 else 0

    # Prepare the report data
    report_data = [
        ['Date', 'avg. error%(Hand mix)', 'avg. error%(Mix mix)'],
        *avg_error_df.values.tolist(),
        [],
        ['Metric', 'Hand Mix', 'Mixer Mix'],
        ['Avg. error%', overall_avg_error_hand, overall_avg_error_mixer],
        ['Sensitivity (Se)', hand_se, mixer_se],
        ['Specificity (Sp)', hand_sp, mixer_sp],
        ['Positive Predictive Value (PPV)', hand_ppv, mixer_ppv],
        ['Negative Predictive Value (NPV)', hand_npv, mixer_npv],
        ['Diagnostic Accuracy (DA)', hand_da, mixer_da]
    ]

    report.clear()
    report.update(report_data)

 