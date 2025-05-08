import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from app_launcher_agent.agent import AppLauncherAgent
from app_launcher_agent.writer_agent import WritingAgent
from app_launcher_agent.utils import format_chat_history
from dotenv import load_dotenv
import os

# Initialize your LLM (same as before)
from langchain_openai import ChatOpenAI

load_dotenv()

def initialize_llm():
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,
        base_url="https://api.nexus.navigatelabsai.com",
        api_key=os.getenv("API_KEY")
    )

def main():
    st.set_page_config(
        page_title="AI Assistant",
        page_icon="🚀",
        layout="centered"
    )
    
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "llm" not in st.session_state:
        st.session_state.llm = initialize_llm()
    
    if "app_agent" not in st.session_state:
        st.session_state.app_agent = AppLauncherAgent(st.session_state.llm)
    
    if "writer_agent" not in st.session_state:
        st.session_state.writer_agent = WritingAgent(st.session_state.llm)
    
    st.title("🚀 AI Assistant")
    st.markdown("""
    This AI assistant can:
    - Open applications on your computer
    - Generate and write content to text editors
    """)
    
    for message in format_chat_history(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    user_input = st.chat_input("What would you like me to do?")
    
    if user_input:
        st.session_state.chat_history.append(HumanMessage(content=user_input))
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Determine which agent to use
        if any(keyword in user_input.lower() for keyword in ["write", "essay", "article", "compose"]):
            result = st.session_state.writer_agent.run(
                user_input,
                st.session_state.chat_history
            )
        else:
            result = st.session_state.app_agent.run(
                user_input,
                st.session_state.chat_history
            )
        
        st.session_state.chat_history.append(AIMessage(content=result))
        
        with st.chat_message("assistant"):
            st.markdown(result)

if __name__ == "__main__":
    main()