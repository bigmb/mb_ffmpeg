"""
Audio operations module providing specialized audio processing functionality using FFmpeg.
"""
from .base import FFmpegBase
import os
from typing import Optional, Union, List, Tuple


class AudioOperations(FFmpegBase):
    def extract_audio(self, input_file: str, output_format: str = "mp3", output_file: Optional[str] = None) -> str:
        """
        Extract audio from a media file.

        Args:
            input_file (str): Path to input media file
            output_format (str): Desired audio format (e.g., 'mp3', 'wav', 'aac')
            output_file (Optional[str]): Path to output file. If None, uses input filename with new extension

        Returns:
            str: Path to the extracted audio file

        Example:
            >>> audio_ops = AudioOperations()
            >>> audio_file = audio_ops.extract_audio("video.mp4", "mp3")
            >>> print(f"Audio extracted to: {audio_file}")
        """
        self.validate_input_file(input_file)
        
        if output_file is None:
            output_file = os.path.splitext(input_file)[0] + f".{output_format}"
        
        self.ensure_output_dir(output_file)
        command = self.build_command(
            input_file,
            output_file,
            ["-vn", "-acodec", "libmp3lame" if output_format == "mp3" else "copy"]
        )
        
        self._run_command(command)
        return output_file

    def change_volume(self, input_file: str, volume: float, output_file: Optional[str] = None) -> str:
        """
        Change audio volume of a media file.

        Args:
            input_file (str): Path to input media file
            volume (float): Volume multiplier (1.0 = original, 0.5 = half, 2.0 = double)
            output_file (Optional[str]): Path to output file. If None, appends "_vol" to input filename

        Returns:
            str: Path to the processed file

        Example:
            >>> audio_ops = AudioOperations()
            >>> louder_file = audio_ops.change_volume("input.mp3", 1.5)  # 50% louder
            >>> print(f"Volume adjusted file saved as: {louder_file}")
        """
        self.validate_input_file(input_file)
        
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_vol{ext}"
        
        self.ensure_output_dir(output_file)
        command = self.build_command(
            input_file,
            output_file,
            ["-af", f"volume={volume}"]
        )
        
        self._run_command(command)
        return output_file

    def normalize_audio(self, input_file: str, target_level: float = -23.0, output_file: Optional[str] = None) -> str:
        """
        Normalize audio to a target loudness level (in LUFS).

        Args:
            input_file (str): Path to input audio file
            target_level (float): Target loudness level in LUFS (default: -23.0 LUFS, EBU R128 standard)
            output_file (Optional[str]): Path to output file. If None, appends "_normalized" to input filename

        Returns:
            str: Path to the normalized audio file

        Example:
            >>> audio_ops = AudioOperations()
            >>> normalized = audio_ops.normalize_audio("input.mp3", target_level=-16.0)
            >>> print(f"Normalized audio saved as: {normalized}")
        """
        self.validate_input_file(input_file)
        
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_normalized{ext}"
        
        self.ensure_output_dir(output_file)
        command = self.build_command(
            input_file,
            output_file,
            ["-af", f"loudnorm=I={target_level}:TP=-1.5:LRA=11"]
        )
        
        self._run_command(command)
        return output_file

    def apply_fade(self, input_file: str, fade_in: float = 0, fade_out: float = 0, output_file: Optional[str] = None) -> str:
        """
        Apply fade-in and/or fade-out effects to audio.

        Args:
            input_file (str): Path to input audio file
            fade_in (float): Fade-in duration in seconds
            fade_out (float): Fade-out duration in seconds
            output_file (Optional[str]): Path to output file. If None, appends "_fade" to input filename

        Returns:
            str: Path to the processed audio file

        Example:
            >>> audio_ops = AudioOperations()
            >>> faded = audio_ops.apply_fade("input.mp3", fade_in=2.0, fade_out=3.0)
            >>> print(f"Audio with fades saved as: {faded}")
        """
        self.validate_input_file(input_file)
        
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_fade{ext}"
        
        self.ensure_output_dir(output_file)
        
        filter_parts = []
        if fade_in > 0:
            filter_parts.append(f"afade=t=in:st=0:d={fade_in}")
        if fade_out > 0:
            # Get duration using ffprobe
            duration = float(self.probe_file(input_file)["format"]["duration"])
            filter_parts.append(f"afade=t=out:st={duration-fade_out}:d={fade_out}")
        
        command = self.build_command(
            input_file,
            output_file,
            ["-af", ",".join(filter_parts)] if filter_parts else ["-c", "copy"]
        )
        
        self._run_command(command)
        return output_file

    def mix_audio(self, input_files: List[str], output_file: str, weights: Optional[List[float]] = None) -> str:
        """
        Mix multiple audio files together with optional weight factors.

        Args:
            input_files (List[str]): List of input audio file paths
            output_file (str): Path to output file
            weights (Optional[List[float]]): List of weight factors for mixing. If None, equal weights are used

        Returns:
            str: Path to the mixed audio file

        Example:
            >>> audio_ops = AudioOperations()
            >>> mixed = audio_ops.mix_audio(
            ...     ["voice.mp3", "background.mp3"],
            ...     "mixed.mp3",
            ...     weights=[1.0, 0.5]
            ... )
            >>> print(f"Mixed audio saved as: {mixed}")
        """
        for input_file in input_files:
            self.validate_input_file(input_file)
        
        if weights is None:
            weights = [1.0] * len(input_files)
        
        if len(weights) != len(input_files):
            raise ValueError("Number of weights must match number of input files")
        
        self.ensure_output_dir(output_file)
        
        # Build complex filter for mixing
        inputs = []
        for i in range(len(input_files)):
            inputs.extend(["-i", input_files[i]])
        
        mix_filter = "[0:a]"
        for i in range(1, len(input_files)):
            mix_filter += f"[{i}:a]"
        mix_filter += f"amix=inputs={len(input_files)}:duration=longest"
        
        command = [self.ffmpeg_path] + inputs + ["-filter_complex", mix_filter, output_file]
        
        self._run_command(command)
        return output_file