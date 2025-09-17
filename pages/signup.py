import streamlit as st
import bcrypt
from supabase import create_client, Client
from postgrest.exceptions import APIError
import time

st.set_page_config(page_title="Signup")

url="https://anpufhhyswexjgwwddcy.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFucHVmaGh5c3dleGpnd3dkZGN5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NzM2ODEsImV4cCI6MjA1OTQ0OTY4MX0.aP4NCS53RezlAsBvAxmzqKUFYtL8azVRbsKnnGCTWmk"

supabase: Client = create_client(url, key)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

with st.form("my_form"):
    st.write("Sign up")
    user_name = st.text_input("Enter the User Name")
    Email = st.text_input("Enter the Email")
    password = st.text_input("Password", type="password")
    re_password = st.text_input("Re Enter the Password", type="password")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if(password != re_password):
            st.error("Password Didn't Match")
        hash_pwd =  hash_password(password )
        try:
            insert = (
                supabase.table("fet_portfolio_users")
                    .insert({"username": user_name, "password_hash": hash_pwd ,"email":Email})
                    .execute()
                )
        except APIError as e:
            st.error(f"{e.message.split(" ")[-1].split("_")[-2].upper()} already exits, try to login with it.")
            st.stop()

        st.success("Sign up sucessfull, now login with credentials")
        time.sleep(2.4)
        st.switch_page("login.py")
        #st.success("redirecting")




col1, col2 = st.columns(2)

with col1:
    if st.button("Back to login page", type="primary"):
        st.switch_page("login.py")

with col2:
    st.button("Login with Google", type="primary")

# with st.sidebar:
#     with st.echo():
#         st.write("this side")