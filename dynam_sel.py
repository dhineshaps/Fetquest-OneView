import streamlit as st
import pandas as pd
import uuid
import yfinance as yf
from supabase import create_client, Client
from postgrest.exceptions import APIError
import time

url="https://anpufhhyswexjgwwddcy.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFucHVmaGh5c3dleGpnd3dkZGN5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NzM2ODEsImV4cCI6MjA1OTQ0OTY4MX0.aP4NCS53RezlAsBvAxmzqKUFYtL8azVRbsKnnGCTWmk"

supabase: Client = create_client(url, key)
#handling rupes symbol
#using AI

if "rows" not in st.session_state:
    st.session_state["rows"] = []

rows_collection = []


def add_row():
    element_id = uuid.uuid4()
    st.session_state["rows"].append(str(element_id))
    #st.write(element_id)

def remove_row(row_id):
    st.session_state["rows"].remove(str(row_id))
    
# def generate_row(row_id):
#     row_container = st.empty()
#     # row_columns = row_container.columns((5,4,3, 2, 1))
#     # row_name = row_columns[0].selectbox("Type", options=("ITC.NS","TCS.NS","RELIANCE.NS"), key=f"txt_{row_id}")
#     # row_name = row_columns[0].selectbox("Stock_Name", options=("ITC.NS","TCS.NS","RELIANCE.NS"))
#     # row_name = row_columns[0].selectbox("qty", options=("ITC.NS","TCS.NS","RELIANCE.NS"))
#     # row_name = row_columns[0].selectbox("avg price", options=("ITC.NS","TCS.NS","RELIANCE.NS"))
#     # row_columns[1].button("🗑️", key=f"del_{row_id}", on_click=remove_row, args=[row_id])


def generate_row(row_id):
    col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])

    with col1:
        st.selectbox("Type", options=("Cash", "F&O", "MF"), key=f"type_{row_id}")
    with col2:
        st.selectbox("Stock", options=("ITC.NS","TCS.NS","RELIANCE.NS"), key=f"stock_{row_id}")
    with col3:
        st.number_input("Qty", min_value=1, key=f"qty_{row_id}")
    with col4:
        st.number_input("Avg Price", min_value=0.0, key=f"price_{row_id}")
    with col5:
        st.button("🗑️", key=f"del_{row_id}", on_click=remove_row, args=[row_id])
    
        

    return {"name": st.session_state.get(f"type_{row_id}")}

st.title("Stocklytics")
rows_data = [] 
for row in st.session_state["rows"]:
    row_data = generate_row(row)
    rows_collection.append(row_data)
    st.write(row_data)
    #st.write("here")
    #st.write(rows_collection)
    # row_data = {
    #         "type": st.session_state.get(f"type_{row}"),
    #         "stock": st.session_state.get(f"stock_{row}"),
    #         "qty": st.session_state.get(f"qty_{row}"),
    #         "price": st.session_state.get(f"price_{row}"),
    #     }
    # rows_data.append(row_data)
    
menu = st.columns(2)

with menu[0]:
    st.button("Add Stock", on_click=add_row)

proceed = st.button("Submit", type="primary")

if proceed:
    print(type(rows_data))
    st.write(rows_data)
    ins_list= []
    for item in rows_data:
        item["id"] = 56
        if 'stock' in item:
             item['asset'] = item.pop('stock')
        if 'qty' in item:
             item['quantity'] = item.pop('qty')
        if 'price' in item:
             item['average_price'] = item.pop('price')
        #print(item)
        ins_list.append(item)
        #print(item["type"], item["stock"], item["qty"], item["price"])

   
    print(tuple(ins_list))
    ins_data = tuple(ins_list)
    try:
        insert = (
            supabase.table("fet_portfolio")
                .insert(ins_data)
                .execute()
            )
    except APIError as e:
        #st.error(f"{e.message.split(" ")[-1].split("_")[-2].upper()} already exits, try to login with it.")
        print(e)
        st.error(e)
        st.stop()



# if proceed:
#     stocks = []

#     for i in rows_collection:
#         stocks_val = i['name']
#         stocks.append(stocks_val)

#     data = []
#     for stock in stocks:
#         try:
#             print(stock)
#             stock_ticker = yf.Ticker(stock)
#             mcap = stock_ticker.info.get("marketCap","N/A")
#             mcap_str = f"₹{mcap / 1e7:,.2f} Crores"
#             cmp = stock_ticker.info.get("currentPrice","N/A")
#             pe = stock_ticker.info.get("trailingPE")
#             sector=stock_ticker.info.get("sectorKey","N/A")
#             pb=stock_ticker.info.get("priceToBook","N/A")
#             industry=stock_ticker.info.get("industry","N/A")
#             hist_data = yf.download(stock, period="1y")
#             w52_high = hist_data['High'].max().iloc[0]
#             w52_low = hist_data['Low'].min().iloc[0]
#             print(w52_low)
#             print(hist_data[('Close', stock)].iloc[-2])
#             dchng = hist_data[('Close', stock)].iloc[-2]
#             try:
#                  onemonth = hist_data[('Close', stock)].iloc[-30]
#             except:
#                 print("error in getting the data")
#                 onemonth = "NA"
#             sbuy =  stock_ticker.recommendations['strongBuy'].iloc[0]
#             hold= stock_ticker.recommendations['hold'].iloc[0]
#             ssell = stock_ticker.recommendations['strongSell'].iloc[0]
#             print(sbuy)

#             data.append([stock,mcap_str,cmp,pe,dchng,onemonth,w52_high,w52_low,sector,pb,sbuy,hold,ssell])

#         except:
#             st.write("some issues")

#     df_all_data =pd.DataFrame(data,columns=['stock','mcap_str','cmp','pe','dchng','onemonth','w52_high','w52_low','sector','pb','sbuy','hold','ssell'])

#     #print(df_all_data)
#     st.dataframe(df_all_data.round(2))
