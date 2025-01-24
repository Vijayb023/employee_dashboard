import json
import streamlit as st
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
import boto3
from botocore.exceptions import ClientError

# Cognito configuration
client_id = "7dbc9lthqi1ennc4kaokrdc0r6"  # Cognito client ID
logout_uri = "https://www.vijaypb.com/"  # Redirect URL after logout
cognito_domain = "https://us-east-1giqb6zif8.auth.us-east-1.amazoncognito.com"  # Cognito domain

# Construct the logout URL
logout_url = f"{cognito_domain}/logout?client_id={client_id}&logout_uri={logout_uri}"

# Clear session, cache, and redirect to logout URL
def clear_session_and_logout():
    # Clear session state (e.g., tokens or user data)
    for key in st.session_state.keys():
        del st.session_state[key]
    
    # Clear Streamlit cache
    st.cache_data.clear()  # Clear cached data
    st.cache_resource.clear()  # Clear cached resources

    # JavaScript to perform a hard redirect
    js_redirect = f"""
        <script>
            window.localStorage.clear();  // Clear any localStorage (optional for stored tokens)
            window.sessionStorage.clear();  // Clear sessionStorage (optional for tokens)
            window.location.replace("{logout_url}");
        </script>
    """
    st.markdown(js_redirect, unsafe_allow_html=True)

# Title and Description
st.title("Sentiment Analysis App")
st.write("This app analyzes sentiment from a JSON file stored in S3 and displays a donut chart.")

# Sign Out Popup Modal
def sign_out_popup():
    with st.modal("Sign Out", closable=True) as modal:
        st.subheader("Confirm Sign Out")
        st.write("Are you sure you want to sign out? You will be redirected to the home page.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Sign Out"):
                clear_session_and_logout()
                st.stop()  # Stop Streamlit script execution
        
        with col2:
            if st.button("Cancel"):
                st.write("Sign-out canceled.")

# Sidebar Sign Out Button
if st.sidebar.button("Sign Out"):
    sign_out_popup()

# Initialize S3 client using Streamlit secrets
s3_client = boto3.client(
    's3',
    aws_access_key_id=st.secrets["my_aws_key"],
    aws_secret_access_key=st.secrets["my_aws_secret"]
)

# Cache the function to fetch and process data from S3
@st.cache_data
def fetch_feedback_data():
    # Fetch the object from S3
    response = s3_client.get_object(Bucket=st.secrets["bucket_name"], Key="feedback_updated.json")

    # Read and decode the body content
    content = response["Body"].read().decode("utf-8")

    # Load the JSON data
    data = json.loads(content)

    # Extract feedback messages
    feedback_list = [item['feedback'] for item in data]

    # Convert to a DataFrame
    feedback_data = pd.DataFrame(feedback_list, columns=["feedback"])

    # Analyze Sentiment
    def get_sentiment(text):
        analysis = TextBlob(text)
        if analysis.sentiment.polarity > 0:
            return "Positive"
        elif analysis.sentiment.polarity < 0:
            return "Negative"
        else:
            return "Neutral"

    feedback_data["Sentiment"] = feedback_data["feedback"].apply(get_sentiment)

    return feedback_data

try:
    # Fetch and process the data
    feedback_data = fetch_feedback_data()

    # Sentiment Counts
    sentiment_counts = feedback_data["Sentiment"].value_counts()

    # Plot Donut Chart
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        sentiment_counts,
        labels=sentiment_counts.index,
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops=dict(width=0.4)
    )
    ax.set_title("Sentiment Analysis")
    plt.setp(autotexts, size=10, weight="bold")

    # Display Chart
    st.pyplot(fig)

    # Display DataFrame
    st.subheader("Feedback with Sentiments")
    st.write(feedback_data)

    # Display Feedback Messages
    st.subheader("Extracted Feedback Messages")
    for i, feedback in enumerate(feedback_data["feedback"], start=1):
        st.write(f"{i}. {feedback.strip().capitalize()}")

except Exception as e:
    st.error(f"An error occurred: {e}")
