import streamlit as st
import plotly.express as px
import pandas as pd
import textwrap
import numpy as np
def mfdata_graph(concatenated_df_mf, total_invested_mf, total_current_amount_mf):

    # --- Compute profit/loss summary ---
    profit_loss = total_current_amount_mf - total_invested_mf
    pl_percent = (profit_loss / total_invested_mf) * 100 if total_invested_mf > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Invested", f"₹{total_invested_mf:,.0f}")
    col2.metric("📈 Current Value", f"₹{total_current_amount_mf:,.0f}")
    col3.metric("P/L", f"₹{profit_loss:,.0f}", f"{pl_percent:.2f}%", delta_color="normal")

    st.markdown("---")

    # --- PIE CHART: Allocation by Category ---
    # if "scheme_category" in concatenated_df_mf.columns:
    #     fig_category_pie = px.pie(
    #         concatenated_df_mf,
    #         names="scheme_category",
    #         values="current_amount",
    #         title="Portfolio Allocation by Scheme Category",
    #         color_discrete_sequence=px.colors.qualitative.Pastel
    #     )
    #     fig_category_pie.update_traces(textinfo="percent+label")
    #     st.plotly_chart(fig_category_pie, use_container_width=True)

    if "scheme_category" in concatenated_df_mf.columns:
        fig_category_pie = px.pie(
            concatenated_df_mf,
            names="scheme_category",
            values="current_amount",
            title="Portfolio Allocation by Scheme Category",
            color_discrete_sequence=px.colors.qualitative.Bold  # 🌈 Bolder colors
        )
        fig_category_pie.update_traces(
            textinfo="percent+label",
            textfont_size=14,
            pull=[0.05] * len(concatenated_df_mf["scheme_category"].unique())  # slight pop-out effect
        )
        fig_category_pie.update_layout(
            title_x=0.5,
            font=dict(size=13),
            showlegend=True
        )
        st.plotly_chart(fig_category_pie, use_container_width=True)

    # --- WRAP LONG FUND NAMES ---
    concatenated_df_mf["asset_wrapped"] = concatenated_df_mf["asset"].apply(
        lambda x: "<br>".join(textwrap.wrap(x, width=30))
    )

    df_bar = pd.melt(
        concatenated_df_mf,
        id_vars=["asset_wrapped"],   # unique identifier per fund
        value_vars=["invested", "current_amount"],
        var_name="Type",
        value_name="Amount"
    )

    # --- Bring in 'invested' as a reference for each asset ---
    df_bar = df_bar.merge(
        concatenated_df_mf[["asset_wrapped", "invested"]].rename(columns={"invested": "invested_ref"}),
        on="asset_wrapped",
        how="left"
    )

    # --- Apply color logic: Red = loss, Green = gain, Blue = invested ---
    df_bar["Color"] = np.where(
        (df_bar["Type"] == "current_amount") & (df_bar["Amount"] < df_bar["invested_ref"]),
        "#ef553b",  # 🔴 Loss
        np.where(
            (df_bar["Type"] == "current_amount") & (df_bar["Amount"] >= df_bar["invested_ref"]),
            "#00cc96",  # 🟢 Gain
            "#007bff"   # 🔵 Invested baseline
        )
    )

    # --- Plot the bar chart ---
    fig_investment_bar = px.bar(
        df_bar,
        y="asset_wrapped",
        x="Amount",
        color="Color",
        orientation="h",
        barmode="group",
        title="Invested vs Current Value (🔴 Loss / 🟢 Gain)",
        color_discrete_map="identity"
    )

    fig_investment_bar.update_layout(
        yaxis_title="Mutual Fund",
        xaxis_title="Amount (₹)",
        legend_title="",
        font=dict(size=12),
        title_x=0.5,
        showlegend=False,
        height=400 + len(df_bar["asset_wrapped"].unique()) * 25,  # dynamic height
        margin=dict(l=250, r=50, t=80, b=50),  # extra space for long names
    )
    st.plotly_chart(fig_investment_bar, use_container_width=True)

    # --- HORIZONTAL BAR: XIRR ---
    if "xirr" in concatenated_df_mf.columns:
        df_perf = concatenated_df_mf.copy()
        df_perf["xirr_percent"] = df_perf["xirr"] * 100
        df_perf = df_perf[df_perf["xirr_percent"].notna()]  # Remove missing values

        fig_xirr = px.bar(
            df_perf,
            y="asset_wrapped",
            x="xirr_percent",
            color="scheme_category",
            orientation="h",
            title="Performance: XIRR (%) by Mutual Fund",
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig_xirr.update_layout(
        xaxis_title="XIRR (%)",
        yaxis_title="Mutual Fund",
        font=dict(size=12),
        title_x=0.5,
        height=400 + len(df_perf["asset_wrapped"].unique()) * 25,  # dynamic height
        margin=dict(l=250, r=50, t=80, b=50)  # space for long names
      )

        st.plotly_chart(fig_xirr, use_container_width=True)
