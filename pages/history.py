import streamlit as st
import pandas as pd
import coinsutils as cu

st.set_page_config(
    page_title="EuroCoins Catalog History",
    # page_icon="🧊",
    # layout="wide",
)

st.page_link("coins.py", label=":arrow_backward: Back")

catalog_df = cu.load_catalog()
history_df = cu.load_history()
history_sorted_df = history_df.sort_values(by=['name','date'], ascending=True)
history_df_grouped_id = history_sorted_df.groupby('id').agg({'name': lambda x: list(x)}).reset_index()

history_df['date'] = pd.to_datetime(history_df['date'], errors='coerce')
history_df['date_only'] = history_df['date'].dt.date

st.subheader('History')

history_df_grouped_date = history_df.groupby(['date_only', 'name']).agg({
        'id': lambda x: list(x)  
}).reset_index()
history_df_grouped_date = history_df_grouped_date.sort_values(by=['date_only', 'name'], ascending=False)

# iterate over the rows
for row in history_df_grouped_date.itertuples():
    d = row.date_only
    owner = row.name
    ids = row.id
    
    date = d.strftime('%d %B %Y')
    st.write(f"#### {owner} @ {date}")

    data = {
        'country': [],
        'series': [],
        'year': [],
        'image': [],
        'value': [],
        'type': []
    }

    for i in ids:
        coin = catalog_df[catalog_df['id'] == i]
        data['country'].append(coin['country'].values[0])
        data['series'].append(coin['series'].values[0])
        data['year'].append(coin['year'].values[0])
        data['value'].append(coin['value'].values[0])
        data['type'].append(coin['type'].values[0])
        data['image'].append(coin['image'].values[0])

    df = pd.DataFrame(data)

    frame = st.data_editor(
        df,
        key=f"history_{date}_{owner}",
        hide_index=True,
        column_config={
            "type": st.column_config.TextColumn(label="Type"),
            "year": st.column_config.NumberColumn(label="Year", format="%d"),
            "country": st.column_config.TextColumn(label="Country"),
            "series": st.column_config.TextColumn(label="Series"),
            "value": st.column_config.NumberColumn(label="Value", format="%.2f"),
            "image": st.column_config.ImageColumn(label="Image")
        },
        disabled=[],
        column_order=('type', 'year', 'country', 'series', 'value', 'image'),
        # width=1000,
        )

