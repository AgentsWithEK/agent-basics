import argparse
import json
from pathlib import Path
from agent import Agent
from tools.calculator_tool.calculator_api import calculate
from tools.research_agent_tool.research_agent_api import research_topic
from tools.weather_tool.weather_api import get_current_weather

# Load tool schemas from JSON files
tools_dir = Path(__file__).parent / "tools"

with open(tools_dir / "weather_tool" / "weather_api.json") as f:
    weather_schema = json.load(f)

with open(tools_dir / "calculator_tool" / "calculator_api.json") as f:
    calculator_schema = json.load(f)

with open(tools_dir / "research_agent_tool" / "research_agent_api.json") as f:
    research_schema = json.load(f)

agent = Agent(
    system_prompt="""
You are a helpful AI assistant with access to multiple tools and capabilities.

## Guidelines
- Use the appropriate tool based on the user's question
- Be concise and helpful in your responses
- If you're unsure which tool to use, you can ask the user for clarification
""",
    schemas=[
        {"type": "function", "function": weather_schema},
        {"type": "function", "function": calculator_schema},
        {"type": "function", "function": research_schema},
    ],
    functions={
        "get_current_weather": get_current_weather,
        "calculate": calculate,
        "research_topic": research_topic,
    },
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Interactive AI Assistant CLI with Multiple Tools"
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        default=True,
        help="Enable streaming mode (default: True)",
    )
    parser.add_argument(
        "--no-stream",
        action="store_false",
        dest="stream",
        help="Disable streaming mode",
    )
    args = parser.parse_args()
    stream = args.stream

    print("AI Assistant - Type 'quit' or 'exit' to end the conversation")
    print(f"Mode: {'Streaming' if stream else 'Non-streaming'}\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "bye"]:
                print("Goodbye!")
                break

            print("Assistant: ", end="", flush=True)

            if stream:
                for content in agent.invoke_stream(user_input):
                    if content:
                        print(content, end="", flush=True)

            else:
                response_content = agent.invoke(user_input)
                if response_content:
                    print(response_content, end="")
            print("\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
