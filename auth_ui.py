import streamlit as st
from database import authenticate_user, create_user, create_workspace

def render_auth_page():
    """Renders the Login and Registration landing page."""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<h1 style='text-align: center;'>🤖 AI Knowledge Hub</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Sign in or create an account to access your personal AI workspaces and search history.</p>", unsafe_allow_html=True)
        st.markdown("---")

        tab_login, tab_signup = st.tabs(["🔐 Sign In", "✨ Create Account"])

        # --- SIGN IN TAB ---
        with tab_login:
            st.subheader("Welcome Back")
            with st.form("login_form"):
                username = st.text_input("Username").strip()
                password = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Sign In", use_container_width=True)

                if submit_login:
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    else:
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state.user = user
                            st.session_state.authenticated = True
                            st.success(f"Welcome back, {user['username']}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password. Please try again.")

        # --- SIGN UP TAB ---
        with tab_signup:
            st.subheader("Create New Account")
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username").strip()
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                initial_workspace = st.text_input("First Workspace Name (optional)", value="My Workspace").strip()

                submit_signup = st.form_submit_button("Create Account", use_container_width=True)

                if submit_signup:
                    if not new_username or not new_password:
                        st.error("Username and password are required.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(new_password) < 4:
                        st.error("Password must be at least 4 characters.")
                    else:
                        success, msg = create_user(new_username, new_password)
                        if success:
                            # If custom workspace name provided and not default
                            user = authenticate_user(new_username, new_password)
                            if user and initial_workspace and initial_workspace != "Default Workspace":
                                create_workspace(user["id"], initial_workspace, "Primary workspace")
                            st.success(msg)
                            st.info("You can now switch to the 'Sign In' tab to log in!")
                        else:
                            st.error(msg)
