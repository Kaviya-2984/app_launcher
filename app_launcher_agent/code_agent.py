from typing import List, Union
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain import hub
from langchain_core.messages import AIMessage, HumanMessage
from .tools import CodeGenerationTool

class CodeGenerationAgent:
    def __init__(self, llm):
        self.llm = llm
        self.tools = self._setup_tools()
        self.agent = self._setup_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=4
        )
    
    def _setup_tools(self) -> List[Tool]:
        """Initialize and return the tools for code generation."""
        code_tool = CodeGenerationTool(self.llm)
        
        return [
            Tool(
                name="code_generator",
                func=code_tool.generate_and_write_code,
                description="Useful for generating code snippets and writing them to text editors. "
                          "Input should specify language, problem, and editor. "
                          "Example: 'Python Fibonacci in notepad.exe'"
            )
        ]
    
    def _setup_agent(self):
        """Initialize and return the agent."""
        prompt = hub.pull("hwchase17/react-chat")
        return create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
    
    def _parse_input(self, input_text: str) -> dict:
        """Parse user input to extract language, problem, and editor."""
        input_lower = input_text.lower()
        editor = "notepad.exe"
        language = "python"
        
        # Detect editor
        editors = {
            "notepad.exe": ["notepad", "notepad.exe"],
            "winword.exe": ["word", "winword.exe"],
            "wordpad.exe": ["wordpad", "wordpad.exe"]
        }
        for ed, keywords in editors.items():
            if any(kw in input_lower for kw in keywords):
                editor = ed
                break
                
        # Detect language
        languages = {
            "python": ["python", "py"],
            "java": ["java"],
            "c++": ["c++", "cpp"],
            "javascript": ["javascript", "js"]
        }
        for lang, keywords in languages.items():
            if any(kw in input_lower for kw in keywords):
                language = lang
                break
                
        # Extract problem statement
        problem = input_text
        for kw in [*editors.values(), *languages.values()]:
            for k in kw:
                problem = problem.replace(k, "")
        problem = problem.replace("write", "").replace("code for", "").strip()
        
        return {
            "language": language,
            "problem": problem,
            "editor": editor
        }
    
    def run(self, input_text: str, chat_history: List[Union[HumanMessage, AIMessage]] = None) -> str:
        """Run the agent with the given input."""
        try:
            parsed = self._parse_input(input_text)
            result = self.agent_executor.invoke({
                "input": f"Generate {parsed['language']} code for {parsed['problem']} and write to {parsed['editor']}",
                "chat_history": chat_history or []
            })
            return result["output"]
        except Exception as e:
            return f"Error generating code: {str(e)}"