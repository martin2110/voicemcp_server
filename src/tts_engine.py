"""
Text-to-Speech engine using mlx-audio with voice cloning
"""

import os
import sys
from pathlib import Path
import tempfile
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

        # Generate speech with mlx-audio Kokoro
        print(f"Generating speech with Kokoro voice '{self.voice}'...", file=sys.stderr, flush=True)

        # Extract directory and filename
        output_dir = output_file.parent
        filename_without_ext = output_file.stem

        generate_audio(
            text=text,
            model_path=self.model_name,
            voice=self.voice,
            lang_code="a",  # American English
            file_prefix=filename_without_ext,
            output_path=str(output_dir),
            audio_format="wav",
            sample_rate=24000,
            verbose=False
        )

        return str(output_file)

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
