def update_status(file_name, sheet):
    values_list = sheet.get_all_values()
    next_row_index = len(values_list) + 1
    update_data = [file_name, "done"]
    sheet.update(f'A{next_row_index}:B{next_row_index}', [update_data])

def isupdated(current_date, status):
    values_list = status.col_values(1)
    return 1 if current_date in values_list else 0