import os
import subprocess
import psutil
import platform
import tempfile
from typing import Dict, Optional
import time

class TextEditorTool:
    """Tool for writing content to text editors."""
    
    def __init__(self, llm):
        self.system = platform.system()
        self.llm = llm
    
    def _generate_content(self, topic: str) -> str:
        """Generate content about the given topic using LLM."""
        prompt = f"Write a comprehensive, well-structured text about: {topic}\n\n" \
                 "The text should:\n" \
                 "- Be between 300-500 words\n" \
                 "- Have proper paragraphs\n" \
                 "- Be informative and engaging\n" \
                 "- Avoid code examples\n" \
                 "- Use Markdown formatting for headings and lists"
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def write_to_file(self, input_text: str) -> str:
        """Handle writing content with specified editor."""
        try:
            # Default values
            app_name = 'notepad.exe'
            topic = input_text
            
            # Check if specific editor is requested
            if "winword.exe" in input_text.lower():
                app_name = 'winword.exe'
                # Extract topic by removing the editor part
                topic = input_text.lower().replace("in winword.exe", "").replace("winword.exe", "").strip()
            elif "wordpad.exe" in input_text.lower():
                app_name = 'wordpad.exe'
                topic = input_text.lower().replace("in wordpad.exe", "").replace("wordpad.exe", "").strip()
            
            # Further clean the topic if it contains "write about" or similar
            if "write about" in topic.lower():
                topic = topic.lower().split("write about")[1].strip()
            if "write a" in topic.lower():
                topic = topic.lower().split("write a")[1].strip()
            
            content = self._generate_content(topic)
            
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w+', encoding='utf-8') as tmp:
                file_path = tmp.name
                tmp.write(content)
            
            # Open file in specified editor
            if self.system == "Windows":
                subprocess.Popen([app_name, file_path], shell=True)
            elif self.system == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", "TextEdit", file_path])
            elif self.system == "Linux":
                subprocess.Popen(["gedit", file_path])
            
            time.sleep(1)  # Small delay to ensure file is opened
            
            return f"Successfully wrote about '{topic}' and opened in {app_name}"
        
        except Exception as e:
            return f"Error writing to file: {str(e)}"

class AppLauncherTool:
    """Tool for launching applications on the system."""
    
    def __init__(self):
        self.system = platform.system()
    
    def is_app_running(self, app_name: str) -> bool:
        """Check if an application is already running."""
        for proc in psutil.process_iter(['name']):
            if app_name.lower() in proc.info['name'].lower():
                return True
        return False
    
    def launch_app(self, app_name: str) -> str:
        """Launch an application on the system."""
        try:
            if self.is_app_running(app_name):
                return f"{app_name} is already running."
            
            if self.system == "Windows":
                # Windows-specific launch logic
                apps = {
                    "notepad": "notepad.exe",
                    "chrome": "chrome.exe",
                    "calculator": "calc.exe",
                    "word": "winword.exe",
                    "excel": "excel.exe",
                    "powerpoint": "powerpnt.exe",
                    "paint": "mspaint.exe",
                    "cmd": "cmd.exe",
                    "explorer": "explorer.exe",
                }
                
                # Try to find the app in our dictionary
                executable = apps.get(app_name.lower())
                
                if executable:
                    try:
                        # Use full path for system apps
                        system_path = os.path.join(os.environ['WINDIR'], 'System32')
                        full_path = os.path.join(system_path, executable)
                        
                        if os.path.exists(full_path):
                            subprocess.Popen(full_path)
                            return f"Successfully launched {app_name}"
                        
                        # Fallback to direct execution if path not found
                        subprocess.Popen(executable, shell=True)
                        return f"Successfully launched {app_name}"
                    except Exception as e:
                        return f"Failed to launch {app_name}: {str(e)}"
                
                # Try direct execution for other apps
                try:
                    subprocess.Popen(f'start "" "{app_name}"', shell=True)
                    return f"Attempted to launch {app_name}"
                except Exception as e:
                    return f"Failed to launch {app_name}: {str(e)}"
            
            elif self.system == "Darwin":  # macOS
                try:
                    subprocess.Popen(["open", "-a", app_name])
                    return f"Successfully launched {app_name}"
                except Exception as e:
                    return f"Failed to launch {app_name}: {str(e)}"
            
            elif self.system == "Linux":
                try:
                    subprocess.Popen([app_name])
                    return f"Successfully launched {app_name}"
                except Exception as e:
                    return f"Failed to launch {app_name}: {str(e)}"
            
            return f"Could not launch {app_name}. Please specify the exact application name."
            
        except Exception as e:
            return f"Error launching {app_name}: {str(e)}"
        
class CodeGenerationTool:
    """Tool for generating and writing code to editors."""
    
    def __init__(self, llm):
        self.llm = llm
        self.editor_tool = TextEditorTool(llm)
        self.system = platform.system()
    
    def _generate_code(self, language: str, problem: str) -> str:
        """Generate code using LLM."""
        prompt = (
            f"Write a {language} program to {problem}.\n"
            "Requirements:\n"
            "- Include proper comments\n"
            "- Use standard naming conventions\n"
            "- Include necessary imports\n"
            "- Add error handling if applicable\n"
            "- Ensure code is properly indented\n"
            "- Include example usage if possible\n\n"
            "Output only the raw code without markdown formatting or additional explanations."
        )
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def generate_and_write_code(self, input_text: str) -> str:
        """Handle code generation and writing to editor."""
        try:
            # Parse input (language, problem, editor)
            parts = input_text.split(";")
            language = parts[0].strip()
            problem = parts[1].strip()
            editor = parts[2].strip() if len(parts) > 2 else "notepad.exe"
            
            # Generate code
            code = self._generate_code(language, problem)
            
            # Create temp file with proper extension
            ext_map = {
                "python": ".py",
                "java": ".java",
                "c++": ".cpp",
                "javascript": ".js"
            }
            ext = ext_map.get(language.lower(), ".txt")
            
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False, mode='w+', encoding='utf-8') as tmp:
                file_path = tmp.name
                tmp.write(code)
            
            # Open in specified editor
            if self.system == "Windows":
                subprocess.Popen([editor, file_path], shell=True)
            elif self.system == "Darwin":
                subprocess.Popen(["open", "-a", "TextEdit", file_path])
            elif self.system == "Linux":
                subprocess.Popen(["gedit", file_path])
            
            time.sleep(1)  # Ensure file opens
            return f"Successfully generated {language} code for {problem} and opened in {editor}"
        
        except Exception as e:
            return f"Code generation error: {str(e)}"        