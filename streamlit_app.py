import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

<meta name="viewport" content="width=device-width, initial-scale=1">


# Title and Description
st.title("Raw Material Handling System-PDCT")
st.markdown("This is a web app for the RMHS Team. Team urang Sigat PMB Silicon.")

# Establish Connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("entry-form-rmhs-cleaning-fdf2ac821627.json", scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key("1Vr7HyWgzbCF3rqLKndZHkl2GUdauzsorRObzH5ObkCc")
worksheet_cleaning = spreadsheet.worksheet("CleaningDetail")
worksheet_load_cell = spreadsheet.worksheet("Load Cell Testing")
worksheet_raw_mat = spreadsheet.worksheet("Raw Material Request")

# Function to fetch data from a specific worksheet
def fetch_data(worksheet):
    data = worksheet.get_all_values()
    existing_data = pd.DataFrame(data[1:], columns=data[0])
    # Remove duplicate and empty column names
    existing_data = existing_data.loc[:, ~existing_data.columns.duplicated()]
    existing_data = existing_data.loc[:, existing_data.columns != ""]
    return existing_data

# Function to clear form inputs
def clear_form():
    for key in st.session_state.keys():
        if key.startswith('load_cell_') or key.startswith('raw_mat_') or key.startswith('cleaning_'):
            del st.session_state[key]

# Tabs for different sections
tabs = st.tabs(["Load Cell-Weight Testing", "Raw Mat Request", "Cleaning Team-Data Entry", "Data View"])

# Load Cell-Weight Testing Tab
with tabs[0]:
    st.markdown("### Load Cell-Weight Testing Data")
    form_data_single_row = {}
    form_data_multiple_rows = []

    with st.form(key='load_cell_form'):
        # Text input for Date
        form_data_single_row["Date"] = st.date_input("Date", key="load_cell_date").strftime("%d-%m-%Y")
        # Text input for Boardman Name
        form_data_single_row["Boardman Name"] = st.text_input("Boardman Name", key="load_cell_name")
        # Text input for Phase
        form_data_single_row["Phase"] = st.selectbox("Phase", ["", "1", "2", "3"], key="load_cell_Phase")
        # Text input for SAF
        form_data_single_row["SAF"] = st.selectbox("SAF", ["", "1", "2", "3", "4", "5", "6"], key="load_cell_SAF")

        # Display header for multiple rows
        st.markdown("### Load Cell-Weight Testing Data Entry")
        cols = st.columns(6)
        headers = ["Weighing Bin", "A", "B", "C", "D", "All"]
        for col, header in zip(cols, headers):
            col.markdown(f"**{header}**")

        # Form for multiple rows
        for i in range(4):
            cols = st.columns(6)
            Weighing_Bin = cols[0].selectbox("", ["", "Qtz", "Qtz Add", "RC", "Add Bin", "LS", "CC"], key=f"load_cell_Bin_{i}")
            A = cols[1].text_input("", key=f"load_cell_A_{i}")
            B = cols[2].text_input("", key=f"load_cell_B_{i}")
            C = cols[3].text_input("", key=f"load_cell_C_{i}")
            D = cols[4].text_input("", key=f"load_cell_D_{i}")
            All = cols[5].text_input("", key=f"load_cell_All_{i}")

            if any([Weighing_Bin, A, B, C, D, All]):
                form_data_multiple_rows.append({
                    "Weighing Bin": Weighing_Bin,
                    "A": A,
                    "B": B,
                    "C": C,
                    "D": D,
                    "All": All
                })

        submitted = st.form_submit_button(label='Submit')
        if submitted:
            for data_dict in form_data_multiple_rows:
                combined_data = [form_data_single_row.get(column, "") for column in ["Date", "Boardman Name", "Phase", "SAF"]]
                combined_data.extend([data_dict.get(column, "") for column in headers])
                try:
                    worksheet_load_cell.append_row(combined_data)
                    st.write("Data appended to the worksheet.")
                except Exception as e:
                    st.error(f"An error occurred while appending data to the worksheet: {e}")

            st.success("Data submitted successfully!")
            clear_form()

    load_cell_data = fetch_data(worksheet_load_cell)
    st.write("### Current Load Cell-Weight Testing Data:")
    st.dataframe(load_cell_data)

