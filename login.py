import streamlit as st
from st_pages import  hide_pages
from supabase import create_client, Client, AuthApiError
import bcrypt
from postgrest.exceptions import APIError
import time
from utils import save_user_id, save_user_cookies
import re


url = st.secrets["db_url"]
key = st.secrets["db_key"]
guser_cred = st.secrets["guser_pwd"]

supabase: Client = create_client(url, key)


st.set_page_config(page_title="Login",page_icon="the-fet-quest.jpg")

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
                    ret_user_data = (
                        supabase.table("fetquest_oneview_users")
                        .select("id","username").eq("email", user_email).execute()
                    )
                    print(ret_user_data)
                except:
                    print("error in connecting")

                if not ret_user_data.data:
                    st.write("user is not registered")
                    st.stop()
                else:
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email":  user_email,
                             "password": password
                        })
                        #print(response)
                        user = response.user
                        if not user:
                            st.error("❌ Login failed. Check your credentials.")
                        elif not user.email_confirmed_at:
                            st.warning("⚠️ Please verify your email before logging in.")
                        else:
                            u_id = ret_user_data.data[0]['id']
                            #print(user_id)
                            u_name = ret_user_data.data[0]['username']
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
                    except AuthApiError as e:
                            err_msg = str(e)
                            if "Email not confirmed" in err_msg or "Email not verified" in err_msg:
                                st.warning("Your email is registered but not yet verified. Please check your inbox to verify.")
                                st.stop()
                            else:
                                st.error("Invalid email or password.")
                                st.stop()
                    except Exception as e:
                            st.write(e)
                            st.error("Error in fetching the data, Retry after sometime")
                            st.stop()
                        

    col1, col2= st.columns(2)

    with col1:
        if st.button("Forget Password", type="primary"):
            st.switch_page("pages/password_reset.py")

    with col2:
        if st.button("Sign up", type="primary"):
            st.switch_page("pages/signup.py")

    # with col3:
    #     if st.button("Login with Google", type="primary"):
    #         res = supabase.auth.sign_in_with_oauth({
    #                 "provider": "google",
    #                 "options": {"redirect_to": "http://localhost:8501"}
    #             })

    #         auth_url = res.url
    #         st.markdown(f"[Click here to log in with Google]({auth_url})")
    #         st.stop()

    #         session = supabase.auth.get_session()

    #         if session and session.user:
    #             st.session_state.user = session.user
    #             st.success(f"👋 Welcome {session.user.email}")
    #         else:
    #             st.info("Please log in to continue.")
            
        # if not getattr(st, "user", None) or not getattr(st.user, "is_logged_in", False):
        #     if st.button("Log in with Google", type="primary"):
        #         st.login()
        #     st.stop()

        # guser_name = st.user.name.strip()
        # guser_email = st.user.email.strip().lower()

        # try:
        #     ret_user = supabase.table("fet_portfolio_users").select("user_id", "username").eq("email", guser_email).execute()
        # except APIError as e:
        #     st.error(f"Database error: {e}")
        #     st.stop()

        # if not ret_user.data:
        #     try:
        #         supabase.table("fet_portfolio_users").insert({
        #             "username": guser_name,
        #             "password_hash": guser_email,  # or any dummy value
        #             "email": guser_email
        #         }).execute()
        #     except APIError as e:
        #         st.error(f"Error inserting user: {e}")
        #         st.stop()

        
        # ret_user = supabase.table("fet_portfolio_users").select("user_id", "username").eq("email", guser_email).execute()
        # st.session_state.clear()   
        # user_data = ret_user.data[0]
        # st.session_state.logged_in = True
        # st.session_state.u_id = user_data["user_id"]
        # st.session_state.u_name = user_data["username"]
        # st.session_state["login_method"] = "google"

        # save_user_cookies(user_data["user_id"], user_data["username"])
        # st.success(f"👋 Logged in as {user_data['username']}")
        # st.switch_page("pages/portfolio_view.py")
            
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