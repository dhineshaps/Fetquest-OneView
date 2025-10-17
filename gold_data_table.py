import pandas as pd
import numpy as np

def gold_data_display(gold_view_df):

    cols_to_keep = [
        "asset", "average_price", "quantity",
        "Current price"
    ]

    df_Gold_display = gold_view_df[cols_to_keep].copy()

    df_Gold_display["Invested Amount"] = df_Gold_display["quantity"] *df_Gold_display["average_price"]
    df_Gold_display["Current Value"] = df_Gold_display["quantity"] *df_Gold_display["Current price"]
    df_Gold_display["Profit/Loss"] =  df_Gold_display["Current Value"] - df_Gold_display["Invested Amount"]

    df_Gold_display.rename(columns={
    "asset": "Gold Category",
    "quantity": "Quantity",
    "average_price": "Average Price",
    "Current price": "Current Price",
    "Invested Amount":"Invested",
    }, inplace=True)

    for col in ["Current Price", "Invested", "Profit/Loss"]:
        if col in df_Gold_display.columns:
            df_Gold_display[col] = pd.to_numeric(df_Gold_display[col], errors="coerce")

    fmt_dict = {
        "Average Price": "{:.2f}",
        "Quantity": "{:.0f}",
        "Invested": "{:.2f}",
        "Current Price": "{:.2f}",
        "Current Value": "{:.2f}",
        "Profit/Loss": "{:.2f}",
    }

    def highlight_row(row):
        """Subtle row background for gain/loss"""
        invested = row.get("Invested", np.nan)
        current = row.get("Current Value", np.nan)

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
    
    styled_df_gold = (
        df_Gold_display.style
        .apply(highlight_row, axis=1)
        .map(color_profit_loss, subset=["Profit/Loss"])
        .format(fmt_dict)
    )

    return styled_df_gold


