# Elise Voice MCP Server

An MCP (Model Context Protocol) server that provides high-quality text-to-speech capabilities using mlx-audio's Kokoro-82M model, optimized for Apple Silicon.

## Features

- **Fast Text-to-Speech**: Convert text to speech with automatic playback using Apple Silicon GPU acceleration
- **Apple Silicon Optimized**: Uses mlx-audio framework for M1/M2/M3 chips with Metal GPU support
- **Voice Characteristics**: Query detailed information about the Elise/Ceylia voice (pitch, speaking rate, quality metrics)
- **Sample Texts**: Browse sample texts from the original dataset
- **Auto-playback**: Generated audio plays automatically and cleans up after itself
- **Easy Integration**: Works seamlessly with Claude Desktop and any MCP-compatible client
- **Streaming Support**: Automatically handles long text by chunking and playing sequentially

## Dataset

This server uses the [Jinsaryko/Elise](https://huggingface.co/datasets/Jinsaryko/Elise) dataset from Hugging Face, which contains high-quality speech samples from the speaker "Ceylia" with detailed acoustic annotations.

## Installation

### Prerequisites

- **macOS with Apple Silicon** (M1/M2/M3 chip required for mlx-audio)
- Python 3.10 or higher
- pip, pipx, or uv package manager

### Option 1: Install from PyPI (recommended)

```bash
# With pipx (isolated environment, recommended)
pipx install elise-voice-mcp

# Or with uv (modern, fast)
uv tool install elise-voice-mcp

# Or with pip
pip install elise-voice-mcp
```

### Option 2: Install from Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/elise-voice-mcp.git
   cd elise-voice-mcp
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

   # Or with uv
   uv pip install -r requirements.txt
   ```

## Configuration

### For Claude Desktop

Add this configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

#### If installed via pipx/uv/pip:

```json
{
  "mcpServers": {
    "elise-voice": {
      "command": "elise-voice-mcp"
    }
  }
}
```

#### If running from source:

```json
{
  "mcpServers": {
    "elise-voice": {
      "command": "/path/to/your/venv/bin/python",
      "args": [
        "-m",
        "elise_voice_server"
      ]
    }
  }
}
```

**Note**: Restart Claude Desktop after updating the configuration.

## Usage

Once configured in Claude Desktop, you can use the following tools:

### 1. Generate Speech

Ask Claude to generate speech from text:

```
Generate speech saying "Hello, I'm Ceylia, and I'm here to help you today!"
```

The audio will be generated, played automatically, and then deleted.

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

## Technical Details

- **TTS Engine**: mlx-audio with Kokoro-82M model
- **Model**: `prince-canuma/Kokoro-82M` (82M parameters, ungated)
- **Voice**: AF Heart (American Female)
- **Framework**: MLX (Apple Silicon optimized)
- **Hardware Acceleration**: Metal GPU + Neural Engine
- **Audio Format**: WAV (24kHz sample rate)
- **Audio Player**: macOS `afplay`
- **Performance**: ~2-5 seconds for most sentences
- **Long Text**: Automatically chunked and played sequentially
- **Cleanup**: Audio files deleted after playback

## Development

### Project Structure

```
elise-voice-mcp/
├── elise_voice_server/         # Main package
│   ├── __init__.py             # Package exports
│   ├── server.py               # MCP server implementation
│   ├── voice_dataset.py        # Dataset loader
│   └── tts_engine.py           # TTS generation engine
├── audio_output/               # Generated audio files (auto-deleted)
├── pyproject.toml              # Package configuration
├── requirements.txt            # Dependencies
├── test_tts.py                 # Direct TTS testing
└── README.md
```

### Running Tests

Test the TTS engine directly without MCP:

```bash
python test_tts.py
```

### Building for Distribution

```bash
# Build wheel
python -m build

# Install locally for testing
pip install -e .
```

## Troubleshooting

### Server doesn't appear in Claude Desktop

1. Verify config file path is correct
2. Check JSON syntax (use a JSON validator)
3. Restart Claude Desktop after config changes
4. Check logs: `~/Library/Logs/Claude/mcp-server-elise-voice.log`

### Audio not playing

1. Verify `afplay` is available: `which afplay`
2. Check audio output device settings
3. Try running `test_tts.py` directly to isolate the issue
4. Check logs for errors

### Import errors

1. Ensure mlx-audio is installed: `pip list | grep mlx-audio`
2. Verify you're on Apple Silicon (M1/M2/M3)
3. Try reinstalling: `pip install --force-reinstall mlx-audio`

### Performance issues

1. Ensure you're running on Apple Silicon
2. Close other GPU-intensive applications
3. Check Activity Monitor for Metal GPU usage
4. First run downloads the model (~300MB) and may be slower

### Dataset loading issues

1. Ensure stable internet connection
2. Check disk space (dataset ~500MB)
3. Dataset is cached locally after first download
4. Check Hugging Face access (dataset is public)

## Migration from Coqui TTS

If you're upgrading from the Coqui TTS version:

- **10x faster**: MLX uses Apple Silicon GPU vs CPU-only Coqui
- **Smaller model**: 82M params vs 6GB XTTS-v2
- **No voice cloning**: Current version uses default Kokoro voice
- **macOS only**: MLX requires Apple Silicon

## Known Limitations

- **macOS Apple Silicon only**: Requires M1/M2/M3 chip for mlx-audio
- **Voice cloning disabled**: Using default Kokoro AF Heart voice
- **No GPU on other platforms**: mlx-audio is Apple Silicon specific

## Roadmap

- [ ] Re-enable voice cloning with Elise dataset
- [ ] Add more voice options from Kokoro model
- [ ] Support for streaming audio generation
- [ ] Docker support (when MLX container support improves)

## License

MIT License

## Acknowledgments

- Dataset: [Jinsaryko/Elise](https://huggingface.co/datasets/Jinsaryko/Elise) on Hugging Face
- TTS Engine: [mlx-audio](https://github.com/lucasnewman/mlx-audio) by Lucas Newman
- Model: [Kokoro-82M](https://huggingface.co/prince-canuma/Kokoro-82M) by Prince Canuma
- MCP Protocol: [Anthropic's Model Context Protocol](https://modelcontextprotocol.io/)
