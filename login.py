import streamlit as st
from st_pages import  hide_pages
from supabase import create_client, Client
import bcrypt
from postgrest.exceptions import APIError
import time
from utils import save_user_id, save_user_cookies
import re


url = st.secrets["db_url"]
key = st.secrets["db_key"]
guser_cred = st.secrets["guser_pwd"]

supabase: Client = create_client(url, key)


st.set_page_config(page_title="Login")

st.markdown("<h1 style='text-align: center; color: #DAA520;font-size: 35px'>The FET Quest - OneView</h1>", unsafe_allow_html=True)

footer = """
<style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: Black;
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 16px;
        z-index: 9999;
        border-top: 1px solid #ccc;
    }
    .stApp {
        padding-bottom: 60px;
    }
</style>
<div class="footer">
    Developed with ❤️ by <strong>The FET Quest</strong>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)


                
def login_form():
    def check_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    with st.form("my_form"):
        user_email = st.text_input("Email").lower()
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:

            valid_email = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user_email)

            if not valid_email:
                st.error("Please Provide valid email address")
                st.stop()

            if not user_email.strip() or not password.strip():
                st.warning("Enter the Credentials to Continue")
            else:
                try:     
                    ret_pwd = (
                        supabase.table("fet_portfolio_users")
                        .select("password_hash").eq("email", user_email).execute()
                    )
                except:
                    print("error in connecting")

                if not ret_pwd.data:
                    st.write("user is not registered")
                else:
                    #write("user is registered")
                    pwd_val = ret_pwd.data[0]['password_hash']
                    val = check_password(password, pwd_val)
                    if val:
                        st.success("Logged in!")
                        try:     
                            user_id = (
                                supabase.table("fet_portfolio_users")
                                .select("user_id","username").eq("email", user_email).execute()
                            )
                        except APIError as e:
                            st.error("Error in fetching the data, Retry after sometime")
                            
                        u_id = user_id.data[0]['user_id']
                        #print(user_id)
                        u_name = user_id.data[0]['username']
                        st.session_state.logged_in=True
                        st.session_state.u_id = u_id
                        st.session_state.u_name = u_name
                        st.session_state["login_method"] = "manual"
                        # st.write(st.session_state.u_id)
                        # st.write(st.session_state.u_name)
                        #save_user_id(str(u_id))
                        save_user_cookies(u_id, u_name)
                        #st.rerun()
                        st.switch_page("pages/portfolio_view.py")
                    else:
                        st.error("Invalid Credentials")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Sign up", type="primary"):
            st.switch_page("pages/signup.py")

    with col2:
        user = getattr(st, "user", None)

        # User not logged in
        if not user or not getattr(user, "is_logged_in", False):
            if st.button("Log in with Google", type="primary"):
                st.login()
            st.stop()

        # User is now logged in (post rerun)
        guser_name = user.name.strip()
        guser_email = user.email.strip().lower()

        with st.spinner("Verifying your profile..."):
            try:
                ret_user = supabase.table("fet_portfolio_users").select("user_id", "username").eq("email", guser_email).execute()
            except APIError as e:
                st.error(f"Database error: {e}")
                st.stop()

            if not ret_user.data:
                supabase.table("fet_portfolio_users").insert({
                    "username": guser_name,
                    "password_hash": guser_email,
                    "email": guser_email
                }).execute()

                ret_user = supabase.table("fet_portfolio_users").select("user_id", "username").eq("email", guser_email).execute()

            user_data = ret_user.data[0]

        # Save session
        st.session_state.logged_in = True
        st.session_state.u_id = user_data["user_id"]
        st.session_state.u_name = user_data["username"]
        st.session_state["login_method"] = "google"

        save_user_cookies(user_data["user_id"], user_data["username"])

        st.success(f"👋 Welcome, {user_data['username']}!")
        st.switch_page("pages/portfolio_view.py")
            
def logout():
    st.logout()
    st.session_state.clear()  # clears all session values
    st.rerun()

def main():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "u_id" not in st.session_state:
        st.session_state.u_id = None
        
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        if st.button("Logout"):
            logout()
            st.experimental_rerun()
        st.write("You are logged in. Navigate to Profile or Dashboard.")
    else:
        #st.title("🔐🔐 Login Page")
        st.markdown("<h1 style='text-align: left; color: #87CEEB;font-size: 25px'>🔐 Login to view your Portfolio</h1>", unsafe_allow_html=True)
        # print("here")
        login_form()

if __name__ == "__main__":
    main()
