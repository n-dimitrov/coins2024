import streamlit as st
import pandas as pd
from itertools import islice
import coinsutils as cu
import random

random_key = random.choice(list(cu.series_names.keys()))

selected_user = None
selected_type = None
selected_country = None
selected_series = None
selected_group_by = None

if 'user' in st.query_params:
    selected_user = st.query_params['user']
if 'type' in st.query_params:
    selected_type = st.query_params['type']
if 'country' in st.query_params:
    selected_country = st.query_params['country']
if 'series' in st.query_params:
    selected_series = st.query_params['series']
if 'group' in st.query_params:
    selected_group_by = st.query_params['group']

def save_history(history_df):
    cu.save_history(history_df)

def add_coin(coin_id, name, date=None):
    if (date is None):
        date = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    print("Add coin to history: ", name, coin_id, date)
    new_row = {'name': name,'id': coin_id, 'date':date}
    new_df = pd.DataFrame([new_row])

    history_df = st.session_state.history_df
    history_df = pd.concat([history_df, new_df], ignore_index=True)
    st.session_state.history_df = history_df
    save_history(history_df)

def remove_coin(coin_id, name):
    print("Remove coin from history: ", name, coin_id)
    df = st.session_state.history_df
    df = df[~((df['name'] == name) & (df['id'] == coin_id))]
    st.session_state.history_df = df
    save_history(df)

def get_last_added():
    history_df = st.session_state.history_df
    last_added_df = history_df.groupby(['date_only', 'name']).agg({
            'id': lambda x: list(x)  
    }).reset_index()
    last_added_df = last_added_df.sort_values(by=['date_only', 'name'], ascending=False)
    last_added = last_added_df.head(3)
    return last_added

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

def coin_progress_bar(coin):
    ownership_percentage = 100 if coin.own == 1 else 0
    bar_html = f"""
    <div style='
        width: 100%; 
        background-color: #e0e0e0; 
        border-radius: 25px;
        overflow: hidden;
        height: 8px;
        margin-top: 10px;
    '>
        <div style='
            width: {ownership_percentage}%; 
            background-color: #1c83e1; 
            height: 100%;
        '></div>
    </div>
    <p style='margin-top: 5px;'></p>
    """
    return bar_html

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
        
        bar_html = coin_progress_bar(coin)
        st.markdown(bar_html, unsafe_allow_html=True)
        
        st.image(image)
        st.write(f"{value} / {year}")

        users_list = st.session_state.users_list
        count_users = len(users_list)

        pop_label = f"{owners_count} / {count_users}"
        pop = st.popover(pop_label)
        with pop:
            # list of owners
            if owners_count > 0:
                for name in owners_names:
                    if name == current_user:
                        name = f":green[{name}]"
                    st.write(name)
            # add / remove button
            if current_user:
                if own == 0:
                    label = f"{current_user} Add :green[:heavy_plus_sign:]"
                    add_button = st.button(label, key=f"add_{coin.id}", on_click=add_coin, args=[coin.id, current_user])
                        
                else:
                    label = f"{current_user} Remove :red[:heavy_minus_sign:]"
                    remove_button = st.button(label, key=f"remove_{coin.id}", on_click=remove_coin, args=[coin.id, current_user])

def get_stats_title(name, found, total):
    if (found == total):
        if (total == 0):
            return f"#### {name}"
        else:
            return f"#### :white_check_mark: :green[{name}]"
    else:
        return f"#### :ballot_box_with_check: :red[{name}]"
    
###
# Country Stats card
###
def country_stats_card(data):
    name = data.name
    total_found = data.total_found
    total = data.total
    total_percent = data.total_percent  
    regular_found = data.regular_found
    regular = data.regular
    regular_percent = data.regular_percent
    cc_found = data.cc_found
    cc = data.cc
    cc_percent = data.cc_percent

    with st.container(border=True):
        st.write(f"### {name}")
    
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container(border=True):
                title = get_stats_title("Regular", regular_found, regular)
                st.write(title)
                progress_title = f"{regular_found} / {regular} ({regular_percent:.2%})"
                st.progress(regular_percent, text = progress_title)

        with col2:
            with st.container(border=True):
                title = get_stats_title("Commemorative", cc_found, cc)
                st.write(title)
                progress_title = f"{cc_found} / {cc} ({cc_percent:.2%})"
                st.progress(cc_percent, text=progress_title)

        with col3:
            with st.container(border=True):
                title = get_stats_title("Total", total_found, total)
                st.write(title)
                progress_title = f"{total_found} / {total} ({total_percent:.2%})"
                st.progress(total_percent, progress_title)

st.header("EuroCoins Catalog")

with st.spinner("Loading..."):
    init_coins()

coins_df = st.session_state.coins_df
users_list = st.session_state.users_list
total_users = len(users_list)

