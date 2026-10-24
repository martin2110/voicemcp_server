#!/usr/bin/env python3
"""
Test the MCP server protocol directly without an LLM client.
Sends JSON-RPC messages to the server and displays responses.
"""
import asyncio
import json
import sys
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))


async def test_mcp_server():
    """Test MCP server by simulating client requests"""

    print("=== Testing MCP Server Protocol ===\n")

    # Import server
    from elise_voice_server.server import app, initialize_tts_engine

    # Initialize TTS engine
    print("1. Initializing TTS engine...")
    await initialize_tts_engine()
    print("   ✓ TTS engine initialized\n")

    # Test list_tools
    print("2. Testing list_tools()...")
    tools = await app._tool_manager.list_tools()
    print(f"   ✓ Found {len(tools)} tools:")
    for tool in tools:
        print(f"      - {tool.name}: {tool.description}")
    print()

    # Test generate_speech
    print("3. Testing generate_speech tool...")
    test_text = "Hello! This is a test of the text to speech system."
    print(f"   Input text: '{test_text}'")

    result = await app._tool_manager.call_tool(
        "generate_speech",
        {"text": test_text, "filename": "test_output", "play": False}
    )

    print(f"   ✓ Result: {result[0].text}")
    print()

    # Test get_voice_info
    print("4. Testing get_voice_info tool...")
    result = await app._tool_manager.call_tool("get_voice_info", {})
    print("   ✓ Voice info retrieved:")
    # Print first few lines only
    lines = result[0].text.split('\n')[:5]
    for line in lines:
        print(f"      {line}")
    print("      ...")
    print()

    # Test list_sample_texts
    print("5. Testing list_sample_texts tool...")
    result = await app._tool_manager.call_tool("list_sample_texts", {"limit": 3})
    print("   ✓ Sample texts retrieved:")
    lines = result[0].text.split('\n')[:7]
    for line in lines:
        print(f"      {line}")
    print()

    print("=== All tests completed successfully! ===")


async def main():
    try:
        await test_mcp_server()
    except Exception as e:
        print(f"\n✗ Error during testing: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
