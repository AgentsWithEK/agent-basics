from agent import Agent
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path
from pydantic import BaseModel
from tools.calculator_tool.calculator_api import calculate
from tools.weather_tool.weather_api import get_current_weather
from typing import Dict, Any
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agent Server", version="1.0.0")


# Load tool schemas from JSON files
tools_dir = Path(__file__).parent / "tools"

with open(tools_dir / "weather_tool" / "weather_api.json") as f:
    weather_schema = json.load(f)

with open(tools_dir / "calculator_tool" / "calculator_api.json") as f:
    calculator_schema = json.load(f)


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
    ],
    functions={
        "get_current_weather": get_current_weather,
        "calculate": calculate,
    },
)


class InvocationRequest(BaseModel):
    input: Dict[str, Any]


class InvocationResponse(BaseModel):
    output: Dict[str, Any]


@app.post("/invocations")
async def invoke_agent(request: InvocationRequest):
    try:
        logger.info(f"Received invocation request: {request.input}")

        user_message = request.input.get("prompt", "")
        if not user_message:
            logger.warning("No prompt found in input")
            raise HTTPException(
                status_code=400,
                detail="No prompt found in input. Please provide a 'prompt' key in the input.",
            )

        logger.info(f"Processing prompt: {user_message}")

        async def generate():
            async for data in agent.invoke_stream(user_message):
                chunk = (
                    json.dumps(
                        {
                            "output": {
                                "message": data,
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        }
                    )
                    + "\n"
                )
                yield chunk

        return StreamingResponse(generate(), media_type="application/x-ndjson")

        # Non-streaming version (commented out)
        # result = await agent.invoke(user_message)
        # response = {
        #     "message": result,
        #     "timestamp": datetime.utcnow().isoformat(),
        # }
        # logger.info(f"Successfully processed request, response: {response}")
        # return InvocationResponse(output=response)

    except Exception as e:
        logger.error(f"Agent processing failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Agent processing failed: {str(e)}"
        )


@app.get("/ping")
async def ping():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
