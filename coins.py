import streamlit as st
import pandas as pd
from itertools import islice

flags = {
    "Andorra": ":flag-ad:",
    "Austria": ":flag-at:",
    "Belgium": ":flag-be:",
    "Croatia": ":flag-hr:",
    "Cyprus": ":flag-cy:",
    "Estonia": ":flag-ee:",
    "Euro area countries": "Euro area countries",
    "Finland": ":flag-fi:",
    "France": ":flag-fr:",
    "Germany": ":flag-de:",
    "Greece": ":flag-gr:",
    "Ireland": ":flag-ie:",
    "Italy": ":flag-it:",
    "Latvia": ":flag-lv:",
    "Lithuania": ":flag-lt:",
    "Luxembourg": ":flag-lu:",
    "Malta": ":flag-mt:",
    "Monaco": ":flag-mc:",
    "Netherlands": ":flag-nl:",
    "Portugal": ":flag-pt:",
    "San Marino": ":flag-sm:",
    "Slovakia": ":flag-sk:",
    "Slovenia": ":flag-si:",
    "Spain": ":flag-es:",
    "Vatican City": ":flag-va:"
}

series_names = {
    "AND-01": "Andorra 1",
    "AUT-01": "Austria 1",
    "BEL-01": "Belgium 1",
    "BEL-02": "Belgium 2",
    "BEL-03": "Belgium 3",
    "CYP-01": "Cyprus 1",
    "DEU-01": "Germany 1",
    "ESP-01": "Spain 1",
    "ESP-02": "Spain 2",
    "ESP-03": "Spain 3",
    "EST-01": "Estonia 1",
    "FIN-01": "Finland 1",
    "FIN-02": "Finland 2",
    "FRA-01": "France 1",
    "FRA-02": "France 2",
    "GRC-01": "Greece 1",
    "HRV-01": "Croatia 1",
    "IRL-01": "Ireland 1",
    "ITA-01": "Italy 1",
    "LTU-01": "Lithuania 1",
    "LUX-01": "Luxembourg 1",
    "LVA-01": "Latvia 1",
    "MCO-01": "Monaco 1",
    "MCO-02": "Monaco 2",
    "MLT-01": "Malta 1",
    "NLD-01": "Netherlands 1",
    "NLD-02": "Netherlands 2",
    "PRT-01": "Portugal 1",
    "SMR-01": "San Marino 1",
    "SMR-02": "San Marino 2",
    "SVK-01": "Slovakia 1",
    "SVN-01": "Slovenia 1",
    "VAT-01": "Vatican City 1",
    "VAT-02": "Vatican City 2",
    "VAT-03": "Vatican City 3",
    "VAT-04": "Vatican City 4",
    "VAT-05": "Vatican City 5",
    "CC-2004": "CC 2004",
    "CC-2005": "CC 2005",
    "CC-2006": "CC 2006",
    "CC-2007": "CC 2007",
    "CC-2007-TOR": "CC 2007 TOR",
    "CC-2008": "CC 2008",
    "CC-2009": "CC 2009",
    "CC-2009-EMU": "CC 2009 EMU",
    "CC-2010": "CC 2010",
    "CC-2011": "CC 2011",
    "CC-2012": "CC 2012",
    "CC-2012-TYE": "CC 2012 TYE",
    "CC-2013": "CC 2013",
    "CC-2014": "CC 2014",
    "CC-2015": "CC 2015",
    "CC-2015-EUF": "CC 2015 EUF",
    "CC-2016": "CC 2016",
    "CC-2017": "CC 2017",
    "CC-2018": "CC 2018",
    "CC-2019": "CC 2019",
    "CC-2020": "CC 2020",
    "CC-2021": "CC 2021",
    "CC-2022": "CC 2022",
    "CC-2022-ERA": "CC 2022 ERA",
    "CC-2023": "CC 2023"
}

series_names_info = {
    "AND-01": "Andorra 1",
    "AUT-01": "Austria 1",
    "BEL-01": "Belgium 1",
    "BEL-02": "Belgium 2",
    "BEL-03": "Belgium 3",
    "CYP-01": "Cyprus 1",
    "DEU-01": "Germany 1",
    "ESP-01": "Spain 1",
    "ESP-02": "Spain 2",
    "ESP-03": "Spain 3",
    "EST-01": "Estonia 1",
    "FIN-01": "Finland 1",
    "FIN-02": "Finland 2",
    "FRA-01": "France 1",
    "FRA-02": "France 2",
    "GRC-01": "Greece 1",
    "HRV-01": "Croatia 1",
    "IRL-01": "Ireland 1",
    "ITA-01": "Italy 1",
    "LTU-01": "Lithuania 1",
    "LUX-01": "Luxembourg 1",
    "LVA-01": "Latvia 1",
    "MCO-01": "Monaco 1",
    "MCO-02": "Monaco 2",
    "MLT-01": "Malta 1",
    "NLD-01": "Netherlands 1",
    "NLD-02": "Netherlands 2",
    "PRT-01": "Portugal 1",
    "SMR-01": "San Marino 1",
    "SMR-02": "San Marino 2",
    "SVK-01": "Slovakia 1",
    "SVN-01": "Slovenia 1",
    "VAT-01": "Vatican City 1",
    "VAT-02": "Vatican City 2",
    "VAT-03": "Vatican City 3",
    "VAT-04": "Vatican City 4",
    "VAT-05": "Vatican City 5",
    "CC-2004": "Commemorative 2004",
    "CC-2005": "Commemorative 2005",
    "CC-2006": "Commemorative 2006",
    "CC-2007": "Commemorative 2007",
    "CC-2007-TOR": "Commemorative 2007 / 50th anniversary of the Treaty of Rome",
    "CC-2008": "Commemorative 2008",
    "CC-2009": "Commemorative 2009",
    "CC-2009-EMU": "Commemorative 2009 / 10th anniversary of Economic and Monetary Union",
    "CC-2010": "Commemorative 2010",
    "CC-2011": "Commemorative 2011",
    "CC-2012": "Commemorative 2012",
    "CC-2012-TYE": "Commemorative 2012 / Ten years of the euro",
    "CC-2013": "Commemorative 2013",
    "CC-2014": "Commemorative 2014",
    "CC-2015": "Commemorative 2015",
    "CC-2015-EUF": "Commemorative 2015 EUF / The 30th anniversary of the EU flag",
    "CC-2016": "Commemorative 2016",
    "CC-2017": "Commemorative 2017",
    "CC-2018": "Commemorative 2018",
    "CC-2019": "Commemorative 2019",
    "CC-2020": "Commemorative 2020",
    "CC-2021": "Commemorative 2021",
    "CC-2022": "Commemorative 2022",
    "CC-2022-ERA": "Commemorative 2022 / 35 years of the Erasmus programme",
    "CC-2023": "Commemorative 2023"
}

def load_catalog():
    print("Loading catalog")
    catalog_df = pd.read_csv('catalog.csv')
    return catalog_df

def load_history():
    print("Loading history")
    history_df = pd.read_csv('history.csv')
    return history_df

def save_history():
    print("Saving history")
    history_df = st.session_state.history_df
    history_df.to_csv('history.csv', index=False)

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
         st.session_state.catalog_df = load_catalog()
    if 'history_df' not in st.session_state:
        st.session_state.history_df = load_history()

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
        flag_emoji = flags.get(country, "")

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
    series_name = series_names_info.get(series, series)
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
        selected_regular = st.checkbox("Regular", value=False)
        selected_commemorative = st.checkbox("Commemorative", value=True)
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
        series_filter = st.checkbox("By series")
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
 