import streamlit as st
import pandas as pd
from itertools import islice
import coinsutils as cu

def save_history():
    print("Saving history")
    history_df = st.session_state.history_df
    history_df.to_csv('.cache/history.csv', index=False)
    cu.upload_file_to_s3('.cache/history.csv', 'history.csv')

def add_coin(coin_id, name, date=None):
    print("Add coin to history: ", name, coin_id)
    if (date is None):
        date = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = {'name': name,'id': coin_id, 'date':date}
    new_df = pd.DataFrame([new_row])

    history_df = st.session_state.history_df
    history_df = pd.concat([history_df, new_df], ignore_index=True)
    st.session_state.history_df = history_df
    save_history()

def remove_coin(coin_id, name):
    print("Remove coin from history: ", name, coin_id)
    df = st.session_state.history_df
    df = df[~((df['name'] == name) & (df['id'] == coin_id))]
    st.session_state.history_df = df
    save_history()

def init_coins():
    if 'catalog_df' not in st.session_state:
         st.session_state.catalog_df = cu.load_catalog()
    if 'history_df' not in st.session_state:
        st.session_state.history_df = cu.load_history()

    catalog_df = st.session_state.catalog_df
    history_df = st.session_state.history_df

    history_sorted_df = history_df.sort_values(by=['name','date'], ascending=True)
    history_df_grouped = history_sorted_df.groupby('id').agg({'name': lambda x: list(x)}).reset_index()

    coins_df = pd.DataFrame()
    coins_df = pd.merge(catalog_df, history_df_grouped, on='id', how='outer')
    coins_df['names'] = coins_df['name'].apply(lambda x: x if isinstance(x, list) else [])
    coins_df['owners'] = coins_df['names'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    coins_df.drop(columns=['name'], inplace=True)

    users_list = history_df['name'].unique()

    st.session_state.coins_df = coins_df
    st.session_state.users_list = users_list


st.set_page_config(
    page_title="EuroCoins Catalog",
    page_icon="🟡",
    layout="wide",
)

def batched(iterable, n_cols):
    if n_cols < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n_cols)):
        yield batch

###
# Coin card
###
def display_coin_card(coin, current_user):
    country = coin.country
    value = coin.value
    image = coin.image
    series = coin.series
    year = coin.year
    info = coin.feature
    owners_count = coin.owners
    own = coin.own
    owners_names = coin.names

    value = f"{value:.2f} €"
    with st.container(border=True):
        flag_emoji = cu.flags.get(country, "")

        st.write(f"{flag_emoji} {country}")
        pr = 0.0
        if own == 1:
            pr = 1.0

        st.progress(pr)
        st.image(image)
        st.write(f"{value} / {year}")
        expander = st.expander(f"Owners {owners_count}")
        with expander:
            if owners_count > 0:
                for name in owners_names:
                    if name == current_user:
                        name = f":green[{name}]"
                    st.write(name)
            if current_user:
                if own == 0:
                    label = "Add :green[:heavy_plus_sign:]"
                    st.button(label, key=f"add_{coin.id}", on_click=add_coin, args=[coin.id, current_user])
                        
                else:
                    label = "Del :red[:heavy_minus_sign:]"
                    st.button(label, key=f"remove_{coin.id}", on_click=remove_coin, args=[coin.id, current_user])

###
# Series container
###
def series_head(series, name, series_coins_count, own_count):
    series_name = cu.series_names_info.get(series, series)
    st.subheader(f"{series_name}")
        
    series_progress = own_count / series_coins_count
    with st.container(border=True):
        c1, c2 = st.columns([1,8])
        c2.progress(series_progress)
        c1.write(f"{own_count} / {series_coins_count}")

st.markdown("""
<style>
.stProgress .st-e4 {
    background-color: green;
}
</style>
""", unsafe_allow_html=True)

st.header("EuroCoins Catalog")

with st.spinner("Loading..."):
    init_coins()

coins_df = st.session_state.coins_df

users_list = st.session_state.users_list
total_users = len(users_list)

col1, col2 = st.columns([1, 6])

with col1:
    st.write("Filters")

    with st.container(border=True):
        user_filter = st.checkbox("By user")
        current_user = st.selectbox("User", users_list)
        if not user_filter:
            current_user = None
        
        user_filter = st.selectbox("Coins", ["All", "Found", "Missing"])

    with st.container(border=True):
        selected_regular = st.checkbox("Regular", value=True)
        selected_commemorative = st.checkbox("Commemorative", value=False)
        if selected_regular:
            coins_df = coins_df[coins_df['type'] == 'RE']
        if selected_commemorative:
            coins_df = coins_df[coins_df['type'] == 'CC']

    with st.container(border=True):
        country_filter = st.checkbox("By country")
        countries_list = coins_df['country'].unique()
        countries_list = sorted(countries_list)
        country = st.selectbox("Country", countries_list)
        if country_filter:
            coins_df = coins_df[coins_df['country'] == country]   

    with st.container(border=True):
        series_filter = st.checkbox("By series", value=False)
        series_list = coins_df['series'].unique()
        series_list = sorted(series_list)

        series = st.selectbox("Series", series_list)
        if series_filter:
            coins_df = coins_df[coins_df['series'] == series]
    
with col2:
    sorted_df = coins_df.sort_values(by=['country', 'value'])

    grouped = sorted_df.groupby('series')
    dfs = {series: group.reset_index(drop=True) for series, group in grouped}

    name_to_check = "-"
    if current_user:
        name_to_check = current_user

    for series, df_group in dfs.items():
        with st.container(border=True):

            series_coins_count = len(df_group)
            df_group = df_group.sort_values(by=['country', 'value'])
            df_group['own'] = df_group['names'].apply(lambda x: 1 if name_to_check in x else 0)

            if (current_user):
                if user_filter == "Found":
                    df_group = df_group[df_group['own'] == 1]
                elif user_filter == "Missing":
                    df_group = df_group[df_group['own'] == 0]

            own_count = df_group['own'].sum()
            
            series_head(series, current_user, series_coins_count, own_count)
  
            n_cols = 8    
            for row in batched(df_group.itertuples(), n_cols):
                cols = st.columns(n_cols)
                for col, coin in zip(cols, row):
                        with col:
                            display_coin_card(coin, current_user) 
 