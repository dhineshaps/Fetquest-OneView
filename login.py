import streamlit as st
from st_pages import  hide_pages
from supabase import create_client, Client
import bcrypt
from postgrest.exceptions import APIError
import time
from utils import save_user_id

url="https://anpufhhyswexjgwwddcy.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFucHVmaGh5c3dleGpnd3dkZGN5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NzM2ODEsImV4cCI6MjA1OTQ0OTY4MX0.aP4NCS53RezlAsBvAxmzqKUFYtL8azVRbsKnnGCTWmk"

supabase: Client = create_client(url, key)

#
#https://stackoverflow.com/questions/78624469/simplest-way-to-hide-a-page-from-streamlit-sidebar
# Important: page title must match sidebar label
#hide_pages(["Signup"])

st.set_page_config(page_title="Login")

def login_form():
    def check_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    with st.form("my_form"):
        st.write("Login Form")
        user_name = st.text_input("Enter the Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Submit")
        if submitted:
            if not user_name.strip() or not password.strip():
                st.warning("Enter the Creds to Continue")
            else:
                try:     
                    ret_pwd = (
                        supabase.table("fet_portfolio_users")
                        .select("password_hash").eq("email", user_name).execute()
                    )
                except:
                    print("error in connecting")

                if not ret_pwd.data:
                    st.write("user is not registered")
                else:
                    st.write("user is registered")
                    pwd_val = ret_pwd.data[0]['password_hash']
                    val = check_password(password, pwd_val)
                    if val:
                        st.success("Logged in!")
                        try:     
                            user_id = (
                                supabase.table("fet_portfolio_users")
                                .select("user_id").eq("email", user_name).execute()
                            )
                        except APIError as e:
                            st.error("Error in fetching the data, Retry after sometime")
                            
                        u_id = user_id.data[0]['user_id']
                        st.session_state.logged_in=True
                        st.session_state.u_id = u_id
                        st.write(st.session_state.u_id)
                        save_user_id(str(u_id))
                        #st.rerun()
                        st.switch_page("pages/portfolio.py")
                    else:
                        st.error("Invalid Credentials")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Sign up", type="primary"):
            st.switch_page("pages/signup.py")

    with col2:
        st.button("Login with Google", type="primary")
    
def logout():
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
        st.write("You are logged in. Navigate to Profile or Dashboard.")
    else:
        st.title("🔐 Login Page")
        print("here")
        login_form()

if __name__ == "__main__":
    main()
