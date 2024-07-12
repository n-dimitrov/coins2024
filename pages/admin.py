import streamlit as st
import pandas as pd
import os
import coinsutils as cu

from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.set_page_config(
    page_title="EuroCoins Catalog Admin",
    # page_icon="🧊",
    layout="wide",
)

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]

    return df

def clear_cache():
    if os.path.exists(".cache/catalog.csv"):
        os.remove(".cache/catalog.csv")
    if os.path.exists(".cache/history.csv"):
        os.remove(".cache/history.csv")

st.title('EuroCoins Admin Page')

st.subheader('Catalog')

catalog_df = cu.load_catalog()
history_df = cu.load_history()

f_catalog_df = filter_dataframe(catalog_df)
frame = st.data_editor(
    f_catalog_df,
    hide_index=True,
    column_config={
        "type": st.column_config.TextColumn(label="Type"),
        "year": st.column_config.NumberColumn(label="Year", format="%d"),
        "country": st.column_config.TextColumn(label="Country"),
        "series": st.column_config.TextColumn(label="Series"),
        "value": st.column_config.NumberColumn(label="Value", format="%.2f"),
        "id": st.column_config.TextColumn(label="ID"),
        "image": st.column_config.ImageColumn(label="Image"),
        "feature": st.column_config.TextColumn(label="Feature"),
        "volume": st.column_config.TextColumn(label="Volume")
    },
    disabled=[],
    column_order=('type', 'year', 'country', 'series', 'value', 'id', 'image', 'feature', 'volume'),
    # width=1000,
    )

countries = f_catalog_df['country'].unique()
countries = sorted(countries)
series = f_catalog_df['series'].unique()
series = sorted(series)
st.write('Coins:', len(f_catalog_df), ' Countries:', len(countries), '  Series:', len(series))


st.subheader('History')

names_filter = st.checkbox("By name")
names = history_df['name'].unique()
n = st.selectbox("Name", names)
if names_filter:
    history_df = history_df[history_df['name'] == n]

ff = st.data_editor(
    history_df,
    hide_index=True,
    column_config={
        "name": st.column_config.TextColumn(label="Name"),
        "id": st.column_config.TextColumn(label="ID")
    },
    disabled=[],
    column_order=('name', 'id', 'date'),
    # width=1000,
    )

st.write('History:', len(history_df))

st.subheader('Cache')

st.button('Clear cache', on_click=clear_cache)

