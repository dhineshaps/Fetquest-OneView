import streamlit as st
import plotly.express as px
import pandas as pd

def stock_data_graph(concatenated_df_stock,total_invested_stock,total_current_amount_stock):

    profit_loss = total_current_amount_stock - total_invested_stock
    pl_percent = (profit_loss / total_invested_stock) * 100 if total_invested_stock > 0 else 0

    col1,col2,col3 = st.columns(3)

    col1.metric("💰 Total Invested in Stock", f"₹{total_invested_stock:,.0f}")
    col2.metric("📈 Current Value", f"₹{total_current_amount_stock:,.0f}")
    col3.metric(
    "P/L", 
    f"₹{profit_loss:,.0f}", 
    f"{pl_percent:.2f}%",
    delta_color="normal"
    )

    col1,col2 = st.columns(2)
    with col2:
        fig_sector = px.pie(
        concatenated_df_stock,
        names="Sector",
        values="Current Value",
        title="Portfolio Allocation by Sector",
        color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_sector, use_container_width=True)



    with col1:
        price_compare_df = pd.melt(
            concatenated_df_stock,
            id_vars=["symbol"],
            value_vars=["average_price", "Current price"],
            var_name="Price Type",
            value_name="Price"
        )

        # Rename columns for nicer display
        price_compare_df["Price Type"] = price_compare_df["Price Type"].replace({
            "average_price": "Average Price",
            "Current price": "Current Price"
        })

        # Plot consolidated bar chart
        fig_stock_prices = px.bar(
            price_compare_df,
            x="symbol",
            y="Price",
            color="Price Type",
            barmode="group",
            title="Average vs Current Price by Stock",
            color_discrete_map={
                "Average Price": "#636EFA",  # Blue
                "Current Price": "#00CC96"   # Green
            }
        )

        fig_stock_prices.update_layout(
            xaxis_title="Stock Symbol",
            yaxis_title="Price (₹)",
            legend_title="Type",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig_stock_prices, use_container_width=True)

    col3,col4 = st.columns(2)
    with col3:
        sector_summary = (
        concatenated_df_stock.groupby("Sector")[["Invested Amount", "Current Value"]].sum().reset_index()
    )
    fig_sector_bar = px.bar(
        sector_summary,
        x="Sector",
        y=["Invested Amount", "Current Value"],
        barmode="group",
        title="Invested vs Current Value by Sector"
    )
    st.plotly_chart(fig_sector_bar, use_container_width=True)

    # with col4:
    #     fig_bubble = px.scatter(
    #     concatenated_df_stock,
    #     x="EPS",
    #     y="Profit/Loss",
    #     size="Market Cap",
    #     color="Sector",
    #     hover_name="symbol",
    #     title="EPS vs Profit Loss Bubble Size = Market Cap"
    # )
    # st.plotly_chart(fig_bubble, use_container_width=True)
