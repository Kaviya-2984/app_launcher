from typing import List, Union, Dict
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from .tools import TextEditorTool

class WritingAgent:
    def __init__(self, llm):
        self.llm = llm
        self.tools = self._setup_tools()
        self.agent = self._setup_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True,
            handle_parsing_errors="Check your output and make sure it conforms!",
            max_iterations=3,
            early_stopping_method="generate"
        )
    
    def _setup_tools(self) -> List[Tool]:
        """Initialize and return the tools for the agent."""
        editor = TextEditorTool(self.llm)
        
        return [
            Tool(
                name="text_editor",
                func=editor.write_to_file,
                description="Useful ONLY for writing content to text files or word processors. "
                           "Input MUST be a string containing ONLY the topic to write about. "
                           "Example: 'Artificial intelligence'"
            )
        ]
    
    def _setup_agent(self):
        """Initialize and return the agent with strict prompt engineering."""
        prompt = hub.pull("hwchase17/react-chat")   
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
            tools_renderer=lambda tools: "\n".join(
            [f"{tool.name}: {tool.description}" for tool in tools]
        )
        )
        
        return agent
    
    def _process_writing_request(self, input_text: str) -> str:
        """Clean and prepare the writing request."""
        remove_phrases = [
            "write about", "write an essay about", 
            "create a document about", "compose text about",
            "open notepad.exe", "in notepad"
        ]
        text = input_text.lower()
        for phrase in remove_phrases:
            text = text.replace(phrase, "")
        return text.strip()
    
    def _extract_app_name(self, input_text: str) -> str:
        """Extract the application name from the input text."""
        input_text = input_text.lower()
        if 'winword.exe' in input_text:
            return 'winword.exe'
        elif 'wordpad.exe' in input_text:
            return 'wordpad.exe'
        return 'notepad.exe'
    
    def _extract_topic(self, input_text: str) -> str:
        """Extract the writing topic from the input text."""
        phrases = ["write about", "write an essay about", "create a document about", "compose text about"]
        for phrase in phrases:
            if phrase in input_text.lower():
                return input_text.lower().split(phrase)[1].strip()
        return input_text
    
    def run(self, input_text: str, chat_history: List[Union[HumanMessage, AIMessage]] = None) -> str:
        """Run the agent with the given input."""
        try:
            if chat_history is None:
                chat_history = []
            
            # Process the input to extract just the writing topic
            clean_input = self._process_writing_request(input_text)
            
            result = self.agent_executor.invoke({
                "input": clean_input,
                "chat_history": chat_history
            })
            
            # Handle the Notepad case specifically
            if "open notepad.exe" in input_text.lower():
                return f"Opened Notepad and wrote about: {clean_input}"
            return result["output"]
            
        except Exception as e:
            return f"Error processing your request: {str(e)}"