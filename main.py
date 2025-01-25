import json
import streamlit as st
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
import boto3
from botocore.exceptions import ClientError

# Cognito configuration
client_id = "7dbc9lthqi1ennc4kaokrdc0r6"  # Your Cognito App Client ID
logout_uri = "https://www.vijaypb.com/"  # Redirect URL after logout
cognito_domain = "https://us-east-1giqb6zif8.auth.us-east-1.amazoncognito.com"  # Your Cognito domain

# Construct the Cognito logout URL
logout_url = f"{cognito_domain}/logout?client_id={client_id}&logout_uri={logout_uri}"

# Title and Description
st.title("Sentiment Analysis App")
st.write("This app analyzes sentiment from a JSON file stored in S3 and displays a donut chart.")

# Sidebar Actions
st.sidebar.header("Actions")

# Add a page link for sign-out using AWS Cognito
st.sidebar.page_link(
    page=logout_url,
    label="Sign Out",
    icon=":material/logout:",
    help="Click to log out using AWS Cognito",
    use_container_width=True
)

# Initialize S3 client using Streamlit secrets
s3_client = boto3.client(
    's3',
    aws_access_key_id=st.secrets["my_aws_key"],
    aws_secret_access_key=st.secrets["my_aws_secret"]
)

# Cache the function to fetch and process data from S3 with a cache key
@st.cache_data
def fetch_feedback_data(last_modified_time):
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
    # Get the last modified time of the file from S3
    response = s3_client.head_object(Bucket=st.secrets["bucket_name"], Key="feedback_updated.json")
    last_modified_time = response["LastModified"]

    # Fetch and process the data with cache invalidation based on last modified time
    feedback_data = fetch_feedback_data(last_modified_time)

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
