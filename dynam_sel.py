import streamlit as st
import pandas as pd
import uuid
import yfinance as yf


#handling rupes symbol

if "rows" not in st.session_state:
    st.session_state["rows"] = []

rows_collection = []


def add_row():
    element_id = uuid.uuid4()
    st.session_state["rows"].append(str(element_id))
    #st.write(element_id)

def remove_row(row_id):
    st.session_state["rows"].remove(str(row_id))
    
def generate_row(row_id):
    row_container = st.empty()
    row_columns = row_container.columns((3, 2, 1))
    row_name = row_columns[0].selectbox("Stock_Name", options=("ITC.NS","TCS.NS","RELIANCE.NS"), key=f"txt_{row_id}")
    row_columns[1].button("🗑️", key=f"del_{row_id}", on_click=remove_row, args=[row_id])
    return {"name": row_name}

st.title("Stocklytics")

for row in st.session_state["rows"]:
    row_data = generate_row(row)
    rows_collection.append(row_data)

menu = st.columns(2)

with menu[0]:
    st.button("Add Stock", on_click=add_row)

proceed = st.button("Submit", type="primary")




if proceed:
    stocks = []

    for i in rows_collection:
        stocks_val = i['name']
        stocks.append(stocks_val)

    data = []
    for stock in stocks:
        try:
            print(stock)
            stock_ticker = yf.Ticker(stock)
            mcap = stock_ticker.info.get("marketCap","N/A")
            mcap_str = f"₹{mcap / 1e7:,.2f} Crores"
            cmp = stock_ticker.info.get("currentPrice","N/A")
            pe = stock_ticker.info.get("trailingPE")
            sector=stock_ticker.info.get("sectorKey","N/A")
            pb=stock_ticker.info.get("priceToBook","N/A")
            industry=stock_ticker.info.get("industry","N/A")
            hist_data = yf.download(stock, period="1y")
            w52_high = hist_data['High'].max().iloc[0]
            w52_low = hist_data['Low'].min().iloc[0]
            print(w52_low)
            print(hist_data[('Close', stock)].iloc[-2])
            dchng = hist_data[('Close', stock)].iloc[-2]
            try:
                 onemonth = hist_data[('Close', stock)].iloc[-30]
            except:
                print("error in getting the data")
                onemonth = "NA"
            sbuy =  stock_ticker.recommendations['strongBuy'].iloc[0]
            hold= stock_ticker.recommendations['hold'].iloc[0]
            ssell = stock_ticker.recommendations['strongSell'].iloc[0]
            print(sbuy)

            data.append([stock,mcap_str,cmp,pe,dchng,onemonth,w52_high,w52_low,sector,pb,sbuy,hold,ssell])

        except:
            st.write("some issues")

    df_all_data =pd.DataFrame(data,columns=['stock','mcap_str','cmp','pe','dchng','onemonth','w52_high','w52_low','sector','pb','sbuy','hold','ssell'])

    #print(df_all_data)
    st.dataframe(df_all_data.round(2))