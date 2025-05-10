# Clickless: Voice-Driven System Control 🚀

**Control everything with just your words**  
_An AI-powered interface for natural language system operations_

![Demo](assets/demo.gif) _Add demo GIF later_

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Security](#security)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Features ✨

| Category        | Capabilities                                          |
| --------------- | ----------------------------------------------------- |
| **App Control** | Launch Notepad, Chrome, Office apps via voice/text    |
| **AI Writing**  | Generate documents/essays → Auto-open in Word/Notepad |
| **Code Gen**    | Create Python/Java/C++ code → Launch in IDEs          |
| **File Ops**    | Create folders + list contents (D/E drives only)      |
| **Smart Calc**  | Solve math + control physical calculator app          |
| **System Ctrl** | Adjust brightness/volume + toggle Bluetooth (Windows) |

---

## Architecture 🧠

````mermaid
graph LR
    A[User Input] --> B(Streamlit UI)
    B --> C{Input Router}
    C -->|App Launch| D[AppLauncherAgent]
    C -->|Writing| E[WritingAgent]
    C -->|Code| F[CodeGenerationAgent]
    C -->|Files| G[FileHandlingAgent]
    C -->|Math| H[CalculationAgent]
    C -->|System| I[SystemControlAgent]


```Key Components:

Agents: LangChain ReAct agents with tool-specific logic

Tools: Secure system operations via psutil, pyautogui, pycaw

UI: Streamlit chat interface with CSS animations

LLM: GPT-3.5-turbo through custom API endpoint
````

Installation ⚙️
Prerequisites:

Python 3.8+

Windows 10/11 (macOS/Linux support in progress)

API key in .env

Steps:

git clone https://github.com/yourusername/clickless.git
cd clickless

python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # macOS/Linux

pip install -r requirements.txt
streamlit run app.py

# App Control

"Open Chrome and Excel"

# Document Writing

"Write 500-word essay about AI ethics in Word"

# Code Generation

"Create Python Fibonacci sequence code in Notepad"

# File Operations

"Create 'Project' folder in D drive"

# Calculations

"Calculate (25\*4)+(18/3)"

# System Control

"Set brightness to 70% and mute volume"

Acknowledgments 🙏
LangChain team for agent framework

Streamlit for UI components

OpenAI for GPT-3.5 integration

Contact: [kaviya29official.email@domain.com] | Project Wiki
