from typing import List, Union
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain import hub
from langchain_core.messages import AIMessage, HumanMessage
from .tools import SystemOperationsTool

class SystemControlAgent:
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
                name="windows_system_control",
                func=self._handle_windows_operation,
                description="Windows system controls: brightness, volume, Bluetooth. "
                          "Commands: 'increase brightness', 'lower volume', 'enable bluetooth'"
            )
        ]

    def _handle_windows_operation(self, input_text: str) -> str:
        input_text = input_text.lower()
        
        if "brightness" in input_text:
            direction = "increase" if "increase" in input_text else "decrease"
            return SystemOperationsTool().adjust_brightness(direction)
        
        elif "volume" in input_text:
            direction = "increase" if any(kw in input_text for kw in ["increase", "up"]) else "decrease"
            return SystemOperationsTool().adjust_volume(direction)
        
        elif "bluetooth" in input_text:
            state = "enable" if any(kw in input_text for kw in ["enable", "turn on"]) else "disable"
            return SystemOperationsTool().toggle_bluetooth(state)
        
        return "Unsupported system operation"

    def _setup_agent(self):
        prompt = hub.pull("hwchase17/react-chat")
        return create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

    def run(self, input_text: str, chat_history: List[Union[HumanMessage, AIMessage]] = None) -> str:
        try:
            result = self.agent_executor.invoke({
                "input": input_text,
                "chat_history": chat_history or []
            })
            return result["output"]
        except Exception as e:
            return f"System error: {str(e)}"