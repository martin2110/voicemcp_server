"""
Text-to-Speech engine using mlx-audio with voice cloning
"""

import os
import sys
import shutil
from pathlib import Path
import tempfile
from contextlib import redirect_stdout, redirect_stderr
import soundfile as sf
from mlx_audio.tts.generate import generate_audio


class TTSEngine:
    """Handles text-to-speech generation using mlx-audio CSM with voice cloning"""

    def __init__(self):
        # Initialize with Kokoro-82M model (optimized for Apple Silicon, ungated)
        self.reference_audio = None
        self.model_name = "prince-canuma/Kokoro-82M"
        self.voice = "af_heart"  # Default voice: AF Heart
        print("Using mlx-audio Kokoro-82M model (Apple Silicon optimized)", file=sys.stderr, flush=True)

    def set_reference_audio(self, audio_data: dict):
        """
        Set reference audio for voice cloning

        Args:
            audio_data: Dictionary containing 'array' and 'sampling_rate' from the dataset
        """
        # Save reference audio to a temporary file
        if audio_data and 'array' in audio_data and 'sampling_rate' in audio_data:
            # Create a temporary file for the reference audio
            temp_ref = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            sf.write(temp_ref.name, audio_data['array'], audio_data['sampling_rate'])
            self.reference_audio = temp_ref.name
            print(f"Reference audio set: {self.reference_audio}", file=sys.stderr, flush=True)

    def _split_text_into_chunks(self, text: str, max_chunk_size: int = 150) -> list[str]:
        """
        Split text into smaller chunks for faster initial audio generation

        Args:
            text: The text to split
            max_chunk_size: Maximum characters per chunk (default: ~1-2 sentences)

        Returns:
            List of text chunks
        """
        # Split on sentence boundaries
        import re
        sentences = re.split(r'([.!?]+(?:\s+|$))', text)

        # Recombine sentences with their punctuation
        chunks = []
        current_chunk = ""

        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            full_sentence = sentence + punctuation

            # If adding this sentence would exceed max_chunk_size, start a new chunk
            if current_chunk and len(current_chunk) + len(full_sentence) > max_chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = full_sentence
            else:
                current_chunk += full_sentence

        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    async def generate_speech(self, text: str, output_path: str, reference_audio_data: dict = None) -> str:
        """
        Generate speech from text using voice cloning

        Args:
            text: The text to convert to speech
            output_path: Path where the audio file will be saved
            reference_audio_data: Optional audio data from Elise dataset for voice cloning

        Returns:
            Path to the generated audio file
        """
        # Create output directory if it doesn't exist
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Set reference audio if provided
        if reference_audio_data:
            self.set_reference_audio(reference_audio_data)

        # Split text into smaller chunks for faster initial response
        chunks = self._split_text_into_chunks(text)
        print(f"Generating speech in {len(chunks)} chunk(s) with Kokoro voice '{self.voice}'...", file=sys.stderr, flush=True)

        # Extract directory and filename
        output_dir = output_file.parent.resolve()  # Get absolute path
        filename_without_ext = output_file.stem

        all_generated_files = []

        # Generate each chunk separately
        for i, chunk in enumerate(chunks):
            chunk_filename = f"{filename_without_ext}_chunk{i}"

            # mlx-audio has a bug - it always writes to cwd, ignoring output_path
            # We need to cd to the output directory before calling generate_audio
            original_cwd = Path.cwd()

            try:
                # Change to output directory so mlx-audio writes there
                os.chdir(output_dir)

                # Suppress mlx-audio's stdout output (it prints colored text even with verbose=False)
                # This breaks MCP JSON protocol, so we redirect to /dev/null
                with open(os.devnull, 'w') as devnull:
                    with redirect_stdout(devnull):
                        generate_audio(
                            text=chunk,
                            model_path=self.model_name,
                            voice=self.voice,
                            lang_code="a",  # American English
                            file_prefix=chunk_filename,
                            output_path=".",  # mlx-audio ignores this parameter
                            audio_format="wav",
                            sample_rate=24000,
                            verbose=False
                        )
            finally:
                # Always restore original working directory
                os.chdir(original_cwd)

            # mlx-audio automatically appends _000, _001, etc. for long text within a chunk
            # Find all generated files for this chunk
            import glob
            chunk_files = sorted(glob.glob(str(output_dir / f"{chunk_filename}_*.wav")))

            if chunk_files:
                all_generated_files.extend(chunk_files)

        if not all_generated_files:
            raise FileNotFoundError(f"No audio files generated for {filename_without_ext}")

        # Return list of all generated files (comma-separated)
        return ",".join(all_generated_files)

    def get_model_info(self) -> dict:
        """
        Get information about the current TTS model

        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "framework": "mlx-audio (Apple Silicon optimized)",
            "supports_voice_cloning": True,
            "has_reference_audio": self.reference_audio is not None
        }
