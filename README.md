# Elise Voice MCP Server

An MCP (Model Context Protocol) server that provides text-to-speech capabilities using the Elise/Ceylia voice dataset from Hugging Face.

## Current Status (Pre-MLX Migration)

This commit represents the working state using **Coqui TTS XTTS-v2** running on CPU.

## Features

- **Text-to-Speech Generation**: Convert text to speech with automatic playback
- **Voice Characteristics**: Query detailed information about the Elise/Ceylia voice (pitch, speaking rate, quality metrics)
- **Sample Texts**: Browse sample texts from the original dataset
- **Auto-playback**: Generated audio plays automatically via macOS `afplay`
- **Easy Integration**: Works seamlessly with Claude Desktop and other MCP clients

## Dataset

This server uses the [Jinsaryko/Elise](https://huggingface.co/datasets/Jinsaryko/Elise) dataset from Hugging Face, which contains high-quality speech samples from the speaker "Ceylia" with detailed acoustic annotations.

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Setup

1. **Clone or navigate to this directory**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or using uv:
   ```bash
   uv pip install -r requirements.txt
   ```

## Configuration

### For Claude Desktop

Add this configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "elise-voice": {
      "command": "/Users/martin.suehowicz/code/voicemcp_server/venv/bin/python",
      "args": [
        "/Users/martin.suehowicz/code/voicemcp_server/src/elise_voice_server.py"
      ],
      "cwd": "/Users/martin.suehowicz/code/voicemcp_server/src"
    }
  }
}
```

**Note**: Update the paths to match your actual installation directory and virtual environment location.

## Usage

Once configured in Claude Desktop, you can use the following tools:

### 1. Generate Speech

Ask Claude to generate speech from text:

```
Generate speech saying "Hello, I'm Ceylia, and I'm here to help you today!"
```

This will create an audio file in the `audio_output/` directory.

### 2. Get Voice Information

Query voice characteristics:

```
What are the characteristics of the Elise voice?
```

This returns information about pitch, speaking rate, and quality metrics from the dataset.

### 3. Browse Sample Texts

See what kind of content the voice was trained on:

```
Show me some sample texts from the Elise dataset
```

## Available Tools

The server provides three MCP tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `generate_speech` | Generate speech audio from text | `text` (required), `filename` (optional), `play` (optional, default: true) |
| `get_voice_info` | Get voice characteristics and quality metrics | None |
| `list_sample_texts` | List sample texts from the dataset | `limit` (optional, default: 5) |

## Output

Generated audio files are saved in the `audio_output/` directory as WAV files and automatically play via macOS `afplay` (can be disabled with `play: false`).

## Development

### Project Structure

```
voicemcp_server/
├── src/
│   ├── __init__.py
│   ├── elise_voice_server.py  # Main MCP server
│   ├── voice_dataset.py       # Dataset loader
│   └── tts_engine.py          # TTS generation
├── audio_output/              # Generated audio files
├── requirements.txt
├── pyproject.toml
└── README.md
```

### Running Tests

```bash
pytest
```

## Technical Details

- **MCP SDK**: Uses the official Python MCP SDK for server implementation
- **Dataset Loading**: Automatically downloads and caches the Elise dataset from Hugging Face
- **TTS Engine**: Coqui TTS XTTS-v2 (tts_models/multilingual/multi-dataset/xtts_v2)
- **Model Location**: `~/Library/Application Support/tts/tts_models--multilingual--multi-dataset--xtts_v2`
- **Audio Format**: Generates WAV audio files
- **Inference**: CPU-only (Apple Silicon MPS support unreliable)
- **Performance**: ~2-3 seconds per short sentence, ~20 seconds for long sentences
- **Dependencies**: PyTorch 2.5.1, Transformers 4.39.3 (downgraded for compatibility)

## Known Issues

- Voice cloning currently disabled due to torchcodec/ffmpeg compatibility issues
- Apple Silicon GPU (MPS) support unreliable with XTTS-v2
- CPU-only inference is slow for longer text

## Next Steps

Planning to migrate to **mlx-audio** for:
- Better Apple Silicon optimization (Neural Engine + GPU)
- Faster inference
- Voice cloning support via CSM model
- More reliable performance

## Troubleshooting

### Dataset Loading Issues

If you encounter issues loading the dataset:
- Ensure you have a stable internet connection
- Check that you have sufficient disk space for the dataset cache (~500MB)
- The dataset will be cached locally after first download

### Model Download Issues

If XTTS-v2 model fails to download:
- Model is ~6GB, ensure sufficient disk space
- Use manual download: `huggingface-cli download coqui/XTTS-v2 --local-dir ~/Library/Application\ Support/tts/tts_models--multilingual--multi-dataset--xtts_v2`

### Audio Generation Errors

If speech generation fails:
- Verify that TTS library is properly installed
- Check that the output directory is writable
- Ensure XTTS-v2 model is fully downloaded
- Check logs: `~/Library/Logs/Claude/mcp-server-elise-voice.log`

### Claude Desktop Integration

If the server doesn't appear in Claude Desktop:
- Verify the config file path is correct
- Check that the `cwd` path in the config matches your installation
- Ensure virtual environment paths are absolute
- Restart Claude Desktop after changing the config
- Check Claude Desktop logs: `~/Library/Logs/Claude/mcp-server-elise-voice.log`

## License

MIT License

## Acknowledgments

- Dataset: [Jinsaryko/Elise](https://huggingface.co/datasets/Jinsaryko/Elise) on Hugging Face
- TTS Engine: [Coqui TTS](https://github.com/coqui-ai/TTS)
- MCP Protocol: [Anthropic's Model Context Protocol](https://modelcontextprotocol.io/)
