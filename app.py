import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from app_launcher_agent.agent import AppLauncherAgent
from app_launcher_agent.utils import format_chat_history
from dotenv import load_dotenv
import os

# Initialize your LLM (this would be your actual implementation)
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Initialize the LLM with your custom configuration
def initialize_llm():
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,
        base_url="https://api.nexus.navigatelabsai.com",
        api_key=os.getenv("API_KEY")  # Store your API key in .env file
    )

# Initialize the Streamlit app
def main():
    # Set page config
    st.set_page_config(
        page_title="AI App Launcher",
        page_icon="🚀",
        layout="centered"
    )
    
    # Inject custom CSS
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "agent" not in st.session_state:
        llm = initialize_llm()
        st.session_state.agent = AppLauncherAgent(llm)
    
    # Header
    st.title("🚀 AI App Launcher")
    st.markdown("""
    This AI assistant can open applications on your computer. 
    Try asking it to open apps like Chrome, Notepad, or Calculator.
    """)
    
    # Display chat history
    for message in format_chat_history(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    user_input = st.chat_input("What app would you like to open?")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append(HumanMessage(content=user_input))
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get AI response
        ai_response = st.session_state.agent.run(
            user_input,
            st.session_state.chat_history
        )
        
        # Add AI response to chat history
        st.session_state.chat_history.append(AIMessage(content=ai_response))
        
        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(ai_response)

if __name__ == "__main__":
    main()