#!/usr/bin/env python3
"""
Elise Voice MCP Server
Provides text-to-speech capabilities using the Elise/Ceylia voice dataset
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional
import base64
import subprocess

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.server.stdio

from .voice_dataset import EliseVoiceDataset
from .tts_engine import TTSEngine


# Initialize server
app = Server("elise-voice-server")

# Global instances
dataset: Optional[EliseVoiceDataset] = None
tts_engine: Optional[TTSEngine] = None


async def initialize_tts_engine():
    """Pre-warm the TTS engine on server startup"""
    global tts_engine
    if tts_engine is None:
        tts_engine = TTSEngine()
        # Warm up by generating a tiny audio snippet to load the model
        import tempfile
        warmup_text = "Hi"
        warmup_file = Path(tempfile.gettempdir()) / "warmup.wav"
        try:
            await tts_engine.generate_speech(warmup_text, str(warmup_file))
            # Clean up warmup files
            import glob
            for f in glob.glob(str(warmup_file.parent / "warmup_*.wav")):
                Path(f).unlink()
        except Exception as e:
            print(f"Warning: TTS warmup failed: {e}", file=sys.stderr, flush=True)


def get_output_dir() -> Path:
    """Get or create output directory for generated audio files"""
    # Use environment variable if set, otherwise use temp directory
    if "ELISE_VOICE_OUTPUT_DIR" in os.environ:
        output_dir = Path(os.environ["ELISE_VOICE_OUTPUT_DIR"])
    else:
        # Create a temporary directory that persists for the session
        import tempfile
        output_dir = Path(tempfile.gettempdir()) / "elise_voice_output"

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="generate_speech",
            description="Generate speech audio using the Elise/Ceylia voice. Returns the path to the generated audio file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to convert to speech"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional filename for the output audio file (without extension)",
                        "default": "output"
                    },
                    "play": {
                        "type": "boolean",
                        "description": "Whether to play the audio immediately after generation (default: true)",
                        "default": True
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="get_voice_info",
            description="Get information about the Elise/Ceylia voice characteristics including pitch, speaking rate, and quality metrics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_sample_texts",
            description="Get a list of sample texts from the Elise dataset that show the type of content the voice was trained on",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of samples to return (default: 5)",
                        "default": 5
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    global dataset, tts_engine

    # Initialize dataset only for tools that need it
    if name in ["get_voice_info", "list_sample_texts"]:
        if dataset is None:
            dataset = EliseVoiceDataset()
            await dataset.load()

    # TTS engine should already be initialized from startup
    if tts_engine is None:
        tts_engine = TTSEngine()

    if name == "generate_speech":
        text = arguments.get("text", "")
        filename = arguments.get("filename", "output")
        play = arguments.get("play", True)

        if not text:
            return [TextContent(
                type="text",
                text="Error: No text provided for speech generation"
            )]

        # Generate speech using Elise voice
        output_dir = get_output_dir()
        output_path = output_dir / f"{filename}.wav"

        try:
            # Generate speech using default CSM voice
            # TODO: Re-enable voice cloning once we solve audio loading without torchcodec
            actual_path = await tts_engine.generate_speech(text, str(output_path), reference_audio_data=None)

            # Play audio if requested - do it in background so we can return text immediately
            if play:
                # actual_path may contain multiple files (comma-separated) for long text
                audio_files = actual_path.split(',')

                async def play_audio_files():
                    """Background task to play audio files sequentially"""
                    for audio_file in audio_files:
                        try:
                            process = await asyncio.create_subprocess_exec('afplay', audio_file)
                            await process.wait()
                            # Delete the file after playing
                            Path(audio_file).unlink()
                        except Exception as e:
                            print(f"Error playing audio file {audio_file}: {e}", file=sys.stderr, flush=True)

                # Start playback in background without waiting
                asyncio.create_task(play_audio_files())
                status = f"Speech generated and playing! ({len(audio_files)} file(s))"
            else:
                status = "Speech generated successfully!"

            # Return immediately while audio plays in background
            return [TextContent(
                type="text",
                text=f"{status}\n\nOutput file(s): {actual_path}\n\nText: {text}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error generating speech: {str(e)}"
            )]

    elif name == "get_voice_info":
        voice_info = dataset.get_voice_characteristics()

        info_text = "## Elise/Ceylia Voice Characteristics\n\n"
        info_text += f"**Speaker:** {voice_info['speaker_name']}\n"
        info_text += f"**Total Samples:** {voice_info['total_samples']}\n\n"
        info_text += "### Acoustic Properties\n"
        info_text += f"- **Pitch (mean):** {voice_info['pitch_mean']:.2f} Hz\n"
        info_text += f"- **Pitch (std):** {voice_info['pitch_std']:.2f} Hz\n"
        info_text += f"- **Speaking Rate:** {voice_info['speaking_rate']:.2f} phonemes/sec\n\n"
        info_text += "### Quality Metrics\n"
        info_text += f"- **STOI (Speech Intelligibility):** {voice_info['stoi']:.3f}\n"
        info_text += f"- **PESQ (Speech Quality):** {voice_info['pesq']:.3f}\n"

        return [TextContent(type="text", text=info_text)]

    elif name == "list_sample_texts":
        limit = arguments.get("limit", 5)
        samples = dataset.get_sample_texts(limit)

        sample_text = f"## Sample Texts from Elise Dataset (showing {len(samples)} samples)\n\n"
        for i, sample in enumerate(samples, 1):
            sample_text += f"{i}. \"{sample}\"\n\n"

        return [TextContent(type="text", text=sample_text)]

    else:
        return [TextContent(
            type="text",
            text=f"Error: Unknown tool '{name}'"
        )]


async def async_main():
    """Async main entry point for the server"""
    # Pre-warm the TTS engine before accepting connections
    await initialize_tts_engine()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Synchronous main entry point (for CLI)"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
