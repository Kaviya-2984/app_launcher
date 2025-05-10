import os
import json
import re
from typing import List, Dict, Union
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain import hub

class FileHandlingAgent:
    def __init__(self, llm):
        self.llm = llm
        self.tools = self._setup_tools()
        self.agent = self._setup_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )

    def _setup_tools(self) -> List[Tool]:
        return [
            Tool(
                name="file_operations",
                func=FileOperationsTool().execute_operation,
                description="Handles folder creation and directory listing. "
                          "Input should be a JSON object with 'operation' and 'path'"
            )
        ]

    def _setup_agent(self):
        prompt = hub.pull("hwchase17/react-chat")
        return create_react_agent(self.llm, self.tools, prompt)

    def run(self, input_text: str, chat_history: List = None) -> str:
        try:
            result = self.agent_executor.invoke({
                "input": input_text,
                "chat_history": chat_history or []
            })
            return result["output"]
        except Exception as e:
            return f"Error: {str(e)}"

class FileOperationsTool:
    def __init__(self):
        self.drive_map = {
            'd drive': "D:\\",
            'e drive': "E:\\",
            'd-desk': "D:\\",
            'e-desk': "E:\\"
        }

    def _resolve_path(self, path: str) -> str:
        """Convert natural language paths to valid Windows paths while preserving spaces"""
        # Replace drive shortcuts first
        for shortcut, actual_path in self.drive_map.items():
            if shortcut in path.lower():
                path = path.lower().replace(shortcut, actual_path)
                break
        
        # Clean path without modifying spaces
        path = path.replace("/", "\\").strip()
        return os.path.abspath(path)

    def execute_operation(self, input_data: Union[str, Dict]) -> str:
        """Handle both natural language and structured inputs"""
        try:
            # Parse input
            if isinstance(input_data, str):
                try:  # First try to parse as JSON
                    input_data = json.loads(input_data)
                except json.JSONDecodeError:  # Fallback to natural language
                    input_data = self._parse_natural_language(input_data)

            operation = input_data.get("operation", "list").lower()
            path = self._resolve_path(input_data.get("path", ""))
            
            if operation == "create_folder":
                return self._create_folder(path)
            elif operation == "list":
                return self._list_directory(path)
            return "Unsupported operation"
        
        except Exception as e:
            return f"Operation failed: {str(e)}"

    def _parse_natural_language(self, text: str) -> Dict:
        """Improved natural language parsing with space handling"""
        text = text.lower().strip()
        operation = "list"
        
        # Create folder pattern
        if "create folder" in text:
            operation = "create_folder"
            match = re.search(r'create folder (?:named|called|as)? ?"?([\w\s-]+)"? (?:in|on|at) (d|e) drive', text)
            if match:
                folder_name = match.group(1).strip()
                drive = f"{match.group(2).upper()}:\\"
                return {
                    "operation": operation,
                    "path": os.path.join(drive, folder_name)
                }
        
        # List pattern with space handling
        if "list" in text:
            match = re.search(r'(?:in|on|at) (d|e) drive(?: in ([\w\s-]+) folder)?', text)
            if match:
                drive = f"{match.group(1).upper()}:\\"
                folder = match.group(2).strip() if match.group(2) else ""
                return {
                    "operation": "list",
                    "path": os.path.join(drive, folder)
                }
        
        return {"operation": "list", "path": "D:\\"}

    def _list_directory(self, path: str) -> str:
        """List directory contents with better formatting"""
        try:
            if not os.path.exists(path):
                return f"Path does not exist: {path}"
                
            items = os.listdir(path)
            # Create markdown-formatted list
            items_list = "\n".join(
                [f"- 📁 {item}" if os.path.isdir(os.path.join(path, item)) 
                 else f"- 📄 {item}" for item in items]
            )
            return f"**Contents of {path}:**\n\n{items_list}"
        except Exception as e:
            return f"Listing failed: {str(e)}"

    def _create_folder(self, path: str) -> str:
        """Create folder with validation"""
        try:
            if not path.lower().startswith(("d:\\", "e:\\")):
                return "Error: Can only create folders in D or E drives"
                
            os.makedirs(path, exist_ok=True)
            return f"Successfully created folder: {path}"
        except Exception as e:
            return f"Error creating folder: {str(e)}"