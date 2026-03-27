#!/usr/bin/env python3
"""Test script to debug LLM tool calling."""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.llm_client import llm_client
from services.lms_client import lms_client


async def test_llm_with_tools():
    """Test LLM tool calling with a simple query."""
    print("=" * 60)
    print("Testing LLM tool calling")
    print("=" * 60)

    # Test message
    user_message = "what labs are available?"
    print(f"\nUser message: {user_message}\n")

    messages = [{"role": "user", "content": user_message}]
    tools = llm_client.get_tool_definitions()

    print(f"Tools defined: {len(tools)}")
    print(f"Tool names: {[t['function']['name'] for t in tools]}\n")

    # First call
    print(">>> Calling LLM first time...")
    response = await llm_client.chat(
        messages=messages,
        tools=tools,
        system_prompt=None,  # No system prompt for debugging
    )

    print(f"Response status: OK")
    
    choice = response.get("choices", [{}])[0]
    assistant_message = choice.get("message", {})
    
    print(f"\nAssistant message keys: {assistant_message.keys()}")
    print(f"Content: {assistant_message.get('content', 'None')[:200]}")
    
    tool_calls = assistant_message.get("tool_calls", [])
    print(f"\nTool calls: {len(tool_calls)}")
    
    for i, tc in enumerate(tool_calls):
        print(f"\n  Tool call {i+1}:")
        print(f"    ID: {tc.get('id', 'N/A')}")
        func = tc.get("function", {})
        print(f"    Name: {func.get('name', 'N/A')}")
        print(f"    Arguments: {func.get('arguments', 'N/A')}")
        
        # Execute the tool
        tool_name = func.get("name", "")
        try:
            args = json.loads(func.get("arguments", "{}"))
        except json.JSONDecodeError:
            args = {}
        
        print(f"    Parsed args: {args}")
        
        # Execute
        if tool_name == "get_items":
            result = await lms_client.get("/items/")
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        print(f"    Result type: {type(result)}")
        print(f"    Result preview: {str(result)[:200]}...")
        
        # Build tool result message
        tool_message = {
            "role": "tool",
            "tool_call_id": tc.get("id", ""),
            "content": json.dumps(result, ensure_ascii=False),
        }
        print(f"\n  Tool message to send back:")
        print(f"    role: {tool_message['role']}")
        print(f"    tool_call_id: {tool_message['tool_call_id']}")
        print(f"    content length: {len(tool_message['content'])} chars")
        
        messages.append(assistant_message)
        messages.append(tool_message)

    # Second call
    if tool_calls:
        print("\n\n>>> Calling LLM second time with tool results...")
        print(f"Messages in conversation: {len(messages)}")
        
        response2 = await llm_client.chat(
            messages=messages,
            tools=tools,
            system_prompt=None,
        )
        
        choice2 = response2.get("choices", [{}])[0]
        assistant_message2 = choice2.get("message", {})
        
        print(f"\nFinal answer:")
        print(f"  Content: {assistant_message2.get('content', 'None')[:500]}")
        
        tool_calls2 = assistant_message2.get("tool_calls", [])
        print(f"\n  More tool calls: {len(tool_calls2)}")


if __name__ == "__main__":
    asyncio.run(test_llm_with_tools())
