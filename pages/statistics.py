import streamlit as st
import pandas as pd
from itertools import islice
import coinsutils as cu
import plotly.graph_objs as go

selected_user = None
selected_type = None
selected_country = None
selected_series = None
if 'user' in st.query_params:
    selected_user = st.query_params['user']
if 'type' in st.query_params:
    selected_type = st.query_params['type']
if 'country' in st.query_params:
    selected_country = st.query_params['country']
if 'series' in st.query_params:
    selected_series = st.query_params['series']

st.set_page_config(
    page_title="EuroCoins Statistics",
    page_icon="🟡",
    layout="wide",
)

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
    history_df['date_only'] = history_df['date'].dt.date
    

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
    
        col1,col2 = st.columns(2)
        with col1:
                title = get_stats_title("Regular", regular_found, regular)
                st.write(title)
                progress_title = f"{regular_found} / {regular} ({regular_percent:.2%})"
                st.progress(regular_percent, text = progress_title)

                title = get_stats_title("Commemorative", cc_found, cc)
                st.write(title)
                progress_title = f"{cc_found} / {cc} ({cc_percent:.2%})"
                st.progress(cc_percent, text=progress_title)

                title = get_stats_title("Total", total_found, total)
                st.write(title)
                progress_title = f"{total_found} / {total} ({total_percent:.2%})"
                st.progress(total_percent, progress_title)
            
        with col2:
            fig = generate_rings_fig(regular_found, regular, cc_found, cc, total_found, total)
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        # col1, col2, col3 = st.columns(3)
        
        # with col1:
        #     with st.container(border=True):
        #         title = get_stats_title("Regular", regular_found, regular)
        #         st.write(title)
        #         progress_title = f"{regular_found} / {regular} ({regular_percent:.2%})"
        #         st.progress(regular_percent, text = progress_title)

        # with col2:
        #     with st.container(border=True):
        #         title = get_stats_title("Commemorative", cc_found, cc)
        #         st.write(title)
        #         progress_title = f"{cc_found} / {cc} ({cc_percent:.2%})"
        #         st.progress(cc_percent, text=progress_title)

        # with col3:
        #     with st.container(border=True):
        #         title = get_stats_title("Total", total_found, total)
        #         st.write(title)
        #         progress_title = f"{total_found} / {total} ({total_percent:.2%})"
        #         st.progress(total_percent, progress_title)

def get_stats_title(name, found, total):
    if (found == total):
        return f"##### :white_check_mark: :green[{name}]"
    else:
        return f"##### :ballot_box_with_check: :red[{name}]"
    
def generate_rings_fig(re_found, re_total, cc_found, cc_total, total_found, total):
    data = [
        # RE
        go.Pie(
            values=[re_found, re_total-re_found],
            labels=['Regular Found','Regular Missing'],
            hole=0.25,
            direction='clockwise',
            sort=False,
            marker={'colors':['#405eb8','#ccd4eb']},
            textinfo='none',
        ),
        # CC
        go.Pie(
            values=[cc_found, cc_total-cc_found],
            labels=['Commemorative Found','Commemorative Missing'],
            hole=0.5,
            direction='clockwise',
            sort=False,
            marker={'colors':['#40b852','#ccebd1']},
            textinfo='none',
        ),
        # Total
        go.Pie(
            values=[total_found, total-total_found],
            labels=['Total Found','Total Missing'],
            hole=0.75,
            direction='clockwise',
            sort=False,
            marker={'colors':['#b85e40','#ebd4cc']},
            textinfo='none',
        )
    ]

    fig = go.Figure(data=data)
    fig.update_layout(showlegend=False)
    return fig

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

    # series filter
    with st.container(border=True):
        series_list = sorted(coins_df['series'].unique())
        
        selected_series_index = series_list.index(selected_series) if selected_series in series_list else 0
        series_filter_selected = selected_series in series_list
        
        series_filter = st.checkbox("By series", value=series_filter_selected)
        series = st.selectbox("Series", series_list, index=selected_series_index)
        
        if series_filter:
            coins_df = coins_df[coins_df['series'] == series]

    # details filter
    with st.container(border=True):
        info_filter = st.text_input("Details")
        if info_filter != "":
            coins_df = coins_df[coins_df['feature'].str.contains(info_filter, case=False, na=False)]


# main content
coins_df = coins_df.sort_values(by=['country', 'value'])
coins_df['own'] = coins_df['names'].apply(lambda x: 1 if current_user in x else 0)
if current_user:
    coins_df['found'] = coins_df['own']
else:
    coins_df['found'] = coins_df['names'].apply(lambda x: 1 if len(x) > 0 else 0)

# total stats
st.subheader("Total statistics")
total_stats_data = cu.generate_stats_data(coins_df, ':flag-eu: Coins')
sssdf = pd.DataFrame([total_stats_data])
for data in sssdf.itertuples():
    country_stats_card(data)    

st.subheader("Countries statistics")

rows = []
# group by country stats
grouped_country = coins_df.groupby('country')
dfs = {country: group.reset_index(drop=True) for country, group in grouped_country}

for country, df_group in dfs.items():
    flag_emoji = cu.flags.get(country, "")
    name = f"{flag_emoji} {country}"
    data = cu.generate_stats_data(df_group, name)
    rows.append(data)

stats_df = pd.DataFrame(rows)
# st.write(stats_df)

for data in stats_df.itertuples():
    country_stats_card(data)