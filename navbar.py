import streamlit as st

def top_navbar():
    # --- CSS: navbar + page_link styling ---
    st.markdown(
        """
        <style>
        .navbar {{
            display: flex;
            align-items: center;
            background-color: #1e1e2f;
            padding: 0.75rem 1rem;
            gap: 2rem;
            position: sticky;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid #333;
        }}
        .navbar a {{
            color: #ccc;
            text-decoration: none;
            font-weight: 500;
            padding: 0.4rem 0.6rem;
            border-radius: 6px;
            transition: all 0.2s ease;
        }}
        .navbar a:hover {{
            color: white;
            background-color: #2b2b3d;
        }}
        .navbar a.active {{
            color: white;
            background-color: #4e9af1;
        }}
        .navbar .right {{
            margin-left: auto;
        }}
        </style>

        """,
        unsafe_allow_html=True,
    )

    left_col, middle_col, right_col = st.columns([2, 2, 1])

    # --- NAVBAR layout using columns so Logout stays to the right ---
    #left_col, middle_col, right_col = st.columns([3, 3, 1])
    with left_col:
        # place two page links next to each other (internal navigation)
        st.page_link("pages/1_View_Portfolio.py", label="View Portfolio")
        # st.page_link("pages/2_Manage_Portfolio.py", label="Manage Portfolio")

    with middle_col:
        st.page_link("pages/2_Manage_Portfolio.py", label="Manage Portfolio")

    with right_col:
        if st.button("Logout"):
            st.session_state.clear()
            st.switch_page("login_new.py")

    # --- JS: add 'active-link' class to the anchor whose text matches current page ---
    page_name = st.session_state.get("current_page", "")
    if page_name:
        # JS runs in the browser and finds the page_link anchors by their data-testid,
        # comparing visible text to the current page name and toggling the class.
        st.markdown(
            f"""
            <script>
            (function() {{
                const pageName = "{page_name}";
                const anchors = window.parent.document.querySelectorAll('a[data-testid="stPageLink-NavLink"]');
                anchors.forEach(a => {{
                    // anchor.innerText sometimes contains whitespace; trim it
                    if (a.innerText && a.innerText.trim() === pageName) {{
                        a.classList.add('active-link');
                    }} else {{
                        a.classList.remove('active-link');
                    }}
                }});
            }})();
            </script>
            """,
            unsafe_allow_html=True,
        )
