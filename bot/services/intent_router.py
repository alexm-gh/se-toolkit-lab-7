"""Intent router for natural language queries."""

import json
import logging
import sys

from services.llm_client import llm_client
from services.lms_client import lms_client

logger = logging.getLogger(__name__)


# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for an LMS (Learning Management System).
You have access to tools that fetch data about labs, students, scores, and analytics.

RULES FOR TOOL USE:
1. When you need data, call the appropriate tool
2. Wait for the tool result to be returned to you
3. Once you have ALL the data you need, provide a FINAL ANSWER
4. Your final answer must be based ONLY on the tool results, not assumptions
5. After seeing tool results, you MUST provide a final answer - do not call more tools unnecessarily

AVAILABLE TOOLS:
- get_items: Get list of all labs and tasks. Returns array of objects with 'title', 'type', and 'id' fields. Use this FIRST to discover available labs.
- get_learners: Get list of enrolled students and their groups.
- get_scores: Get score distribution (4 buckets) for a specific lab. Requires 'lab' parameter.
- get_pass_rates: Get per-task average pass rates and attempt counts for a lab. Requires 'lab' parameter.
- get_timeline: Get submissions per day for a specific lab. Requires 'lab' parameter.
- get_groups: Get per-group scores and student counts for a lab. Requires 'lab' parameter.
- get_top_learners: Get top N learners by score for a specific lab. Requires 'lab' and optional 'limit' parameters.
- get_completion_rate: Get completion rate percentage for a specific lab. Requires 'lab' parameter.
- trigger_sync: Trigger ETL sync to refresh data from autochecker.

EXAMPLE WORKFLOW for "which lab has the lowest pass rate?":
1. Call get_items to get all labs
2. For each lab, call get_pass_rates(lab="lab-XX")
3. Compare the pass rates from all results
4. Provide final answer: "Lab XX has the lowest pass rate at YY%"

If the user's message is unclear or ambiguous, ask for clarification.
If the user greets you, respond warmly and mention what you can help with.
ALWAYS provide a complete final answer after receiving tool results."""


async def route_message(user_message: str) -> str:
    """Route a user message through the LLM to get a response."""
    logger.info(f"Routing message: {user_message}")

    messages = [{"role": "user", "content": user_message}]
    tools = llm_client.get_tool_definitions()

    max_iterations = 5  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        logger.debug(f"Iteration {iteration}: Calling LLM")

        # Call LLM
        response = await llm_client.chat(
            messages=messages,
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
        )

        # Get the assistant's response
        assistant_message = response.get("choices", [{}])[0].get("message", {})

        # Debug: log full assistant message
        logger.debug(f"Assistant message: {assistant_message}")

        # Check if LLM wants to call tools
        tool_calls = assistant_message.get("tool_calls", [])

        # Also check for content - if LLM provides content without tool calls, that's the final answer
        content = assistant_message.get("content")

        if not tool_calls:
            # No tool calls - LLM has a final answer
            if content:
                logger.info(f"LLM final answer: {content[:200]}...")
                return content
            else:
                logger.warning("LLM returned no content and no tool calls")
                return "I'm not sure how to help with that."

        logger.debug(f"LLM called {len(tool_calls)} tool(s)")

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
                logger.warning(f"Failed to parse tool arguments: {tool_args_str}")
                tool_args = {}

            # Debug output
            print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)
            logger.debug(f"Tool call: {tool_name}({tool_args})")

            # Execute the tool
            result = await execute_tool(tool_name, tool_args)
            result_preview = str(result)[:200] if result else "None"
            print(f"[tool] Result: {result_preview}...", file=sys.stderr)
            logger.debug(f"Tool result: {result_preview}...")

            # Add tool result to conversation as a new message
            tool_message = {
                "role": "tool",
                "tool_call_id": tool_call.get("id", ""),
                "content": json.dumps(result, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result),
            }
            logger.debug(f"Tool message: {tool_message}")
            messages.append(tool_message)

        print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)
        logger.debug(f"Feeding {len(tool_calls)} tool result(s) back to LLM")
        logger.debug(f"Conversation now has {len(messages)} messages")

    # If we reach here, max iterations exceeded
    logger.warning("Max iterations exceeded")
    return "I'm having trouble processing your request. Please try rephrasing."


async def execute_tool(name: str, args: dict) -> dict | list:
    """Execute a tool by calling the appropriate LMS client method."""
    logger.info(f"Executing tool: {name}({args})")
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
        logger.error(f"Tool execution error: {e}")
        return {"error": str(e)}
