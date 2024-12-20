from typing import Tuple, Optional
from etl import get_station_measurements
from stations import get_stations_uuid
from plot import plot_detection, plot_reference_data
from sklearn.neighbors import LocalOutlierFactor
import pandas as pd
import streamlit as st


@st.cache_data(ttl="20m")
def detection(df_ref: pd.DataFrame, df_pred: pd.DataFrame) -> pd.DataFrame:
    print("Running detection ...")

    assert "value" in df_ref, "Could not find 'value' among columns."
    assert "value" in df_pred, "Could not find 'value' among columns."

    # Initialize the novelty detection ML algorithm
    clf = LocalOutlierFactor(n_neighbors=2, novelty=True)

    # Feed the reference measurements to the ML model
    clf.fit(df_ref["value"].values.reshape(-1, 1))

    # Add a new column to the data frame holding the detection results (1 --> normal, -1 --> abnormal)
    df_pred["novelty"] = clf.predict(df_pred["value"].values.reshape(-1, 1))

    return df_pred


@st.cache_data(ttl="30m")
def get_station_data(
    uuid: str,
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    print(f"Getting latest station data with id: {uuid} ...")

    # Retrieve data for the selected station
    df_ref, df_pred = get_station_measurements(
        uuid=uuid, reference_window="PT6H", prediction_window="PT1H"
    )

    return df_ref, df_pred


st.set_page_config(layout="wide")
st.title("Novelty Detection for Water Level")

col1, col2 = st.columns(2)


# Select station uuid
uuid = st.selectbox("Station UUID", get_stations_uuid())

# Retrieve data for the selected station (reference + prediction)
df_ref, df_pred = get_station_data(uuid=uuid)

if df_pred is None or df_ref is None:
    st.write(
        "There are no new measurements for the requested station. "
        "Please try agian later!"
    )
else:
    st.write("Fetching new measurements successful!")
    df_pred = detection(df_ref=df_ref, df_pred=df_pred)
    fig_pred = plot_detection(df=df_pred)
    st.pyplot(fig_pred, use_container_width=True)
    fig_ref = plot_reference_data(df=df_ref)
    st.pyplot(fig_ref, use_container_width=True)
