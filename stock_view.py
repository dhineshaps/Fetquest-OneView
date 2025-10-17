import streamlit as st
import plotly.express as px
import pandas as pd

def stock_data_graph(concatenated_df_stock, total_invested_stock, total_current_amount_stock):

    # --- Summary Metrics ---
    profit_loss = total_current_amount_stock - total_invested_stock
    pl_percent = (profit_loss / total_invested_stock) * 100 if total_invested_stock > 0 else 0

    col1, col2, col3,col4 = st.columns(4)
    col1.metric("💰 Total Invested in Stocks", f"₹{total_invested_stock:,.0f}")
    col2.metric("📈 Total Current Value", f"₹{total_current_amount_stock:,.0f}")
    col3.metric(
        "P/L",
        f"₹{profit_loss:,.0f}",
        f"{pl_percent:.2f}%",
        delta_color="normal"
    )
    col4.metric("P/L %", f"₹{pl_percent:,.0f}")

    st.markdown("---")

    col1,col2 = st.columns(2)
 
    # --- Sector Allocation Pie Chart ---
    with col1:
        if "Sector" in concatenated_df_stock.columns:
            fig_sector = px.pie(
                concatenated_df_stock,
                names="Sector",
                values="Invested Amount",
                title="Portfolio Allocation by Sector - Total Invested",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            fig_sector.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_sector, use_container_width=True)
    
    with col2:
        if "Sector" in concatenated_df_stock.columns:
            fig_sector = px.pie(
                concatenated_df_stock,
                names="Sector",
                values="Current Value",
                title="Portfolio Allocation by Sector -Total Current Value",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            fig_sector.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_sector, use_container_width=True)
    st.markdown("---")
    col1,col2 = st.columns(2)
    # --- Company Size Allocation Pie Chart ---
    with col1:
        if "Company Size" in concatenated_df_stock.columns:
            fig_cap = px.pie(
                concatenated_df_stock,
                names="Company Size",
                values="Invested Amount",
                title="Invested by Company Size",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_cap.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_cap, use_container_width=True)
    with col2:
        if "Company Size" in concatenated_df_stock.columns:
            fig_cap = px.pie(
                concatenated_df_stock,
                names="Company Size",
                values="Current Value",
                title="Current Value by Company Size",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_cap.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_cap, use_container_width=True)
    st.markdown("---")
    # --- Average vs Current Price by Stock ---
    price_compare_df = pd.melt(
        concatenated_df_stock,
        id_vars=["symbol"],
        value_vars=["average_price", "Current price"],
        var_name="Price Type",
        value_name="Price"
    )

    price_compare_df["Price Type"] = price_compare_df["Price Type"].replace({
        "average_price": "Average Price",
        "Current price": "Current Market Price"
    })

    fig_stock_prices = px.bar(
        price_compare_df,
        x="symbol",
        y="Price",
        color="Price Type",
        barmode="group",
        title="Average vs Current Market Price by Stock",
        color_discrete_map={
            "Average Price": "#1f77b4",  # Blue
            "Current Market Price": "#D6C41E"   # Green
        }
    )
    fig_stock_prices.update_layout(
        xaxis_title="Stock Symbol",
        yaxis_title="Price (₹)",
        legend_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_x=0.5
    )
    st.plotly_chart(fig_stock_prices, use_container_width=True)
    st.markdown("---")
    # --- Profit / Loss by Stock ---
    concatenated_df_stock["profit_loss"] = (
        concatenated_df_stock["Current Value"] - concatenated_df_stock["Invested Amount"]
    )
    concatenated_df_stock["Result"] = concatenated_df_stock["profit_loss"].apply(
        lambda x: "Gain" if x >= 0 else "Loss"
    )

    fig_pl = px.bar(
        concatenated_df_stock,
        x="symbol",
        y="profit_loss",
        color="Result",
        title="Profit / Loss by Stock",
        color_discrete_map={"Gain": "#00CC96", "Loss": "#EF553B"}
    )
    fig_pl.update_layout(
        xaxis_title="Stock",
        yaxis_title="Profit / Loss (₹)",
        title_x=0.5,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_pl, use_container_width=True)
    st.markdown("---")
    # --- Sector-wise Return (%) ---
    if "Sector" in concatenated_df_stock.columns:
        sector_return = (
            concatenated_df_stock.groupby("Sector")[["Invested Amount", "Current Value"]]
            .sum()
            .reset_index()
        )
        sector_return["Return %"] = (
            (sector_return["Current Value"] - sector_return["Invested Amount"])
            / sector_return["Invested Amount"]
        ) * 100

        fig_sector_return = px.bar(
            sector_return,
            x="Sector",
            y="Return %",
            color="Sector",
            title="Sector-wise Return (%)",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_sector_return.update_layout(
            xaxis_title="Sector",
            yaxis_title="Return (%)",
            title_x=0.5,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_sector_return, use_container_width=True)