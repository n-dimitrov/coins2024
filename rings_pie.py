import plotly.graph_objs as go
import streamlit as st

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

fig = generate_rings_fig(180, 284, 109, 511, 289, 795)

st.header("Chart")
st.plotly_chart(fig, theme="streamlit", use_container_width=True)