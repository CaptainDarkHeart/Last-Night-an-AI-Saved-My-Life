"""Track analysis and feature extraction."""

import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Optional, Dict, List, Tuple


class Track:
    """Represents an audio track with analysis metadata."""

    def __init__(self, audio_path: str, sample_rate: int = 44100):
        """
        Initialize a Track object.

        Args:
            audio_path: Path to audio file (WAV, AIFF, MP3, FLAC, etc.)
            sample_rate: Target sample rate (default: 44100 Hz)
        """
        self.audio_path = Path(audio_path)
        self.name = self.audio_path.stem
        self.sample_rate = sample_rate

        # Audio data
        self.audio: Optional[np.ndarray] = None
        self.duration: Optional[float] = None

        # Beat/tempo analysis
        self.beats: Optional[np.ndarray] = None
        self.downbeats: Optional[np.ndarray] = None
        self.tempo: Optional[float] = None

        # Features
        self.features: Dict[str, np.ndarray] = {}

        # Cue points
        self.cue_points: Optional[np.ndarray] = None
        self.cue_points_indices: Optional[np.ndarray] = None

    def load_audio(self) -> None:
        """Load audio file and resample to target sample rate."""
        try:
            # Load audio using soundfile (supports more formats than librosa)
            self.audio, sr = sf.read(str(self.audio_path))

            # Convert to mono if stereo
            if len(self.audio.shape) > 1:
                self.audio = np.mean(self.audio, axis=1)

            # Resample if needed
            if sr != self.sample_rate:
                self.audio = librosa.resample(
                    self.audio,
                    orig_sr=sr,
                    target_sr=self.sample_rate
                )

            self.duration = len(self.audio) / self.sample_rate

        except Exception as e:
            raise ValueError(f"Failed to load audio file {self.audio_path}: {e}")

    def detect_beats(self) -> Tuple[np.ndarray, float]:
        """
        Detect beats and estimate tempo using librosa.

        Returns:
            Tuple of (beat_times, tempo)
        """
        if self.audio is None:
            self.load_audio()

        # Detect tempo and beats
        tempo, beat_frames = librosa.beat.beat_track(
            y=self.audio,
            sr=self.sample_rate,
            units='frames'
        )

        # Convert frames to time
        beat_times = librosa.frames_to_time(
            beat_frames,
            sr=self.sample_rate
        )

        self.beats = beat_times
        self.tempo = float(tempo)

        return beat_times, self.tempo

    def detect_downbeats(self) -> np.ndarray:
        """
        Estimate downbeats (assuming 4/4 time signature).

        Returns:
            Array of downbeat times in seconds
        """
        if self.beats is None:
            self.detect_beats()

        # Simple heuristic: every 4th beat is a downbeat
        # In production, use madmom for better accuracy
        downbeat_indices = np.arange(0, len(self.beats), 4)
        self.downbeats = self.beats[downbeat_indices]

        return self.downbeats

    def extract_features_for_beats(self) -> Dict[str, np.ndarray]:
        """
        Extract 24-dimensional feature vectors at each beat.

        Features:
        - 13 MFCC coefficients
        - 7 Spectral Contrast bands
        - 1 Spectral Centroid
        - 1 Spectral Rolloff
        - 1 Spectral Flux
        - 1 RMS Energy

        Returns:
            Dictionary of feature arrays
        """
        if self.audio is None:
            self.load_audio()

        if self.beats is None:
            self.detect_beats()

        # Extract MFCCs (13 coefficients)
        mfcc = librosa.feature.mfcc(
            y=self.audio,
            sr=self.sample_rate,
            n_mfcc=13
        )

        # Extract Spectral Contrast (7 bands)
        spectral_contrast = librosa.feature.spectral_contrast(
            y=self.audio,
            sr=self.sample_rate,
            n_bands=7
        )

        # Extract Spectral Centroid
        spectral_centroid = librosa.feature.spectral_centroid(
            y=self.audio,
            sr=self.sample_rate
        )

        # Extract Spectral Rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=self.audio,
            sr=self.sample_rate
        )

        # Calculate Spectral Flux (difference between consecutive frames)
        spec = np.abs(librosa.stft(self.audio))
        spectral_flux = np.sqrt(
            np.sum(np.diff(spec, axis=1)**2, axis=0)
        )
        spectral_flux = np.pad(spectral_flux, (1, 0), mode='edge')

        # Extract RMS Energy
        rms = librosa.feature.rms(y=self.audio)

        # Sample features at beat times
        beat_frames = librosa.time_to_frames(
            self.beats,
            sr=self.sample_rate
        )

        # Build feature matrix (24 x num_beats)
        features_at_beats = []

        for beat_frame in beat_frames:
            # Ensure we don't go out of bounds
            frame_idx = min(beat_frame, mfcc.shape[1] - 1)

            beat_features = np.concatenate([
                mfcc[:, frame_idx],                    # 13 MFCCs
                spectral_contrast[:, frame_idx],       # 7 Spectral Contrast
                [spectral_centroid[0, frame_idx]],     # 1 Centroid
                [spectral_rolloff[0, frame_idx]],      # 1 Rolloff
                [spectral_flux[frame_idx]],            # 1 Flux
                [rms[0, frame_idx]]                    # 1 RMS
            ])

            features_at_beats.append(beat_features)

        # Convert to numpy array (num_beats x 24)
        self.features['beat_features'] = np.array(features_at_beats)

        return self.features

    def to_dict(self) -> Dict:
        """
        Convert track analysis to dictionary format.

        Returns:
            Dictionary with all track metadata
        """
        return {
            'name': self.name,
            'path': str(self.audio_path),
            'duration': float(self.duration) if self.duration else None,
            'sample_rate': self.sample_rate,
            'tempo': float(self.tempo) if self.tempo else None,
            'num_beats': len(self.beats) if self.beats is not None else None,
            'num_downbeats': len(self.downbeats) if self.downbeats is not None else None,
            'beats': self.beats.tolist() if self.beats is not None else None,
            'downbeats': self.downbeats.tolist() if self.downbeats is not None else None,
            'cue_points': self.cue_points.tolist() if self.cue_points is not None else None,
            'cue_points_indices': self.cue_points_indices.tolist() if self.cue_points_indices is not None else None,
        }
