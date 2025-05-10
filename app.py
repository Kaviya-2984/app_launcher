import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from app_launcher_agent.agent import AppLauncherAgent
from app_launcher_agent.writer_agent import WritingAgent
from app_launcher_agent.file_agent import FileHandlingAgent
from app_launcher_agent.code_agent import CodeGenerationAgent
from app_launcher_agent.calculation_agent import CalculationAgent
from app_launcher_agent.utils import format_chat_history
from app_launcher_agent.system_agent import SystemControlAgent
from dotenv import load_dotenv
import os
os.environ["LANGCHAIN_HANDLER"] = "false"

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
    
    # Initialize LLM first
    if "llm" not in st.session_state:
        st.session_state.llm = initialize_llm()
    
    # Then initialize agents that depend on LLM
    if "calc_agent" not in st.session_state:
        st.session_state.calc_agent = CalculationAgent(st.session_state.llm)

    if "app_agent" not in st.session_state:
        st.session_state.app_agent = AppLauncherAgent(st.session_state.llm)
    
    if "writer_agent" not in st.session_state:
        st.session_state.writer_agent = WritingAgent(st.session_state.llm)
    
    if "file_agent" not in st.session_state:
        st.session_state.file_agent = FileHandlingAgent(st.session_state.llm)

    if "code_agent" not in st.session_state:
        st.session_state.code_agent = CodeGenerationAgent(st.session_state.llm)
    if "system_agent" not in st.session_state:
        st.session_state.system_agent = SystemControlAgent(st.session_state.llm)    
        
    st.title("🚀 CLICKLESS ")
    st.markdown("""
    Control everything with just your words!
               
    """)
    
    for message in format_chat_history(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Only ONE chat_input with a unique key
    user_input = st.chat_input("What would you like me to do?", key="main_chat_input")

    if user_input is not None and user_input.strip() != "":
        clean_input = user_input.strip()

        st.session_state.chat_history.append(HumanMessage(content=clean_input))

        with st.chat_message("user"):
            st.markdown(clean_input)
        
        # Determine agent
        
        if any(kw in clean_input.lower() for kw in ["write", "essay", "article"]):
            if "[CODEREQUEST]" in clean_input:  # Check for code flag
                agent = st.session_state.code_agent
                clean_input = clean_input.replace("[CODEREQUEST]", "").strip()
            else:
                agent = st.session_state.writer_agent

        elif any(kw in clean_input.lower() for kw in ["list", "create"]):
            agent = st.session_state.file_agent

        elif any(kw in clean_input.lower() for kw in ["calculate", "+", "-", "*", "/", "="]):
            agent = st.session_state.calc_agent

        elif any(kw in clean_input.lower() for kw in ["open", "launch", "start"]):
            agent = st.session_state.app_agent
            
        elif any(kw in clean_input.lower() for kw in ["code", "program", "algorithm", "function"]):
            agent = st.session_state.code_agent

        elif any(kw in clean_input.lower() for kw in ["brightness", "volume", "bluetooth", "system"]):
            agent = st.session_state.system_agent
        else:
            agent = st.session_state.app_agent
        
        # Get response
        try:
            with st.spinner("Processing..."):
                result = agent.run(clean_input, st.session_state.chat_history)
        except Exception as e:
            result = f"Error: {str(e)}"

        with st.chat_message("assistant"):
            st.markdown(result)    
        
        st.session_state.chat_history.append(AIMessage(content=result))
        
        # Display response
        st.rerun()

if __name__ == "__main__":
    main()