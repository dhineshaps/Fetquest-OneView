import streamlit as st
# Initialize flag only once
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Define callback function to set the flag
def form_callback():
    st.session_state.submitted = True

# Show button only if not submitted
if not st.session_state.submitted:
    st.button("My Button", on_click=form_callback)

# You can add anything after submission
if st.session_state.submitted:
    st.write("Button is now hidden after submission.")
    st.write("More content here...")