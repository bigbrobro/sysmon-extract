import streamlit as st
import re
import os

from sysmon_extract.sysmon import extract
from openhunt import ossem

EVENT_DICTIONARY = list(map(str, range(1, 23)))

def start_ui():

    st.title("Sysmon Extractor")
    st.subheader("Extract sysmon data based off the event type")

    st.write("Supported data types are csv, json and parquet.")
    st.write("Load your data by specifying the full path.")

    st.info("HDFS is supported. Specify hdfs://HOST:PORT/path/to/file for either input or outputh path.")

    up_file = st.text_input("Input File:")

    if up_file is not None:
        if ".csv" in up_file:
            headers = st.checkbox(
                "For csv files if the first row contains headers?",
                value=True)
        else:
            headers = False

    st.write("Specify the output path below. If writing to a local directory, the full path must be specified. If no path is provided, it will write the file to the current working directory.")
    out_file = st.text_input("Output file")

    st.write("If you have multiple log sources in one file, please enter the column that specifies the log source for each row.")
    log_col = st.text_input("Log name columns:")

    st.write("If your Sysmon data is nested in another column, please enter the column below.")
    event_col = st.text_input("Event column: ")

    selection = st.multiselect(
        "Select events to extract",
        EVENT_DICTIONARY
    )

    st.write("If you want to extract any other columns from the data, specify them below separated by a comma")
    additional_cols = st.text_area("Additional columns", "col1, col2.nested_col")

    st.write("If you want the resulting file as a single file, check the box below.")
    st.warning(
        "Make sure that you have enough memory to fit the data into memory, otherwise this will fail")
    single_file = st.checkbox("Output as a single file", value=False)

    st.write("If you have an existing spark cluster you would like to connect to, enter it below.")
    st.info("For a cluster, spark://HOST:PORT, for a mesos/yarn cluster mesos://HOST:PORT")
    master = st.text_input("Spark Instance", "local")

    if st.button("Extract!"):

        assert up_file, st.write("Must choose a file for upload.")
        assert selection, st.write("Please select rules you would like to extract")

        # Assign default values
        # master = "local" if not master else master
        additional_cols = re.sub(r"\s+", "", additional_cols).split(",")
        out_file = f"{os.getcwd()}/sysmon-output.csv" if not out_file else out_file

        with st.spinner(text="Extracting logs..."):
            extract(
                up_file.strip(),
                selection,
                out_file,
                header=headers,
                log_column=log_col,
                event_column=event_col,
                additional_columns=additional_cols,
                single_file=single_file,
                master=master
            )

        st.success("Done!")
        st.balloons()

    st.header("Event Dictionary Help")
    st.subheader("Display the schema information for each Sysmon rule")

    event = st.selectbox("Select an event.", EVENT_DICTIONARY)

    df = ossem.getEventDf("windows", "sysmon", f"event-{event}")

    st.table(df[["event_code", "title", "name",
                "type", "description", "sample_value"]])

if __name__ == "__main__":
    start_ui()