### sidebar filters
with st.sidebar:
    st.header("Filters")

    # user filter
    with st.container(border=True):
        user_filter_selected_index = users_list.index(selected_user) if selected_user in users_list else 0
        user_filter_selected = selected_user in users_list

        user_filter = st.checkbox("By user", value=user_filter_selected)
        current_user = st.selectbox("User", users_list, index=user_filter_selected_index)

        if not user_filter:
            current_user = None
        
        user_filter = st.selectbox("Coins", ["All", "Found", "Missing"])

    # type filter
    with st.container(border=True):
        REGULAR = "RE"
        COMMEMORATIVE = "CC"
        TYPE_MAPPING = {0: REGULAR, 1: COMMEMORATIVE}
        UI_TYPE_MAPPING = {"Regular": REGULAR, "Commemorative": COMMEMORATIVE}

        selected_type_index = 1 if selected_type == COMMEMORATIVE else 0
        type_filter_selected = selected_type in TYPE_MAPPING.values()
        
        type_filter = st.checkbox("By type", value=type_filter_selected)
        selected_ui_type = st.selectbox("Type", list(UI_TYPE_MAPPING.keys()), index=selected_type_index)

        if type_filter:
            coins_df = coins_df[coins_df['type'] == UI_TYPE_MAPPING[selected_ui_type]]


    # country filter
    with st.container(border=True):
        countries_list = sorted(coins_df['country'].unique())

        selected_country_index = countries_list.index(selected_country) if selected_country in countries_list else 0
        country_filter_selected = selected_country in countries_list

        country_filter = st.checkbox("By country", value=country_filter_selected)
        country = st.selectbox("Country", countries_list, index=selected_country_index)
        
        if country_filter:
            coins_df = coins_df[coins_df['country'] == country]   

    # # series filter
    # with st.container(border=True):
    #     series_list = sorted(coins_df['series'].unique())
        
    #     selected_series_index = series_list.index(selected_series) if selected_series in series_list else 0
    #     series_filter_selected = selected_series in series_list
        
    #     series_filter = st.checkbox("By series", value=series_filter_selected)
    #     series = st.selectbox("Series", series_list, index=selected_series_index)
        
    #     if series_filter:
    #         coins_df = coins_df[coins_df['series'] == series]

    # details filter
    with st.container(border=True):
        info_filter = st.text_input("Details")
        if info_filter != "":
            coins_df = coins_df[coins_df['feature'].str.contains(info_filter, case=False, na=False)]

    # group by 
    with st.container(border=True):
        group_by_list = ["Value", "Country", "Series"]

        selected_group_by_index = 1
        if selected_group_by == "value":
            selected_group_by_index = 0
        elif selected_group_by == "country":
            selected_group_by_index = 1
        elif selected_group_by == "series":
            selected_group_by_index = 2

        group_by = st.selectbox("Group by", group_by_list, index=selected_group_by_index)

    
## main content

coins_df = coins_df.sort_values(by=['country', 'value'])
coins_df['own'] = coins_df['names'].apply(lambda x: 1 if current_user in x else 0)
if current_user:
    coins_df['found'] = coins_df['own']
else:
    coins_df['found'] = coins_df['names'].apply(lambda x: 1 if len(x) > 0 else 0)

if user_filter == "Found":
    coins_df = coins_df[coins_df['found'] == 1]
elif user_filter == "Missing":
    coins_df = coins_df[coins_df['found'] == 0]

 
## statistics
with st.expander(":bar_chart: Statistics"):
    st.subheader("Statistics")

    # total stats
    total_stats_data = cu.generate_stats_data(coins_df, ':flag-eu: Coins')
    sssdf = pd.DataFrame([total_stats_data])
    for data in sssdf.itertuples():
        country_stats_card(data)

    st.page_link('pages/statistics.py', label=':bar_chart: More Statistics')


## last added
with st.expander(":calendar: Last added"):
    st.subheader("History")
    catalog_df = st.session_state.catalog_df
    last_added_df = get_last_added()

    for row in last_added_df.itertuples():
        d = row.date_only
        owner = row.name
        ids = row.id
        date = d.strftime('%d %B %Y')
        data = {
            'country': [],
            'series': [],
            'year': [],
            'image': [],
            'value': [],
            'type': []
        }
        st.write(f"#### {owner} @ {date}")

        for i in ids:
            coin = catalog_df[catalog_df['id'] == i]
            data['country'].append(coin['country'].values[0])
            data['series'].append(coin['series'].values[0])
            data['year'].append(coin['year'].values[0])
            data['value'].append(coin['value'].values[0])
            data['type'].append(coin['type'].values[0])
            data['image'].append(coin['image'].values[0])

        dff = pd.DataFrame(data)
        frame = st.data_editor(
            dff,
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

    st.page_link('pages/history.py', label=':calendar: Full History')

# add new column with series name
coins_df['series_name'] = coins_df['series'].apply(lambda x: cu.series_names_info.get(x, x))

# gouped by 
if group_by == "Value":
    gby = 'value'
elif group_by == "Country":
    gby = 'country'
elif group_by == "Series":
    gby = 'series_name'
else:
    gby = 'country'


grouped_series = coins_df.groupby(gby)
dfs = {series: group.reset_index(drop=True) for series, group in grouped_series}

for series, df_group in dfs.items():
    series_coins_count = len(df_group)
    df_group = df_group.sort_values(by=['country', 'value'])
    found_count = df_group['found'].sum()
    # series_name = cu.series_names_info.get(series, series)
    series_name = series
    series_procentage = found_count / series_coins_count

    series_title = get_stats_title(series_name, found_count, series_coins_count)

    with st.expander(f"{series_title}"):    
        with st.container(border=True):
            c1, c2 = st.columns([1,8])
            c2.progress(series_procentage)
            c1.write(f"{found_count} / {series_coins_count}")

        n_cols = 8    
        for row in batched(df_group.itertuples(), n_cols):
            cols = st.columns(n_cols)
            for col, coin in zip(cols, row):
                    with col:
                        display_coin_card(coin, current_user) 
