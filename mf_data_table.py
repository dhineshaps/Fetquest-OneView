
#to style the df table in mf view

def mf_data_display(mf_view_df):
    cols_to_keep = [
    "asset", "current_amount","average_price","quantity", 
    "scheme_category","xirr","cagr","invested","current_amount","Profit/Loss",
     ]
    
    df_mf_display  = mf_view_df[cols_to_keep].copy()

    df_mf_display.index = df_mf_display.index + 1

    df_mf_display.rename(columns={
    "asset": "Fund",
    "quantity": "Quantity",
    "average_price": "Average Price",
    "xirr" : "XIRR",
    "cagr" : "CAGR",
    "current_amount" : "Current Value",
    "scheme_category" :"Scheme Category",
    "invested":"Invested"
    }, inplace=True)

    fmt_dict = {
    "Average Price": "{:.2f}",
    "Quantity": "{:.0f}",
    "XIRR": "{:.2f}",
    "CAGR": "{:.2f}",
    "Invested": "{:.2f}",
    "Current Value": "{:.2f}",
    "Profit/Loss": "{:.2f}",
        }

    def highlight_row(row):
        """Subtle row background for gain/loss"""
        if row["Current Value"] > row["Invested"]:
            return ["background-color: rgba(0, 255, 0, 0.05)"] * len(row)  # soft green tint
        elif row["Current Value"] < row["Invested"]:
            return ["background-color: rgba(255, 0, 0, 0.05)"] * len(row)  # soft red tint
        else:
            return [""] * len(row)
        

    def color_profit_loss(val):
        """Text color for profit/loss column"""
        color = "limegreen" if val > 0 else "tomato" if val < 0 else "white"
        return f"color: {color}; font-weight: bold"

    styled_df = (
        df_mf_display.style
        .apply(highlight_row, axis=1)
        .map(color_profit_loss, subset=["Profit/Loss"])
        .format(fmt_dict) 
    )

    return styled_df
