import streamlit as st
import plotly.express as px
import pandas as pd

def gold_data_graph(concatenated_df_gold,total_invested_gold,total_current_amount_gold):
    fig_gold_value = px.bar(
        concatenated_df_gold,
        y="asset",
        x=["Current price", "average_price"],
        orientation="h",
        barmode="group",
        title="Gold Holdings: Invested vs Current Value",
        color_discrete_sequence=["#FFD700", "#DAA520"]  # gold shades
    )
    st.plotly_chart(fig_gold_value, use_container_width=True)


    # fig_gold_pie = px.pie(
    # concatenated_df_gold,
    # names="type",
    # values="Current price",
    # title="Portfolio Allocation within Gold",
    # color_discrete_sequence=px.colors.sequential.Sunset
    # )
    # st.plotly_chart(fig_gold_pie, use_container_width=True)