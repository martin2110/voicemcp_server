"""
Dataset loader for the Elise/Ceylia voice dataset from Hugging Face
"""

from typing import Dict, List, Any
from datasets import load_dataset
import numpy as np


class EliseVoiceDataset:
    """Manages loading and accessing the Elise voice dataset"""

    def __init__(self):
        self.dataset = None
        self.dataset_name = "Jinsaryko/Elise"

    async def load(self):
        """Load the dataset from Hugging Face"""
        if self.dataset is None:
            print(f"Loading dataset {self.dataset_name}...")
            # Load in a non-blocking way
            self.dataset = load_dataset(self.dataset_name, split="train")
            print(f"Dataset loaded: {len(self.dataset)} samples")

    def get_voice_characteristics(self) -> Dict[str, Any]:
        """
        Get average voice characteristics from the dataset
        Returns statistics about pitch, speaking rate, and quality metrics
        """
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load() first.")

        # Calculate average characteristics
        pitch_means = []
        pitch_stds = []
        speaking_rates = []
        stoi_scores = []
        pesq_scores = []

        for sample in self.dataset:
            if sample.get("utterance_pitch_mean") is not None:
                pitch_means.append(float(sample["utterance_pitch_mean"]))
            if sample.get("utterance_pitch_std") is not None:
                pitch_stds.append(float(sample["utterance_pitch_std"]))
            if sample.get("speaking_rate") is not None:
                speaking_rates.append(float(sample["speaking_rate"]))
            if sample.get("stoi") is not None:
                stoi_scores.append(float(sample["stoi"]))
            if sample.get("pesq") is not None:
                pesq_scores.append(float(sample["pesq"]))

        return {
            "speaker_name": self.dataset[0].get("speaker_name", "Ceylia"),
            "total_samples": len(self.dataset),
            "pitch_mean": np.mean(pitch_means) if pitch_means else 0,
            "pitch_std": np.mean(pitch_stds) if pitch_stds else 0,
            "speaking_rate": np.mean(speaking_rates) if speaking_rates else 0,
            "stoi": np.mean(stoi_scores) if stoi_scores else 0,
            "pesq": np.mean(pesq_scores) if pesq_scores else 0,
        }

    def get_sample_texts(self, limit: int = 5) -> List[str]:
        """
        Get sample texts from the dataset
        Args:
            limit: Maximum number of samples to return
        Returns:
            List of text samples
        """
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load() first.")

        texts = []
        count = 0

        for sample in self.dataset:
            if count >= limit:
                break
            if sample.get("text"):
                texts.append(sample["text"])
                count += 1

        return texts

    def get_audio_sample(self, index: int = 0) -> Dict[str, Any]:
        """
        Get a specific audio sample with its metadata
        Args:
            index: Index of the sample to retrieve
        Returns:
            Dictionary containing audio data and metadata
        """
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load() first.")

        if index >= len(self.dataset):
            raise IndexError(f"Index {index} out of range (dataset has {len(self.dataset)} samples)")

        sample = self.dataset[index]
        return {
            "text": sample.get("text"),
            "audio": sample.get("audio"),
            "speaker_name": sample.get("speaker_name"),
            "duration": sample.get("audioduration"),
            "pitch_mean": sample.get("utterance_pitch_mean"),
            "speaking_rate": sample.get("speaking_rate"),
        }
