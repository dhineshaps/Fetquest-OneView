def stock_data_display(stock_view_df):
    cols_to_keep = [
        "asset", "Current price", "average_price", "quantity",
        "PE", "EPS", "PB Ratio", "Market Cap", "Company Size", "Sector",
        "52Week High", "52Week Low",
        "Invested Amount", "Current Value", "Profit/Loss", "P/L %"
    ]

    df_Stock_display = stock_view_df[cols_to_keep].copy()
    df_Stock_display.index = df_Stock_display.index + 1

    df_Stock_display.rename(columns={
        "asset": "Stock",
        "quantity": "Quantity",
        "average_price": "Avg Price",
        "Current price": "CMP",
        "PE": "P/E Ratio",
        "Invested Amount": "Total Invested",
        "Current Value": "Total Current Value"
    }, inplace=True)

    def safe_fmt(x, decimals=2):
        try:
            x = float(x)
            if decimals == 0:
                return f"{int(x)}" if x.is_integer() else f"{x:.0f}"
            return f"{x:.{decimals}f}"
        except:
            return x

    safe_formatters = {
        "CMP": lambda x: safe_fmt(x, 2),
        "Avg Price": lambda x: safe_fmt(x, 2),
        "Quantity": lambda x: safe_fmt(x, 2),
        "P/E Ratio": lambda x: safe_fmt(x, 2),
        "EPS": lambda x: safe_fmt(x, 2),
        "PB Ratio": lambda x: safe_fmt(x, 2),
        "Total Invested": lambda x: safe_fmt(x, 2),
        "Total Current Value": lambda x: safe_fmt(x, 2),
        "Profit/Loss": lambda x: safe_fmt(x, 2),
        "52Week High": lambda x: safe_fmt(x, 2),
        "52Week Low": lambda x: safe_fmt(x, 2),
        "P/L %": lambda x: safe_fmt(x, 2)
    }

    def highlight_row(row):
        if row["Total Current Value"] > row["Total Invested"]:
            return ["background-color: rgba(0,255,0,0.05)"] * len(row)
        elif row["Total Current Value"] < row["Total Invested"]:
            return ["background-color: rgba(255,0,0,0.05)"] * len(row)
        else:
            return [""] * len(row)


    def color_profit_loss(val):
        try:
            v = float(val)
            if v > 0:
                return "color: limegreen; font-weight: bold"
            elif v < 0:
                return "color: tomato; font-weight: bold"
        except:
            pass
        return "color: white"

    styled_df = (
        df_Stock_display.style
            .apply(highlight_row, axis=1)
            .map(color_profit_loss, subset=["Profit/Loss"])
            .format(safe_formatters)
    )

    return styled_df
