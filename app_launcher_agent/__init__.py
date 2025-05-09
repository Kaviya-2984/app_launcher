"""
AI App Launcher Agent Module

This module provides an AI agent that can open applications on your computer using natural language commands.
"""

from .agent import AppLauncherAgent
from .writer_agent import WritingAgent
from .file_agent import FileHandlingAgent
from .tools import AppLauncherTool
from .utils import format_chat_history

__all__ = [
    "AppLauncherAgent",
    "WritingAgent",
    "FileHandlingAgent",
    "CodeGenerationAgent",
    "AppLauncherTool",
    "TextEditorTool",
    "CodeGenerationTool",
    "format_chat_history"
]
__version__ = "0.3.0"