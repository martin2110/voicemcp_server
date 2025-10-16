# Development Context - Elise Voice MCP Server

## Project Goal
Create an MCP server that allows Claude Desktop to use the Elise/Ceylia voice from the Hugging Face dataset (https://huggingface.co/datasets/Jinsaryko/Elise) for text-to-speech generation.

## Development Journey

### Phase 1: Initial Setup
- Created MCP server structure with three tools
- Integrated Hugging Face datasets library to load Elise voice samples
- Initially attempted to use edge-tts (failed - no voice cloning support)

### Phase 2: Coqui TTS Implementation
- Switched to Coqui TTS with XTTS-v2 model for voice cloning capabilities
- Implemented stdout suppression to prevent breaking MCP JSON protocol
- Added automatic audio playback via macOS `afplay`

### Phase 3: Dependency Hell
**Problem:** Multiple version compatibility issues
- **PyTorch 2.8.0** → `weights_only` security changes broke model loading
  - Solution: Downgraded to PyTorch 2.5.1
- **Transformers 4.57.1** → Missing `BeamSearchScorer` import
  - Solution: Downgraded to Transformers 4.39.3
- **torchcodec** → Couldn't link to ffmpeg libraries for audio decoding
  - Solution: Disabled voice cloning temporarily

### Phase 4: Model Download Issues
**Problem:** XTTS-v2 model (~6GB) timing out during automatic download
- Initial attempts using TTS library auto-download failed after 4+ minutes
- Model directory existed but was empty (0B)
- **Solution:** Manual download using `huggingface-cli download coqui/XTTS-v2`
- Successfully downloaded all 18 files including model.pth (1.9GB)

### Phase 5: Apple Silicon GPU Attempts
**Problem:** Wanted to use Apple Silicon GPU for faster inference

Attempts made:
1. **First attempt:** Auto-detect MPS, set `gpu=True`
   - Failed: TTS library tried to use CUDA instead of MPS
   
2. **Second attempt:** Load on CPU, then move to MPS
   - Failed: "Output channels > 65536 not supported at MPS device"
   
3. **Third attempt:** Set `PYTORCH_ENABLE_MPS_FALLBACK=1`
   - Failed: Environment variable not recognized (set too late, after torch import)
   
4. **Fourth attempt:** Set fallback before importing torch
   - Partially worked: Some generations succeeded, others failed
   - Inconsistent behavior, unreliable for production

**Final decision:** Use CPU-only for stability

## Current Architecture

### Files
- `src/elise_voice_server.py` - Main MCP server with 3 tools
- `src/tts_engine.py` - TTS engine using XTTS-v2
- `src/voice_dataset.py` - Elise dataset loader

### MCP Tools
1. `generate_speech(text, filename, play=true)` - Generate and optionally play audio
2. `get_voice_info()` - Query voice characteristics from dataset
3. `list_sample_texts(limit=5)` - Browse dataset samples

### Configuration
```json
{
  "mcpServers": {
    "elise-voice": {
      "command": "/path/to/voicemcp_server/venv/bin/python",
      "args": [
        "/path/to/voicemcp_server/elise_voice_server/server.py"
      ],
      "cwd": "/path/to/voicemcp_server"
    }
  }
}
```

Or if installed via pipx/pip:
```json
{
  "mcpServers": {
    "elise-voice": {
      "command": "elise-voice-mcp"
    }
  }
}
```

### Key Implementation Details

**Stdout Suppression:**
```python
@contextmanager
def suppress_stdout():
    """Context manager to suppress stdout output"""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
```

**Environment Variables:**
```python
os.environ['COQUI_TOS_AGREED'] = '1'  # Accept XTTS-v2 terms
```

**Built-in Speaker:**
Uses "Claribel Dervla" as default speaker when voice cloning is disabled

## Performance Metrics (CPU-only)
- Model loading: ~3 seconds (lazy initialization)
- Short sentence (10-15 words): ~2-3 seconds
- Long sentence (40+ words): ~20 seconds
- Audio format: WAV, ~500KB per sentence

## What Works
✅ Text-to-speech generation with XTTS-v2
✅ Automatic audio playback
✅ MCP tool integration with Claude Desktop
✅ Dataset loading from Hugging Face
✅ Stable, reliable operation on CPU

## What Doesn't Work
❌ Voice cloning (torchcodec/ffmpeg issues)
❌ Apple Silicon GPU acceleration (MPS unreliable)
❌ Fast inference (CPU-bound)

## Lessons Learned
1. PyTorch version matters - newer isn't always better for compatibility
2. MPS support is still maturing - not all operations supported
3. Manual model downloads more reliable for large files
4. MCP stdout must be pure JSON - suppress all library output
5. Setting environment variables must happen before imports

## Next: MLX-Audio Migration

### Why MLX-Audio?
- **Native Apple Silicon support** - Uses Metal Performance Shaders and Neural Engine
- **Voice cloning** - CSM model supports reference audio
- **Faster inference** - Optimized for M-series chips
- **Better compatibility** - Designed for macOS/Apple Silicon

### Migration Plan
1. Install mlx-audio and dependencies
2. Rewrite tts_engine.py to use mlx-audio CSM model
3. Enable voice cloning with Elise dataset samples
4. Test performance improvements
5. Keep same MCP interface (no breaking changes)

### Expected Benefits
- 5-10x faster inference (GPU + Neural Engine)
- Voice cloning working properly
- More stable on Apple Silicon
- Potential real-time TTS generation

## User Context
- Platform: macOS Apple Silicon
- Use case: SRE/DevOps work, Kubernetes controllers in Go
- Goal: Fast, natural voice responses from Claude
