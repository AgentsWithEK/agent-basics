import json
import sys
from pathlib import Path

# Add parent directory to path to import Agent
sys.path.append(str(Path(__file__).parent.parent.parent))
from agent import Agent


def research_topic(query: str, context: str = None) -> str:
    try:
        # Create a research-focused agent
        research_agent = Agent(
            system_prompt="""
You are a research assistant specialized in providing detailed, well-structured information on various topics.

## Your capabilities:
- Answer factual questions with accurate information
- Provide structured analysis and breakdowns
- Offer multiple perspectives on topics
- Synthesize information clearly and concisely

## Your style:
- Be direct and informative
- Use bullet points for clarity when appropriate
- Cite reasoning when making claims
- Admit uncertainty when you don't have complete information
""",
            schemas=[],  # Research agent doesn't need tools
            functions={},
        )

        # Build the query
        if context:
            full_query = f"Context: {context}\n\nQuestion: {query}"
        else:
            full_query = query

        # Get response from the research agent
        response = research_agent.invoke(full_query)
        research_result = response.choices[0].message.content

        return json.dumps(
            {
                "query": query,
                "context": context,
                "findings": research_result,
                "status": "success",
            }
        )

    except Exception as e:
        return json.dumps({"query": query, "error": str(e), "status": "failed"})
