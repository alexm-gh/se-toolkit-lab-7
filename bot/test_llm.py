#!/usr/bin/env python3
"""Test script to debug LLM tool calling with multiple iterations."""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.llm_client import llm_client
from services.lms_client import lms_client


async def execute_tool(name: str, args: dict):
    """Execute a tool by calling the appropriate LMS client method."""
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


async def test_llm_with_tools():
    """Test LLM tool calling with a multi-step query."""
    print("=" * 60)
    print("Testing LLM tool calling - Multi-step query")
    print("=" * 60)

    # Test message
    user_message = "which lab has the lowest pass rate?"
    print(f"\nUser message: {user_message}\n")

    messages = [{"role": "user", "content": user_message}]
    tools = llm_client.get_tool_definitions()

    print(f"Tools defined: {len(tools)}")
    print(f"Tool names: {[t['function']['name'] for t in tools]}\n")

    max_iterations = 5
    
    for iteration in range(max_iterations):
        print(f"\n{'='*60}")
        print(f"ITERATION {iteration + 1}")
        print(f"{'='*60}")
        print(f"Messages in conversation: {len(messages)}")
        
        # Call LLM
        print("\n>>> Calling LLM...")
        response = await llm_client.chat(
            messages=messages,
            tools=tools,
            system_prompt=None,
        )
        
        choice = response.get("choices", [{}])[0]
        assistant_message = choice.get("message", {})
        
        content = assistant_message.get("content")
        tool_calls = assistant_message.get("tool_calls", [])
        
        print(f"\nAssistant response:")
        print(f"  Content: {content[:200] if content else '(none)'}...")
        print(f"  Tool calls: {len(tool_calls)}")
        
        # Check if we have a final answer
        if not tool_calls:
            if content:
                print(f"\n*** FINAL ANSWER RECEIVED ***")
                print(f"\n{content}")
                return
            else:
                print("\n*** ERROR: No content and no tool calls ***")
                return
        
        # Show tool calls
        print(f"\nTool calls:")
        for i, tc in enumerate(tool_calls):
            func = tc.get("function", {})
            print(f"  {i+1}. {func.get('name', 'N/A')}({func.get('arguments', '{}')})")
        
        # Add assistant message to conversation
        messages.append(assistant_message)
        
        # Execute tool calls
        print(f"\n>>> Executing {len(tool_calls)} tool(s)...")
        for tc in tool_calls:
            func = tc.get("function", {})
            tool_name = func.get("name", "")
            try:
                args = json.loads(func.get("arguments", "{}"))
            except json.JSONDecodeError:
                args = {}
            
            result = await execute_tool(tool_name, args)
            result_str = json.dumps(result, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result)
            
            print(f"  {tool_name}: {len(result_str)} bytes")
            
            # Add tool result to conversation
            tool_message = {
                "role": "tool",
                "tool_call_id": tc.get("id", ""),
                "content": result_str,
            }
            messages.append(tool_message)
        
        print(f"\n>>> Added {len(tool_calls)} tool results to conversation")
    
    print(f"\n*** MAX ITERATIONS REACHED ({max_iterations}) ***")
    print(f"Final conversation has {len(messages)} messages")


if __name__ == "__main__":
    asyncio.run(test_llm_with_tools())
