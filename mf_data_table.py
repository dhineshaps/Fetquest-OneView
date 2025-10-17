import pandas as pd
import numpy as np

def mf_data_display(mf_view_df):
    cols_to_keep = [
        "asset", "average_price", "quantity",
        "scheme_category", "xirr", "cagr", "invested", "current_amount","Profit/Loss","P/L %"
    ]

    # Keep only existing columns to avoid KeyError
    cols_to_keep = [c for c in cols_to_keep if c in mf_view_df.columns]
    df_mf_display = mf_view_df[cols_to_keep].copy()

    # Convert numeric columns properly
    for col in ["current_amount", "invested", "Profit/Loss"]:
        if col in df_mf_display.columns:
            df_mf_display[col] = pd.to_numeric(df_mf_display[col], errors="coerce")

    # Rename for display clarity
    df_mf_display.rename(columns={
        "asset": "Fund",
        "quantity": "Quantity",
        "average_price": "Average Price",
        "xirr": "XIRR",
        "cagr": "CAGR",
        "current_amount": "Total Current Value",
        "scheme_category": "Scheme Category",
        "invested": "Total Invested"
    }, inplace=True)

    # Formatting rules
    fmt_dict = {
        "Average Price": "{:.2f}",
        "Quantity": "{:.0f}",
        "XIRR": "{:.2f}",
        "CAGR": "{:.2f}",
        "Total Invested": "{:.2f}",
        "Total Current Value": "{:.2f}",
        "Profit/Loss": "{:.2f}",
        "P/L %": "{:.2f}",
    }

    def highlight_row(row):
        """Subtle row background for gain/loss"""
        invested = row.get("Total Invested", np.nan)
        current = row.get("Total Current Value", np.nan)

        if pd.notna(current) and pd.notna(invested):
            if float(current) > float(invested):
                return ["background-color: rgba(0, 255, 0, 0.05)"] * len(row)  # soft green
            elif float(current) < float(invested):
                return ["background-color: rgba(255, 0, 0, 0.05)"] * len(row)  # soft red
            else:
                return ["background-color: rgba(255, 255, 255, 0.05)"] * len(row)
        else:
            return ["background-color: rgba(255, 255, 255, 0.05)"] * len(row)

    def color_profit_loss(val):
        """Text color for profit/loss column"""
        try:
            val = float(val)
            color = "limegreen" if val > 0 else "tomato" if val < 0 else "white"
        except Exception:
            color = "white"
        return f"color: {color}; font-weight: bold"

    styled_df_mf = (
        df_mf_display.style
        .apply(highlight_row, axis=1)
        .map(color_profit_loss, subset=["Profit/Loss"])
        .format(fmt_dict)
    )

    return styled_df_mf
