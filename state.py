import streamlit as st

if 'key' not in st.session_state:
    st.session_state['key'] = 'value'

st.write(st.session_state.key)

for k in st.session_state.keys():
    st.write(k)