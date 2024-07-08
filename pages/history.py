import streamlit as st
import pandas as pd
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
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
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


history_df = pd.read_csv('history.csv')
history_df['date'] = pd.to_datetime(history_df['date'], format='%Y-%m-%d %H:%M:%S')

catalog_df = pd.read_csv('catalog.csv')
catalog_df['year'] = catalog_df['year'].astype(int)

df = pd.DataFrame(columns=["name", "type", "year", "country", "series", "value", "id", "image", "date"])
df['year'] = df['year'].astype(int)

# iterate over the history data
newrows = []
for index, row in history_df.iterrows():
    name = row['name']
    id = row['id']
    date = row['date']

    type = ""
    year = 0
    country = ""
    series = ""
    value = ""
    image = ""

    # find the coin in the catalog by id
    coin = catalog_df[catalog_df['id'] == id]
    if not coin.empty:
        type = coin['type'].values[0]
        year = coin['year'].values[0]
        country = coin['country'].values[0]
        series = coin['series'].values[0]
        value = coin['value'].values[0]
        image = coin['image'].values[0]
    else:
        print("Coin not found in catalog: " + id)
    
    row = {
        "name": name,
        "type": type,
        "year": year,
        "country": country,
        "series": series,
        "value": value,
        "id": id,
        "image": image,
        "date": date
    }
    newrows.append(row)

new_rows_df = pd.DataFrame(newrows)
df = pd.concat([df, new_rows_df], ignore_index=True)

print(df)

f_df = filter_dataframe(df)

frame = st.data_editor(
    f_df,
    hide_index=True,
    column_config={
        "name": st.column_config.TextColumn(label="Name"),
        "type": st.column_config.TextColumn(label="Type"),
        "year": st.column_config.NumberColumn(label="Year", format="%d", min_value=1999, max_value=2024, step=1),
        "country": st.column_config.TextColumn(label="Country"),
        "series": st.column_config.TextColumn(label="Series"),
        "value": st.column_config.NumberColumn(label="Value", format="%.2f"),
        "id": st.column_config.TextColumn(label="ID"),
        "image": st.column_config.ImageColumn(label="Image"),
        "date": st.column_config.DatetimeColumn(label="Date"),
    },
    disabled=['id'],
    column_order=('name', 'type', 'year', 'country', 'series', 'value', 'image', 'date'),
    # width=1000,
    )

s_coins = f_df['id'].unique()
s_coins = sorted(s_coins)

s_countries = f_df['country'].unique()
s_countries = sorted(s_countries)

s_series = f_df['series'].unique()
s_series = sorted(s_series)

st.write("Total: ", len(f_df), "Coins: ", len(s_coins), " Countries: ", len(s_countries), " Series: ", len(s_series))


