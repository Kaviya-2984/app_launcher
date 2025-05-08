import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage
from app_launcher_agent.agent import AppLauncherAgent
from app_launcher_agent.tools import AppLauncherTool

@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(content="Mocked AI response")
    return llm

@pytest.fixture
def app_launcher_agent(mock_llm):
    return AppLauncherAgent(mock_llm)

def test_app_launcher_agent_initialization(app_launcher_agent, mock_llm):
    """Test that the agent initializes correctly with tools."""
    assert app_launcher_agent.llm == mock_llm
    assert len(app_launcher_agent.tools) == 1
    assert app_launcher_agent.tools[0].name == "app_launcher"

def test_app_launcher_agent_run_success(app_launcher_agent, mock_llm):
    """Test running the agent with a simple command."""
    result = app_launcher_agent.run("Open Chrome")
    assert result == "Mocked AI response"
    mock_llm.invoke.assert_called_once()

def test_app_launcher_agent_with_chat_history(app_launcher_agent, mock_llm):
    """Test running the agent with chat history."""
    chat_history = [
        HumanMessage(content="Open Chrome"),
        AIMessage(content="Successfully launched Chrome")
    ]
    result = app_launcher_agent.run("Open it again", chat_history)
    assert result == "Mocked AI response"
    assert mock_llm.invoke.call_count == 1

def test_app_launcher_tool_windows(mocker):
    """Test the AppLauncherTool on Windows."""
    mocker.patch('platform.system', return_value="Windows")
    mocker.patch('subprocess.Popen')
    mocker.patch('psutil.process_iter', return_value=[])
    
    tool = AppLauncherTool()
    result = tool.launch_app("notepad")
    assert "Successfully launched notepad" in result

def test_app_launcher_tool_mac(mocker):
    """Test the AppLauncherTool on macOS."""
    mocker.patch('platform.system', return_value="Darwin")
    mocker.patch('subprocess.Popen')
    mocker.patch('psutil.process_iter', return_value=[])
    
    tool = AppLauncherTool()
    result = tool.launch_app("Safari")
    assert "Successfully launched Safari" in result

def test_app_launcher_tool_linux(mocker):
    """Test the AppLauncherTool on Linux."""
    mocker.patch('platform.system', return_value="Linux")
    mocker.patch('subprocess.Popen')
    mocker.patch('psutil.process_iter', return_value=[])
    
    tool = AppLauncherTool()
    result = tool.launch_app("firefox")
    assert "Successfully launched firefox" in result

def test_app_launcher_tool_app_already_running(mocker):
    """Test the tool when app is already running."""
    mocker.patch('platform.system', return_value="Windows")
    mock_process = MagicMock()
    mock_process.info = {'name': 'notepad.exe'}
    mocker.patch('psutil.process_iter', return_value=[mock_process])
    
    tool = AppLauncherTool()
    result = tool.launch_app("notepad")
    assert "already running" in result

def test_app_launcher_tool_error_handling(mocker):
    """Test the tool's error handling."""
    mocker.patch('platform.system', return_value="Windows")
    mocker.patch('subprocess.Popen', side_effect=Exception("Test error"))
    mocker.patch('psutil.process_iter', return_value=[])
    
    tool = AppLauncherTool()
    result = tool.launch_app("unknown_app")
    assert "Error launching" in result
    assert "Test error" in result

def test_format_chat_history():
    """Test the format_chat_history utility function."""
    from app_launcher_agent.utils import format_chat_history
    from langchain_core.messages import HumanMessage, AIMessage
    
    chat_history = [
        HumanMessage(content="Hello"),
        AIMessage(content="Hi there!"),
        HumanMessage(content="How are you?"),
    ]
    
    formatted = format_chat_history(chat_history)
    assert len(formatted) == 3
    assert formatted[0]["role"] == "user"
    assert formatted[0]["content"] == "Hello"
    assert formatted[1]["role"] == "assistant"
    assert formatted[1]["content"] == "Hi there!"