import subprocess
import time
import re
import platform
import pyautogui
import pygetwindow as gw
import os
from typing import List, Union
from langchain.agents import Tool
from langchain_core.messages import AIMessage, HumanMessage

class CalculationAgent:
    def __init__(self, llm):
        self.llm = llm
        self.tools = self._setup_tools()
    
    def _setup_tools(self) -> List[Tool]:
        return [
            Tool(
                name="calculator",
                func=self._perform_calculation,
                description="Performs calculations and shows results in calculator. "
                          "Format: 'calculate [expression]' or '3+5+2'"
            )
        ]

    def _safe_eval(self, expression: str) -> float:
        """Securely evaluate mathematical expressions"""
        sanitized = re.sub(r'[^\d\+\-\*\/\(\)\.]', '', expression)
        if not sanitized:
            raise ValueError("No valid expression found")
        return eval(sanitized)

    def _perform_calculation(self, input_text: str) -> str:
        """Handle calculations with residual value prevention"""
        try:
            # Extract and validate expression
            original_expression = self._extract_expression(input_text)
            if not original_expression:
                return "Please provide a valid mathematical expression"

            # Calculate actual result
            result = self._safe_eval(original_expression)
            
            # Create residual-neutral expression
            neutral_expression = f"{original_expression}+0"
            
            # Refresh calculator instance
            self._close_calculator()
            self._launch_calculator()
            time.sleep(1.5)
            self._focus_calculator()
            
            # Input neutralized expression
            pyautogui.write(f'{neutral_expression}=')
            time.sleep(0.3)
            pyautogui.press('enter')
            
            return f"Result: {original_expression} = {result}"

        except Exception as e:
            return f"Calculation error: {str(e)}"

    def _extract_expression(self, text: str) -> str:
        """Improved expression extraction"""
        # Remove command words and previous residuals
        clean_text = re.sub(r'\b(calculate|calc|calculator|\.exe|open)\b', '', text, flags=re.IGNORECASE)
        match = re.search(r'((?:[\d\(\)][\+\-\*\/\(\)\d\. ]+))', clean_text)
        return match.group(1).strip() if match else ''

    def _launch_calculator(self):
        """Platform-specific calculator launch"""
        system = platform.system()
        if system == "Windows":
            subprocess.Popen("calc.exe")
        elif system == "Darwin":
            subprocess.Popen(["/System/Applications/Calculator.app/Contents/MacOS/Calculator"])
        elif system == "Linux":
            subprocess.Popen(["gnome-calculator"])

    def _close_calculator(self):
        """Close existing calculator instances"""
        system = platform.system()
        try:
            if system == "Windows":
                os.system("taskkill /f /im calculator.exe")
            elif system == "Darwin":
                os.system("pkill Calculator")
            elif system == "Linux":
                os.system("pkill gnome-calculator")
        except:
            pass

    def _focus_calculator(self):
        """Bring calculator to foreground"""
        system = platform.system()
        if system == "Windows":
            windows = gw.getWindowsWithTitle("Calculator")
            if windows:
                windows[0].activate()
        elif system == "Darwin":
            applescript = '''
            tell application "Calculator" to activate
            '''
            subprocess.run(["osascript", "-e", applescript])
        elif system == "Linux":
            subprocess.Popen(["wmctrl", "-a", "Calculator"])

    def run(self, input_text: str, chat_history: List[Union[HumanMessage, AIMessage]] = None) -> str:
        try:
            return self._perform_calculation(input_text)
        except Exception as e:
            return f"Error: {str(e)}"