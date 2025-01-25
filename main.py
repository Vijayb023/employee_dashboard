import streamlit as st

# Cognito Configuration
client_id = "7dbc9lthqi1ennc4kaokrdc0r6"  # Your Cognito App Client ID
logout_uri = "https://www.vijaypb.com/"  # URL to redirect after logout
cognito_domain = "https://us-east-1giqb6zif8.auth.us-east-1.amazoncognito.com"  # Your Cognito domain

# Generate the Cognito logout URL
logout_url = f"{cognito_domain}/logout?client_id={client_id}&logout_uri={logout_uri}"

# Generate a styled logout button with Cognito logout functionality
def styled_cognito_logout_button():
    logout_html = f"""
    <style>
        .logout-btn {{
            display: inline-block;
            background-color: #FF4B4B;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            font-size: 16px;
            border-radius: 5px;
            text-align: center;
            cursor: pointer;
        }}
        .logout-btn:hover {{
            background-color: #D43F3F;
        }}
    </style>
    <script>
        function signOutRedirect() {{
            // Clear tokens from localStorage and sessionStorage
            localStorage.clear();
            sessionStorage.clear();

            // Redirect to the Cognito logout URL
            window.top.location.href = "{logout_url}";
        }}
    </script>
    <button class="logout-btn" onclick="signOutRedirect()">Sign Out</button>
    """
    st.sidebar.markdown(logout_html, unsafe_allow_html=True)

# Add the Cognito sign-out button to the sidebar
st.sidebar.header("Actions")
styled_cognito_logout_button()

# Title and Description (example content)
st.title("AWS Cognito Logout Example")
st.write("Click 'Sign Out' in the sidebar to log out using AWS Cognito.")

# Placeholder for other app content
st.write("Add your app's main functionality here.")
