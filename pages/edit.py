import pandas as pd
import streamlit as st

catalog_file = st.file_uploader("Choose a Catalog file",type="csv")
if catalog_file is not None:
    df = pd.read_csv(catalog_file)

    st.subheader('Catalog')

    df = st.data_editor(
        df,
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
    
    if st.button('Save'):
        df.to_csv("catalog-new.csv", index=False, sep=',', encoding='utf-8')