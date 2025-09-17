import streamlit as st

st.title("My Streamlit App")

# Create two tabs
tab1, tab2 = st.tabs(["Operation 1", "Operation 2"])

with tab1:
    st.header("First Operation")
    number = st.number_input("Enter a number")
    st.write("Square:", number ** 2)

with tab2:
    st.header("Second Operation")
    text = st.text_input("Enter some text")
    st.write("Reversed:", text[::-1])