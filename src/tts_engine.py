"""
Text-to-Speech engine using Coqui TTS with voice cloning
"""

import os
import sys

# Set environment variables BEFORE importing torch
os.environ['COQUI_TOS_AGREED'] = '1'

from pathlib import Path
from TTS.api import TTS
import tempfile
import soundfile as sf
import numpy as np
from contextlib import contextmanager


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


class TTSEngine:
    """Handles text-to-speech generation using Coqui TTS with voice cloning"""

    def __init__(self):
        # Initialize with XTTS-v2 which supports voice cloning
        self.tts = None
        self.reference_audio = None
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        # XTTS-v2 MPS support is unreliable, stick with CPU for stability
        self.device = "cpu"

    def _get_tts(self):
        """Lazy initialization of TTS engine"""
        if self.tts is None:
            print("Loading XTTS-v2 model on CPU...", file=sys.stderr, flush=True)
            with suppress_stdout():
                self.tts = TTS(self.model_name, progress_bar=False, gpu=False)
        return self.tts

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
            print(f"Reference audio set: {self.reference_audio}", flush=True)

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

        # Get the TTS engine
        tts = self._get_tts()

        # Generate speech with voice cloning
        with suppress_stdout():
            if self.reference_audio:
                print(f"Generating speech with Elise voice cloning...", file=sys.stderr, flush=True)
                tts.tts_to_file(
                    text=text,
                    file_path=str(output_file),
                    speaker_wav=self.reference_audio,
                    language="en"
                )
            else:
                # Use built-in speaker when no reference audio is provided
                print(f"Generating speech with built-in speaker...", file=sys.stderr, flush=True)
                # XTTS-v2 has several built-in speakers, using "Claribel Dervla" as default
                tts.tts_to_file(
                    text=text,
                    file_path=str(output_file),
                    speaker="Claribel Dervla",
                    language="en"
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
            "supports_voice_cloning": True,
            "has_reference_audio": self.reference_audio is not None
        }
