import streamlit as st
from supabase import create_client, Client
import bcrypt
import time

st.set_page_config(page_title="Login",page_icon="the-fet-quest.jpg")

SUPABASE_URL = st.secrets["db_url"]
SUPABASE_KEY = st.secrets["db_key_service"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
st.markdown("<h1 style='text-align: center; color: #FFA500;font-size: 30px'>FETQuest OneView - Portfolio</h1>", unsafe_allow_html=True)
st.title("🔑 Password Reset")

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "show_reset_form" not in st.session_state:
    st.session_state.show_reset_form = False

def check_security_answer(security_answer: str, hashed: str) -> bool:
    return bcrypt.checkpw(security_answer.encode("utf-8"), hashed.encode("utf-8"))

# Step 1: Enter email
email = st.text_input("Enter the email:")

# Step 2: Use session_state flag to control visibility
if "show_reset_form" not in st.session_state:
    st.session_state.show_reset_form = False

if st.button("Proceed to change the Password",type="primary"):
    if not email:
        st.warning("⚠️ Please enter user's email.")
        st.stop()
    else:
        try:
            users = supabase.auth.admin.list_users()

            if hasattr(users, "users"):
                user_list = users.users
            elif isinstance(users, list):
                user_list = users
            else:
                st.error("Unexpected response from Supabase.")
                st.stop()

            matched_user = next(
                (u for u in user_list if hasattr(u, "email") and u.email.lower() == email.lower()),
                None
            )

            if not matched_user:
                st.error(f"❌ No user found for {email}")
            else:
                st.session_state.user_id = getattr(matched_user, "id", None)
                st.session_state.show_reset_form = True 
        except Exception as e:
            st.error(f"Error: {e}")

# Step 3: Display form only if valid email found
if st.session_state.show_reset_form:
    try:
        response_ques = (
            supabase.table("fetquest_oneview_users")
            .select("security_question")
            .eq("email", email.lower())
            .execute()
        )
    except Exception as e:
        st.error(f"Error fetching question: {e}")
        st.stop()

    with st.form("reset_password_form"):
        new_password = st.text_input("Enter new password", type="password")
        confirm_password = st.text_input("Confirm new password", type="password")
        st.write(f"**Security Question:** {response_ques.data[0]['security_question']}")
        security_answer = st.text_input("Your Answer").strip()

        submitted = st.form_submit_button("Change password", type="primary")

        if submitted:
            if new_password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif len(new_password) < 6:
                st.warning("⚠️ Password must be at least 6 characters long.")
                st.stop()
            elif not security_answer:
                st.error("❌ Security Answer required to proceed.")
            else:
                try:     
                    ret_sec_answer = (
                        supabase.table("fetquest_oneview_users")
                        .select("security_answer").eq("email", email).execute()
                    )
                except Exception as e:
                    st.error(f"Error fetching question: {e}")
                    st.stop()

                security_answer_db_val = ret_sec_answer.data[0]['security_answer']
                val = check_security_answer(security_answer.lower(), security_answer_db_val)
                if val:
                    try:
                        supabase.auth.admin.update_user_by_id(
                            st.session_state.user_id,
                            {"password": new_password}
                        )
                    except Exception as e:
                        st.error(f"Error fetching question: {e}")
                        st.stop()
                    st.success(f"✅ Password reset successfully for {email}!")
                    time.sleep(4)
                    st.session_state.show_reset_form = False
                else:
                    st.error("Security Answer not matched")
col1, col2 = st.columns(2)

with col1:
    if st.button("Back to login page"):
        st.switch_page("login.py")