# Raw Material Request From Warehouse
with tabs[1]:
    st.markdown("### Raw Material Request From Warehouse")
    form_data_single_row = {}
    form_data_multiple_rows = []

    with st.form(key='raw_mat_Request'):
        # Text input for Date
        form_data_single_row["Date"] = st.date_input("Date", key="raw_mat_date").strftime("%d-%m-%Y")
        # Text input for Boardman Name
        form_data_single_row["Boardman Name"] = st.text_input("Boardman Name", key="raw_mat_name")
        # Text input for Phase
        form_data_single_row["Phase"] = st.selectbox("Phase", ["", "1", "2", "3"], key="raw_mat_Phase")
        # Text input for SAF
        form_data_single_row["SAF"] = st.selectbox("SAF", ["", "1", "2", "3", "4", "5", "6"], key="raw_mat_SAF")

        st.markdown("##### Day Bin Quantity")
        cols = st.columns(8)
        headers = ["WC1", "WC2", "QTZ", "RC", "LS", "CC", "Extra", "Extra 2"]
        for col, header in zip(cols, headers):
            col.markdown(f"**{header}**")
        day_bin_data = {}
        for col, header in zip(cols, headers):
            day_bin_data[header] = col.text_input("", key=f"day_bin_{header}")

        st.markdown("##### Raw Material Request Quantity")
        cols = st.columns(8)
        raw_mat_request_data = {}
        for col, header in zip(cols, headers):
            raw_mat_request_data[f"{header}_Req"] = col.text_input("", key=f"raw_mat_{header}_Req")

        st.markdown("##### Warehouse Time Start Sending")
        cols = st.columns(8)
        warehouse_time_data = {}
        for col, header in zip(cols, headers):
            warehouse_time_data[f"{header}_Send"] = col.text_input("", key=f"warehouse_time_{header}_Send")

        submitted = st.form_submit_button(label='Submit')

        if submitted:
            combined_data = [form_data_single_row.get(column, "") for column in ["Date", "Boardman Name", "Phase", "SAF"]]
            combined_data.extend([day_bin_data.get(header, "") for header in headers])
            combined_data.extend([raw_mat_request_data.get(f"{header}_Req", "") for header in headers])
            combined_data.extend([warehouse_time_data.get(f"{header}_Send", "") for header in headers])

            try:
                worksheet_raw_mat.append_row(combined_data)
                st.write("Data appended to the worksheet.")
            except Exception as e:
                st.error(f"An error occurred while appending data to the worksheet: {e}")

            st.success("Data submitted successfully!")
            clear_form()

# Cleaning-Data Entry Tab
with tabs[2]:
    st.markdown("### Cleaning Team- Data Entry")
    form_data_single_row = {}
    form_data_multiple_rows = []

    with st.form(key='cleaning_form'):
        form_data_single_row["Date"] = st.date_input("Date", key="cleaning_date").strftime("%d-%m-%Y")
        form_data_single_row["Team Name"] = st.selectbox("Team Name", ["", "Alpha", "Beta", "Charlie", "Delta"], key="cleaning_team_name")
        form_data_single_row["Team Leader"] = st.text_input("Team Leader", key="cleaning_team_leader")
        form_data_single_row["Manpower"] = st.slider("Manpower", 1, 25, 1, key="cleaning_manpower")

        st.markdown("### Data Entry")
        cols = st.columns(5)
        headers = ["Phase", "SAF", "Area", "Weight (Kg)", "Remarks"]
        for col, header in zip(cols, headers):
            col.markdown(f"**{header}**")

        for i in range(4):
            cols = st.columns(5)
            phase = cols[0].selectbox("", ["", 1, 2, 3], key=f"cleaning_phase_{i}")
            saf = cols[1].selectbox("", ["", 1, 2, 3, 4, 5, 6], key=f"cleaning_saf_{i}")
            area = cols[2].text_input("", key=f"cleaning_area_{i}")
            weight = cols[3].text_input("", key=f"cleaning_weight_{i}")
            remarks = cols[4].text_input("", key=f"cleaning_remarks_{i}")

            if any([phase, saf, area, weight, remarks]):
                form_data_multiple_rows.append({
                    "Phase": phase,
                    "SAF": saf,
                    "Area": area,
                    "Weight (Kg)": weight,
                    "Remarks": remarks
                })

        submitted = st.form_submit_button(label='Submit')

        if submitted:
            for data_dict in form_data_multiple_rows:
                combined_data = [form_data_single_row.get(column, "") for column in ["Date", "Team Name", "Team Leader", "Manpower"]]
                combined_data.extend([data_dict.get(column, "") for column in headers])
                try:
                    worksheet_cleaning.append_row(combined_data)
                    st.write("Data appended to the worksheet.")
                except Exception as e:
                    st.error(f"An error occurred while appending data to the worksheet: {e}")

            st.success("Data submitted successfully!")
            clear_form()

# Data View Tab
with tabs[3]:
    latest_data = fetch_data(worksheet_cleaning)
    st.write("### Current Data:")
    st.dataframe(latest_data)
