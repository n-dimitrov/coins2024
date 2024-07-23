import base64
import streamlit as st
import pandas as pd
from PIL import Image
from openai import OpenAI
import os
import json
import coinsutils as cu

# open_ai_key = os.getenv("OPENAI_API_KEY")
open_ai_key = st.secrets.get("OPENAI_API_KEY")

def init_coins():
    if 'catalog_df' not in st.session_state:
         st.session_state.catalog_df = cu.load_catalog()
    if 'history_df' not in st.session_state:
        st.session_state.history_df = cu.load_history()

    catalog_df = st.session_state.catalog_df
    history_df = st.session_state.history_df

    history_sorted_df = history_df.sort_values(by=['name','date'], ascending=True)
    history_df_grouped_id = history_sorted_df.groupby('id').agg({'name': lambda x: list(x)}).reset_index()

    history_df['date'] = pd.to_datetime(history_df['date'], errors='coerce')
    history_df.loc[:, 'date_only'] = history_df['date'].dt.date
    
    coins_df = pd.DataFrame()
    coins_df = pd.merge(catalog_df, history_df_grouped_id, on='id', how='outer')
    coins_df['names'] = coins_df['name'].apply(lambda x: x if isinstance(x, list) else [])
    coins_df['owners'] = coins_df['names'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    coins_df.drop(columns=['name'], inplace=True)
    coins_df['feature'] = coins_df['feature'].fillna('')
    coins_df['volume'] = coins_df['volume'].fillna('')
    users_list = sorted(history_df['name'].unique())

    st.session_state.coins_df = coins_df
    st.session_state.users_list = users_list

def display_coin_card(coin, current_user):
    country = coin.country
    value = coin.value
    image = coin.image
    series = coin.series
    year = coin.year
    info = coin.feature
    owners_count = coin.owners
    owners_names = coin.names

    value = f"{value:.2f} €"
    with st.container(border=True):
        flag_emoji = cu.flags.get(country, "")

        st.write(f"{flag_emoji} {country}")
        st.write(f"{series}")
        st.image(image)
        st.write(f"{value} / {year}")
        st.write(info)

        pop = st.popover(f"Owners {owners_count}")
        with pop:
            if owners_count > 0:
                for name in owners_names:
                    st.write(name)


st.title('AI Coin search')

uploaded_file = st.file_uploader("Choose a coin image")
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    uploaded_file.seek(0)
    base64_image = base64.b64encode(uploaded_file.read()).decode('utf-8')

#     result = """
# { "country": "Andorra", "year": "n/a", "value": "n/a", "type": "regular", "description": "This is a 0.01 Euro coin from Andorra, dated 2014. The design features a Pyrenean chamois and a bearded vulture, symbols representative of the fauna in Andorra, surrounded by the twelve stars of the European Union." }
# """
    result = "{}"

    if st.button('Search'):
        with st.spinner('Analizying...'):
            client = OpenAI(api_key=open_ai_key)

            response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                "role": "system",
                "content": "You are a helpful assistant. I am a coin expert. I can help you identify coins. Please provide me with an image of the coin you would like me to identify. Responses are in json format contains the country, year, value (0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.00, 2.00), type - regural or commemorative and description. Use n/a if not applicable.",
                },
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What coin is this? "},
                    {
                    "type": "image_url",
                    "image_url": {
                        # "url": "https://www.ecb.europa.eu/euro/coins/comm/html/comm_2022/0416-23r.jpg",
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                    },
                ],
                }
            ],
            max_tokens=1000,
            response_format={ "type": "json_object" }
            )

            # st.write(response)
            result = response.choices[0].message.content

            st.write("Possible result:")
            st.info(result)

            json_result = json.loads(result)

            with st.spinner('Searching in catatlog...'):
                init_coins()
                coins_df = st.session_state.coins_df

                country = json_result['country']
                if country != 'n/a':
                    coins_df = coins_df[coins_df['country'] == country]   
                year = json_result['year']
                if year != 'n/a':
                    y = int(year)
                    coins_df = coins_df[coins_df['year'] == y]
                value = json_result['value']
                if value != 'n/a':
                    v = float(value)
                    coins_df = coins_df[coins_df['value'] == v]
                coin_type = json_result['type']
                if coin_type != 'n/a':
                    t = "CC" if coin_type == 'commemorative' else "RE"
                    coins_df = coins_df[coins_df['type'] == t]

                description = json_result['description']
                
                with st.expander("Details"):
                    st.write("Country: ", country)
                    st.write("Year: ", year)
                    st.write("Value: ", value)
                    st.write("Type: ", t)
                    st.write("Description: ", description)

                st.write("Matching coins: ", len(coins_df))
                
                for index, row in coins_df.iterrows():
                    display_coin_card(row, "-")








   