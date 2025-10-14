
#to style the df table in stock view

def stock_data_display(stock_view_df):
    cols_to_keep = [
    "asset", "Current price","average_price","quantity", 
    "PE", "EPS", "PB Ratio", "Market Cap","Company Size","Sector","52Week High","52Week Low","Invested Amount","Current Value","Profit/Loss"
     ]
    
    df_Stock_display = stock_view_df[cols_to_keep].copy()

    df_Stock_display.index = df_Stock_display.index + 1

    df_Stock_display.rename(columns={
    "asset": "Stock",
    "quantity": "Quantity",
    "average_price": "Average Price",
    "Current price": "Current Price",
    "PE": "P/E Ratio",
    "Invested Amount":"Invested",
    }, inplace=True)

    fmt_dict = {
    "Current Price": "{:.2f}",
    "Average Price": "{:.2f}",
    "Quantity": "{:.0f}",
    "P/E Ratio": "{:.2f}",
    "EPS": "{:.2f}",
    "PB Ratio": "{:.2f}",
    "Invested": "{:.2f}",
    "Current Value": "{:.2f}",
    "Profit/Loss": "{:.2f}",
    "52Week High": "{:.2f}",
    "52Week Low": "{:.2f}",
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
        df_Stock_display.style
        .apply(highlight_row, axis=1)
        .map(color_profit_loss, subset=["Profit/Loss"])
        .format(fmt_dict) 
    )

    return styled_df


    # gb = GridOptionsBuilder.from_dataframe(df_Stock_display)
    # gb.configure_default_column(editable=False, groupable=False, resizable=True, sortable=True)

    # cell_style_jscode = JsCode("""
    # function(params) {
    #     if (params.colDef.field == 'Current Value') {
    #         let invested = params.data['Invested'];
    #         let current = params.value;
    #         if (current < invested) {
    #             return {'color': 'red', 'font-weight': 'bold'};
    #         } else if (current > invested) {
    #             return {'color': 'green', 'font-weight': 'bold'};
    #         }
    #     }
    #     return {};
    # }
    # """)

    # gb.configure_columns(
    # ["Current Value"],
    # cellStyle=cell_style_jscode
    # )

    # grid_options = gb.build()

    # gb.configure_grid_options(
    # rowHeight=35,                # taller rows
    # headerHeight=40,             # taller headers
    # domLayout='normal',          # no scrollbars unless needed
    # suppressHorizontalScroll=True
    # )

    # custom_css = {
    # ".ag-header-cell-label": {
    #     "justify-content": "center",
    #     "font-weight": "600",
    #     "font-size": "14px",
    #     "color": "#ffffff" if st.get_option("theme.base") == "dark" else "#000000",
    # },
    # ".ag-cell": {
    #     "font-size": "14px",
    #     "padding": "6px 8px",
    # },
    # ".ag-row": {
    #     "border-bottom": "1px solid rgba(128,128,128,0.2)",
    # },
    # ".ag-header": {
    #     "background-color": "#1E1E1E" if st.get_option("theme.base") == "dark" else "#f8f9fa",
    # },
    # }

    # AgGrid(
    # df_Stock_display,
    # gridOptions=grid_options,
    # theme="streamlit",  # nice light/dark mode adaptive theme
    # fit_columns_on_grid_load=True,
    # enable_enterprise_modules=False,
    # allow_unsafe_jscode=True,
    # ustom_css=custom_css
    # )