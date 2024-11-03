import streamlit as st
import requests
import json
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="Health Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "http://localhost:5000"

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

def get_random_tip():
    """Fetch random health tip from API"""
    try:
        response = requests.get(f"{API_URL}/tips/random")
        return response.json()
    except Exception as e:
        st.error(f"Error fetching health tip: {str(e)}")
        return None

def send_message(message):
    """Send chat message to API"""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "message": message
            }
        )
        return response.json()
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return None

def submit_feedback(rating, comment):
    """Submit user feedback to API"""
    try:
        response = requests.post(
            f"{API_URL}/feedback",
            json={
                "rating": rating,
                "comment": comment
            }
        )
        return response.json()
    except Exception as e:
        st.error(f"Error submitting feedback: {str(e)}")
        return None

# Sidebar
with st.sidebar:
    st.title("🏥 Health Assistant")
    
    # Display random health tip
    st.subheader("Daily Health Tip")
    if st.button("Get New Tip"):
        tip = get_random_tip()
        if tip:
            st.info(tip['tip'])
    
    # Feedback section
    st.subheader("Feedback")
    rating = st.slider("Rate your experience", 1, 5, 3)
    feedback_comment = st.text_area("Your feedback")
    if st.button("Submit Feedback"):
        if submit_feedback(rating, feedback_comment):
            st.success("Thank you for your feedback!")

# Main chat interface
st.title("💬 Chat with Health Assistant")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get bot response
    response = send_message(prompt)
    if response:
        # Add assistant response to chat history
        assistant_response = response.get('response', "I'm sorry, I couldn't process that request.")
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

# Footer
st.markdown("---")
st.markdown("💡 Tip: Ask any health-related questions in the chat above!")