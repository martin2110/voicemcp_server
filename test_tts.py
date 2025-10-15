#!/usr/bin/env python3
"""Direct test of TTS engine without MCP protocol"""
import sys
import asyncio

from elise_voice_server.tts_engine import TTSEngine

async def main():
    print("Testing TTS engine directly...", file=sys.stderr)
    
    engine = TTSEngine()
    
    # Test speech generation
    output_path = "audio_output/direct_test.wav"
    text = "Hello! This is a direct test of the TTS engine."
    
    print(f"Generating speech: '{text}'", file=sys.stderr)
    result = await engine.generate_speech(text, output_path)
    print(f"✓ Speech generated: {result}", file=sys.stderr)
    
    # Check if file exists
    import os
    if os.path.exists(result):
        size = os.path.getsize(result)
        print(f"✓ File exists: {size} bytes", file=sys.stderr)
        
        # Try to play it
        import subprocess
        print("Playing audio...", file=sys.stderr)
        subprocess.run(['afplay', result])
        print("✓ Playback complete", file=sys.stderr)
    else:
        print(f"✗ File not found: {result}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
