import streamlit as st
import plotly.express as px
import pandas as pd

def mfdata_graph(concatenated_df_mf, total_invested_mf, total_current_amount_mf):

    profit_loss = total_current_amount_mf - total_invested_mf
    pl_percent = (profit_loss / total_invested_mf) * 100 if total_invested_mf > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Invested in MF", f"₹{total_invested_mf:,.0f}")
    col2.metric("📈 Current Value", f"₹{total_current_amount_mf:,.0f}")
    col3.metric(
        "P/L",
        f"₹{profit_loss:,.0f}",
        f"{pl_percent:.2f}%",
        delta_color="normal"
    )

    st.markdown("---")

    # --- Pie Chart: Allocation by Scheme Category ---
    if "scheme_category" in concatenated_df_mf.columns:
        fig_category_pie = px.pie(
            concatenated_df_mf,
            names="scheme_category",
            values="current_amount",
            title="Portfolio Allocation by Scheme Category",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_category_pie, use_container_width=True)

    # --- Bar Chart: Invested vs Current Value ---
    fig_investment_bar = px.bar(
        concatenated_df_mf,
        x="symbol",
        y=["invested", "current_amount"],
        barmode="group",
        title="Invested vs Current Value by Fund",
        color_discrete_sequence=["#007bff", "#00cc96"]
    )
    st.plotly_chart(fig_investment_bar, use_container_width=True)

    # --- Scatter Plot: XIRR vs CAGR ---
    if "xirr" in concatenated_df_mf.columns and "cagr" in concatenated_df_mf.columns:
        fig_xirr_cagr = px.scatter(
            concatenated_df_mf,
            x="xirr",
            y="cagr",
            color="scheme_category",
            hover_name="symbol",
            title="XIRR vs CAGR by Fund",
            size="current_amount",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig_xirr_cagr, use_container_width=True)
