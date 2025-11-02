import streamlit as st
import bcrypt
from supabase import create_client, Client, AuthApiError
from postgrest.exceptions import APIError 
import time
import re

st.set_page_config(page_title="Signup",page_icon="the-fet-quest.jpg")

url = st.secrets["db_url"]
key = st.secrets["db_key"]

supabase: Client = create_client(url, key)
st.markdown("<h1 style='text-align: center; color: #FFA500;font-size: 30px'>Sign up for FETQuest OneView - Portfolio</h1>", unsafe_allow_html=True)
def hash_sec_answer(sec_answer: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(sec_answer.encode("utf-8"), salt)
    return hashed.decode("utf-8")

with st.form("my_form"):
    user_name = st.text_input("Enter the User Name")
    Email = st.text_input("Enter the Email").lower()
    password = st.text_input("Password", type="password")
    re_password = st.text_input("Re Enter the Password", type="password")
    security_question = st.selectbox('Select the Security Question',("What was the name of your first school?",
      "What is your mother’s maiden name?","What is the name of the city where you were born?",
      "What was the name of your first pet?","What is your favorite teacher’s name?"))
    security_answer = st.text_input("Enter the security answer").lower()
    submitted = st.form_submit_button("Submit")

    if submitted:

        valid_email = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', Email)
        if not valid_email:
            st.error("Please Provide valid email address")
            st.stop()

        if(password != re_password):
            st.error("Password Didn't Match")
            st.stop()
        
        if len(password) < 6:
            st.error("Password shoule be Mininum 6 Characters")
            st.stop()

        if not security_answer:
            st.error("Please choose and answer the security question")
            st.stop()

        if not password:
            st.error("please enter the password")
            st.stop()
        
        security_answer = security_answer.strip().lower()

        try:
            response = supabase.table("fetquest_oneview_users").select("email").eq("email", Email).execute()
            print(f"respone is {response}")
        except APIError as e:
            st.error(f"{e.message} Issue with sugnup please try later")

        if not response.data:
            try:
              auth_res = supabase.auth.sign_up({
                        "email": Email,
                        "password": password,
                        "options": {
                            "email_redirect_to": "https://fetquest-oneview.streamlit.app/verification"
                        }
                    })
            except APIError as e:
                st.write(e)
                st.stop()

            if auth_res.user:
                hash_answer =  hash_sec_answer(security_answer)
                user_id = auth_res.user.id
                try:
                    insert = (
                        supabase.table("fetquest_oneview_users")
                            .insert({"id":user_id,"username": user_name,"email":Email,"security_question":security_question,"security_answer":hash_answer })
                            .execute()
                        )
                except AuthApiError as e:
                    if "For security purposes" in str(e):
                        wait_time = ''.join([c for c in str(e) if c.isdigit()]) or "60"
                        st.warning(f"Please wait {wait_time} seconds before trying again.")
                    else:
                        st.error(f"Signup failed: {e}")
                
            st.success("🎉 Sign up Sucessful! Check your email for verification!")
            time.sleep(4)
            st.switch_page("login.py")
        else:
            st.write("User Already Exits, Please try to login")

col1, col2 = st.columns(2)

with col1:
    if st.button("Back to login page", type="primary"):
        st.switch_page("login.py")
