"""
AI App Launcher Agent Module

This module provides an AI agent that can open applications and control system settings using natural language commands.
"""

from .agent import AppLauncherAgent
from .writer_agent import WritingAgent
from .file_agent import FileHandlingAgent
from .code_agent import CodeGenerationAgent
from .file_agent import FileOperationsTool  
from .calculation_agent import CalculationAgent
from .system_agent import SystemControlAgent  # New import
from .tools import AppLauncherTool, TextEditorTool, CodeGenerationTool, SystemOperationsTool  # Updated import
from .utils import format_chat_history

__all__ = [
    "AppLauncherAgent",
    "WritingAgent",
    "FileHandlingAgent",
    "CodeGenerationAgent",
    "CalculationAgent",
    "SystemControlAgent",  # Added
    "AppLauncherTool",
    "TextEditorTool", 
    "CodeGenerationTool",
    "SystemOperationsTool",  # Added
    "format_chat_history"
]
__version__ = "0.4.0"  # Version bump