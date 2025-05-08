from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from typing import List, Union
from .tools import AppLauncherTool

class AppLauncherAgent:
    def __init__(self, llm):
        self.llm = llm
        self.tools = self._setup_tools()
        self.agent = self._setup_agent()
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    def _setup_tools(self) -> List[Tool]:
        """Initialize and return the tools for the agent."""
        launcher = AppLauncherTool()
        
        return [
            Tool(
                name="app_launcher",
                func=launcher.launch_app,
                description="Useful for launching applications on Windows computers. "
               "For Windows apps, use exact names like 'notepad.exe', 'calc.exe', 'chrome.exe'. "
               "For Microsoft Office apps, use 'winword.exe', 'excel.exe', 'powerpnt.exe'."
)
        ]
    
    def _setup_agent(self):
        """Initialize and return the agent."""
        prompt = hub.pull("hwchase17/react-chat")
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return agent
    
    def run(self, input_text: str, chat_history: List[Union[HumanMessage, AIMessage]] = None) -> str:
        """Run the agent with the given input."""
        try:
            if chat_history is None:
                chat_history = []
            
            result = self.agent_executor.invoke({
                "input": input_text,
                "chat_history": chat_history
            })
            
            return result["output"]
        except Exception as e:
            return f"Error processing your request: {str(e)}"