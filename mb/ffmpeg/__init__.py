"""
mb_ffmpeg - A Python package for FFmpeg operations using Object-Oriented Programming

This package provides a clean, object-oriented interface to FFmpeg operations,
from basic to advanced functionalities.
"""

from .base import FFmpegBase
from .basic_ops import BasicOperations
from .audio_ops import AudioOperations
from .video_ops import VideoOperations
from .advanced_ops import AdvancedOperations

__all__ = ['FFmpegBase', 'BasicOperations', 'AudioOperations', 'VideoOperations', 'AdvancedOperations']
