import streamlit as st
import plotly.express as px
import pandas as pd
from gemini_llm import get_ai_portfolio_recommendation

def consolidated_data(total_invested_stock,total_invested_mf,total_invested_gold,total_current_amount_stock,total_current_amount_mf,total_current_amount_gold):
        if total_invested_gold != 0:
            total_invested = total_invested_stock + total_invested_gold + total_invested_mf
            #st.write(total_invested)
            total_current_invested_value = total_current_amount_stock  + total_current_amount_mf + total_current_amount_gold
            #st.write(total_current_invested_value)
            profit_loss = total_current_invested_value - total_invested
            #st.write(profit_loss) 
            #st.write(portfolio_curd)

            pl_percent = (profit_loss / total_invested) * 100 if total_invested > 0 else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total Invested", f"₹{total_invested:,.0f}")
            col2.metric("📈 Current Value", f"₹{total_current_invested_value:,.0f}")
            col3.metric(
                "P/L", 
                f"₹{profit_loss:,.0f}", 
                f"{pl_percent:.2f}%",
                delta_color="normal"
            )
        else:
            st.subheader("📊 Total Portfolio (Excluding Gold Current Value in P/L)")
            total_invested = total_invested_stock + total_invested_mf
            total_current_invested_value = total_current_amount_stock  + total_current_amount_mf
            profit_loss = total_current_invested_value - total_invested
            gold_value_display = total_current_amount_gold if total_current_amount_gold else 0
            pl_percent = (profit_loss / total_invested) * 100 if total_invested > 0 else 0
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Total Invested", f"₹{total_invested:,.0f}")
            col2.metric("📈 Current Value", f"₹{total_current_invested_value:,.0f}")
            col3.metric(
                "P/L", 
                f"₹{profit_loss:,.0f}", 
                f"{pl_percent:.2f}%",
                delta_color="normal"
            )
            col4.metric("Gold (Current)", f"₹{gold_value_display:,.0f}")
            st.markdown("---")
            st.subheader("📊 Total Portfolio (Including Gold Current Value)")
            total_invested_sep = total_invested_stock + total_invested_gold + total_invested_mf
            total_current_invested_value_sep = total_current_amount_stock  + total_current_amount_mf + total_current_amount_gold
            profit_loss_Sep = total_current_invested_value_sep - total_invested_sep
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Total Invested", f"₹{total_invested_sep:,.0f}")
            col2.metric("📈 Current Value", f"₹{total_current_invested_value_sep:,.0f}")
            col3.metric("📈 P/L", f"₹{profit_loss_Sep:,.0f}")

        
        if (total_invested_gold is None or total_invested_gold == 0) and total_current_amount_gold != 0:
            st.info("⚠️ Gold profit/loss is not included due to missing invested amount.")

        alloc_data = [
        {"Asset": "Stocks", "Invested": total_invested_stock, "Current": total_current_amount_stock},
        {"Asset": "Mutual Funds", "Invested": total_invested_mf, "Current": total_current_amount_mf},
        {"Asset": "Gold", "Invested": total_invested_gold, "Current": total_current_amount_gold}
        ]


        alloc_df = pd.DataFrame(alloc_data)
        #st.write(alloc_df)
        alloc_df = alloc_df[(alloc_df["Invested"] > 0) | (alloc_df["Current"] > 0)]
        ######################for bar chart assets vs current  vs invested ###########################
        bar_df = alloc_df.melt(
        id_vars="Asset",
        value_vars=["Invested", "Current"],
        var_name="Type",
        value_name="Value"
            )
        
        asset_colors = {
        "Stocks": "#7B1FA2",         # purple
        "Mutual Funds": "#1565C0",   # blue
        "Gold": "#D4AF37"           # gold
        }
        
        color_map = {
        ("Stocks", "Invested"): "#7B1FA2",
        ("Stocks", "Current"): "#BA68C8",
        ("Mutual Funds", "Invested"): "#1565C0",
        ("Mutual Funds", "Current"): "#64B5F6",
        ("Gold", "Invested"): "#B8860B",
        ("Gold", "Current"): "#FFD700",
            }
        bar_df["ColorKey"] = bar_df.apply(lambda row: color_map.get((row["Asset"], row["Type"]), "#333333"), axis=1)
        #################################################################################################
        col1, col2 = st.columns(2)
        if not alloc_df.empty:
            pie_df = alloc_df[["Asset", "Current"]].rename(columns={"Current": "Current Value"})
            fig_pie = px.pie(
                pie_df,
                names="Asset",
                values="Current Value",
                hole=0.4,
                title="Asset Allocation by Current Value",
                color="Asset",
                color_discrete_map={
                "Stock": "#990EC4",     
                "Mutual Fund": "#2f1dd3", 
                "Gold": "#DDBF13",        
            }
            )
            with col1:
                st.plotly_chart(fig_pie, use_container_width=True)

        #     fig_bar = px.bar(
        #     alloc_df,
        #     x="Asset",
        #     y=["Invested", "Current"],
        #     barmode="group",
        #     title="Invested vs Current Value by Asset"
        # )

            fig_bar = px.bar(
            alloc_df,
            x="Asset",
            y=["Invested", "Current"],
            barmode="group",
            title="Invested vs Current Value by Asset",
            color_discrete_map={
                "Invested": "#636EFA",   # Example blue
                "Current": "#EF553B",    # Example red
            }
        )
        #     fig_bar = px.bar(
        #     bar_df,
        #     x="Asset",
        #     y="Value",
        #     color="Asset",               # 👈 color by Asset
        #     barmode="group",
        #     pattern_shape="Type",        # differentiates Invested vs Current by pattern
        #     title="Invested vs Current Value by Asset",
        #     color_discrete_map=asset_colors
        # )
            fig_bar.update_traces(
            selector=dict(legendgroup="Invested"),
            marker_line_width=0
            )

            fig_bar.update_traces(
            selector=dict(legendgroup="Current"),
            marker_line_color="white",
            marker_line_width=2
        )

            # 3️⃣ Clean legend
            fig_bar.update_layout(
                legend_title_text="",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
        #     fig_bar.update_layout(
        #     xaxis_title="Asset",
        #     yaxis_title="Value (₹)",
        #     bargap=0.25,
        #     plot_bgcolor="rgba(0,0,0,0)",
        #     paper_bgcolor="rgba(0,0,0,0)",
        # )
            with col2:
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("### 💹 Profit / Loss Contribution by Asset")
            alloc_df["Profit/Loss"] = alloc_df["Current"] - alloc_df["Invested"]
            fig_pl = px.bar(
                alloc_df,
                x="Profit/Loss",
                y="Asset",
                orientation="h",
                title="P/L Contribution by Asset",
                color="Profit/Loss",
                color_continuous_scale=["red", "green"]
            )
            st.plotly_chart(fig_pl, use_container_width=True)
        else:
            st.info("No assets available to display portfolio allocation.")

        
        with st.expander("AI Portfolio Recommendation"):
            st.info("This analysis assumes a 10-year investment horizon and is fully AI-curated. Treat the results as a preview for informational purposes only, No Individual Assests are Analyzed , only the portfolio based on allocation")
            with st.form("portfolio_form"):
                risk_profile = st.selectbox(
                    "What is your Risk Profile?",
                    ("Conservative", "Moderate", "Aggressive"),
                    index=1
                )
                goal = st.selectbox(
                    "What is your Goal?",
                    (
                        "Wealth Growth",
                        "Retirement Corpus",
                        "Buying a Home",
                        "Child’s Education",
                        "Capital Preservation",
                        "Emergency Fund",
                        "Financial Independence"
                    ),
                )
                submitted = st.form_submit_button("Get AI Report")

                if submitted:
                    with st.spinner("Analyzing your portfolio..."):
                        response = get_ai_portfolio_recommendation(
                            total_invested,
                            total_current_invested_value,
                            total_invested_stock,
                            total_invested_mf,
                            total_invested_gold,
                            total_current_amount_stock,
                            total_current_amount_mf,
                            total_current_amount_gold,
                            risk_profile,
                            goal
                        )

                    st.markdown("### 🧭 AI Recommendation")
                    st.write(response)