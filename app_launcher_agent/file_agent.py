import os
import subprocess
import shutil
import json
import re
from typing import List, Dict, Optional, Union
from pathlib import Path
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
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
            max_iterations=5
        )

    def _setup_tools(self) -> List[Tool]:
        """Initialize and return the tools for file operations."""
        file_tool = FileOperationsTool()
        
        return [
            Tool(
                name="file_operations",
                func=file_tool.execute_file_operation,
                description="Useful for file/folder operations. Input format: "
                          "{'operation': '...', 'path': '...', 'content'(optional): '...'}"
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

    def _parse_file_command(self, input_text: str) -> Dict:
        """Parse natural language command into file operation dictionary."""
        input_text = input_text.lower()
        operation_map = {
            "list": ["list", "show", "display"],
            "create_folder": ["create folder", "make directory", "new folder"],
            "create_file": ["create file", "make file", "new file"],
            "delete": ["delete", "remove"],
            "copy": ["copy"],
            "move": ["move", "rename"],
            "open_file": ["open"],
            "save_content": ["save"]
        }
        
        operation = None
        for op, keywords in operation_map.items():
            if any(keyword in input_text for keyword in keywords):
                operation = op
                break
        
        # Default to list if no clear operation
        if not operation:
            operation = "list"
        
        return {
            "operation": operation,
            "path": input_text,
            "content": input_text if "save" in input_text else None
        }

    def run(self, input_text: str, chat_history: List[Union[HumanMessage, AIMessage]] = None) -> str:
        """Run the agent with the given input."""
        try:
            result = self.agent_executor.invoke({
                "input": input_text,
                "chat_history": chat_history or []
            })
            return result["output"]
        except Exception as e:
            return f"Error: {str(e)}"


class FileOperationsTool:
    """Tool for performing file operations on Windows."""
    
    def __init__(self):
        self.drive_map = {
            'd-desk': "D:\\",
            'e-desk': "E:\\",
            'd drive': "D:\\",
            'e drive': "E:\\",
            'c drive': "C:\\"
        }
    
    def _resolve_path(self, path: str) -> str:
        try:
            path = path.lower().strip().replace(' ', '-')
            for shortcut, actual_path in self.drive_map.items():
                if shortcut in path:
                    path = path.replace(shortcut, actual_path)
                    break
            path = os.path.abspath(path.replace("/", "\\"))
            if len(path) == 2 and path[1] == ":":
                path += "\\"
            return path
        except Exception as e:
            print(f"Path resolve error: {e}")
            return path

    def execute_file_operation(self, input_data: Union[str, Dict]) -> str:
        """Execute file operation based on input."""
        try:
            # Handle string inputs that might be JSON
            if isinstance(input_data, str):
                try:
                    input_data = json.loads(input_data.replace("'", '"'))
                except:
                    return self._handle_natural_language(input_data)

            operation = input_data.get("operation", "list").lower()
            path = self._resolve_path(str(input_data.get("path", "")))
            
            
            if operation == "list":
                return self._list_directory(path)
            elif operation == "create_folder":
                return self._create_folder(path)
            elif operation == "create_file":
                return self._create_file(path)
            elif operation == "delete":
                return self._delete_path(path)
            elif operation == "copy":
                dest = self._resolve_path(input_data.get("destination", ""))
                return self._copy_path(path, dest)
            elif operation == "move":
                dest = self._resolve_path(input_data.get("destination", ""))
                return self._move_path(path, dest)
            elif operation == "open_file":
                return self._open_file(path)
            elif operation == "save_content":
                content = input_data.get("content", "")
                return self._save_content(path, content)
            else:
                return f"Unsupported operation: {operation}"
        
        except Exception as e:
            return f"Operation failed: {str(e)}"

    def _handle_natural_language(self, text: str) -> str:
        text = text.lower()
        operation, path, name = "list", "", ""
        
        # Extract operation
        if "create folder" in text:
            operation = "create_folder"
        elif "create file" in text:
            operation = "create_file"
        elif "delete" in text:
            operation = "delete"
        elif "copy" in text:
            operation = "copy"
        elif "move" in text or "rename" in text:
            operation = "move"
        elif "open" in text:
            operation = "open_file"
        elif "save" in text:
            operation = "save_content"
            
        # Extract path and name
        path_match = re.search(r'(in|at|on|to) ([a-z0-9\- ]+)', text)
        if path_match:
            path = self._resolve_path(path_match.group(2))
        
        name_match = re.search(r'(named|called|as) ([a-z0-9\-_. ]+)', text)
        if name_match:
            name = name_match.group(2).strip()
        
        if operation == "create_folder":
            return self._create_folder(os.path.join(path, name))
        elif operation == "create_file":
            return self._create_file(os.path.join(path, name))
        else:
            return self.execute_file_operation({"operation": operation, "path": path})

    def _list_directory(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                return f"Path does not exist: {path}"
                
            items = os.listdir(path)
            return "\n".join([
                f"Contents of {path}:",
                *[f"[DIR]  {item}" if os.path.isdir(os.path.join(path, item)) 
                 else f"[FILE] {item}" for item in items]
            ])
        except Exception as e:
            return f"Listing failed: {str(e)}"

    def _create_folder(self, path: str) -> str:
        """Create a new folder."""
        try:
            os.makedirs(path, exist_ok=True)
            return f"Successfully created folder: {path}"
        except Exception as e:
            return f"Error creating folder: {str(e)}"

    def _create_file(self, path: str) -> str:
        """Create a new empty file."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                pass
            if os.path.exists(path):
                return f"Successfully created file: {path}"
            else:
                return f"Failed to create file: {path}"
            
        except Exception as e:
            return f"Error creating file: {str(e)}"

    def _delete_path(self, path: str) -> str:
        """Delete a file or folder."""
        try:
            if not os.path.exists(path):
                return f"Path does not exist: {path}"
            
            if os.path.isdir(path):
                shutil.rmtree(path)
                return f"Successfully deleted folder: {path}"
            else:
                os.remove(path)
                return f"Successfully deleted file: {path}"
        except Exception as e:
            return f"Error deleting path: {str(e)}"

    def _copy_path(self, src: str, dest: str) -> str:
        """Copy a file or folder."""
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dest)
                return f"Successfully copied folder from {src} to {dest}"
            else:
                shutil.copy2(src, dest)
                return f"Successfully copied file from {src} to {dest}"
        except Exception as e:
            return f"Error copying path: {str(e)}"

    def _move_path(self, src: str, dest: str) -> str:
        """Move or rename a file or folder."""
        try:
            shutil.move(src, dest)
            return f"Successfully moved from {src} to {dest}"
        except Exception as e:
            return f"Error moving path: {str(e)}"

    def _open_file(self, path: str) -> str:
        """Open a file with default application."""
        try:
            os.startfile(path)
            return f"Successfully opened: {path}"
        except Exception as e:
            return f"Error opening file: {str(e)}"

    def _save_content(self, path: str, content: str) -> str:
        """Save content to a file."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully saved content to: {path}"
        except Exception as e:
            return f"Error saving content: {str(e)}"