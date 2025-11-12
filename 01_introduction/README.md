# Agent Basics - Introduction

In this module we create a lightweight, AI agent framework built with Python and LiteLLM. This framework enables building conversational AI agents with tool-calling capabilities, parallel execution, and streaming support.

## Features

- **Multi-Tool Support**: Easily integrate multiple tools (weather, calculator, research, etc.)
- **Parallel Tool Execution**: Tools execute concurrently using asyncio for optimal performance
- **Streaming Support**: Real-time response streaming with `invoke_stream()`
- **Async & Sync Tools**: Automatically handles both async and synchronous tool functions
- **Conversation Memory**: Maintains conversation history for context-aware responses
- **Performance Tracking**: Built-in timing metrics for monitoring agent performance

## Installation

```bash
# Install dependencies using uv
uv sync
```

## Quick Start

### Running the Interactive CLI

```bash
# With streaming (default)
python interactive_cli.py

# Without streaming
python interactive_cli.py --no-stream
```

## Example Interactions

### Calculator Tool

```bash
You: Calculate 25 + 17
Assistant: The result of 25 + 17 is 42.

Tool 1: calculate(operation="add", num1="25", num2="17")
Response 1: {
  "operation": "add",
  "num1": 25.0,
  "num2": 17.0,
  "result": 42.0
}
```

### Weather Tool

```bash
You: What's the weather in Tokyo?
Assistant: The current temperature in Tokyo is 10�C.

Tool 1: get_current_weather(location="Tokyo", unit="celsius")
Response 1: {
  "location": "Tokyo",
  "temperature": "10",
  "unit": "celsius"
}
```

### Multiple Tools in Parallel

```bash
You: What's 100 + 50 and also the weather in San Francisco?
Assistant: The sum of 100 and 50 is 150. The weather in San Francisco
is currently 72�F.

Tool 1: calculate(operation="add", num1="100", num2="50")
Tool 2: get_current_weather(location="San Francisco")

# Both execute simultaneously!
```

## Performance Metrics

The agent automatically tracks and displays:

- **Total Time**: End-to-end execution time
- Timing information is displayed after each response

```bash
============================================================
Total Time: 5.23s
============================================================
```
