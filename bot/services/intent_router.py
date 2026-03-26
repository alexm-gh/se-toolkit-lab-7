"""Intent router for natural language queries."""

import json
import sys

from services.llm_client import llm_client
from services.lms_client import lms_client


# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for an LMS (Learning Management System).
You have access to tools that fetch data about labs, students, scores, and analytics.

When the user asks a question:
1. First understand what they want to know
2. Call the appropriate tool(s) to get the data
3. Analyze the results carefully
4. Provide a clear, helpful answer based on the data

IMPORTANT:
- Always call tools to get real data before answering
- Include specific numbers, names, and percentages from the tool results in your answer
- For "what labs" questions: call get_items and list the actual lab titles
- For "scores" questions: call get_pass_rates with the lab name and show percentages
- For "lowest/highest" questions: compare data from multiple labs
- For "how many" questions: count and return the actual number

Available tools:
- get_items: Get list of all labs and tasks. Returns array of objects with 'title' and 'type' fields.
- get_learners: Get list of enrolled students and their groups.
- get_scores: Get score distribution (4 buckets) for a specific lab.
- get_pass_rates: Get per-task average pass rates and attempt counts for a lab.
- get_timeline: Get submissions per day for a specific lab.
- get_groups: Get per-group scores and student counts for a lab.
- get_top_learners: Get top N learners by score for a specific lab.
- get_completion_rate: Get completion rate percentage for a specific lab.
- trigger_sync: Trigger ETL sync to refresh data from autochecker.

If the user's message is unclear or ambiguous, ask for clarification.
If the user greets you, respond warmly and mention what you can help with.
Always base your answers on the data returned by tools, not assumptions."""


async def route_message(user_message: str) -> str:
    """Route a user message through the LLM to get a response."""
    messages = [{"role": "user", "content": user_message}]
    tools = llm_client.get_tool_definitions()

    max_iterations = 5  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Call LLM
        response = await llm_client.chat(
            messages=messages,
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
        )

        # Get the assistant's response
        assistant_message = response.get("choices", [{}])[0].get("message", {})

        # Check if LLM wants to call tools
        tool_calls = assistant_message.get("tool_calls", [])

        if not tool_calls:
            # No tool calls - LLM has a final answer
            content = assistant_message.get("content", "I'm not sure how to help with that.")
            return content

        # Add assistant message with tool calls to conversation
        messages.append(assistant_message)

        # Execute tool calls
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            tool_name = function.get("name", "")
            tool_args_str = function.get("arguments", "{}")

            try:
                tool_args = json.loads(tool_args_str) if tool_args_str else {}
            except json.JSONDecodeError:
                tool_args = {}

            # Debug output
            print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)

            # Execute the tool
            result = await execute_tool(tool_name, tool_args)
            print(f"[tool] Result: {str(result)[:100]}...", file=sys.stderr)

            # Add tool result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id", ""),
                "content": json.dumps(result) if not isinstance(result, str) else result,
            })

        print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)

    # If we reach here, max iterations exceeded
    return "I'm having trouble processing your request. Please try rephrasing."


async def execute_tool(name: str, args: dict) -> dict | list:
    """Execute a tool by calling the appropriate LMS client method."""
    try:
        if name == "get_items":
            return await lms_client.get("/items/")
        elif name == "get_learners":
            return await lms_client.get("/learners/")
        elif name == "get_scores":
            lab = args.get("lab", "")
            return await lms_client.get("/analytics/scores", params={"lab": lab})
        elif name == "get_pass_rates":
            lab = args.get("lab", "")
            return await lms_client.get("/analytics/pass-rates", params={"lab": lab})
        elif name == "get_timeline":
            lab = args.get("lab", "")
            return await lms_client.get("/analytics/timeline", params={"lab": lab})
        elif name == "get_groups":
            lab = args.get("lab", "")
            return await lms_client.get("/analytics/groups", params={"lab": lab})
        elif name == "get_top_learners":
            lab = args.get("lab", "")
            limit = args.get("limit", 5)
            return await lms_client.get("/analytics/top-learners", params={"lab": lab, "limit": limit})
        elif name == "get_completion_rate":
            lab = args.get("lab", "")
            return await lms_client.get("/analytics/completion-rate", params={"lab": lab})
        elif name == "trigger_sync":
            return await lms_client.post("/pipeline/sync", data={})
        else:
            return {"error": f"Unknown tool: {name}"}
    except Exception as e:
        return {"error": str(e)}
