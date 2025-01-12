"""
Base FFmpeg class that provides core functionality and utilities.
"""
import subprocess
import os
from typing import List, Optional, Union, Dict


class FFmpegBase:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize FFmpeg base class.

        Args:
            ffmpeg_path (str): Path to FFmpeg executable. Defaults to "ffmpeg"
                             assuming it's available in system PATH.
        """
        self.ffmpeg_path = ffmpeg_path
        self._verify_ffmpeg()

    def _verify_ffmpeg(self) -> None:
        """Verify FFmpeg is installed and accessible."""
        try:
            subprocess.run([self.ffmpeg_path, "-version"], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg or provide correct path.")

    def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """
        Execute FFmpeg command and handle errors.

        Args:
            command (List[str]): Command to execute as list of strings.

        Returns:
            subprocess.CompletedProcess: Result of the command execution.
        """
        try:
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if process.returncode != 0:
                raise RuntimeError(f"FFmpeg command failed: {process.stderr}")
            return process
        except Exception as e:
            raise RuntimeError(f"Error executing FFmpeg command: {str(e)}")

    def probe_file(self, input_file: str) -> Dict:
        """
        Get media file information using ffprobe.

        Args:
            input_file (str): Path to input media file.

        Returns:
            Dict: Dictionary containing file information.

        Example:
            >>> ffmpeg = FFmpegBase()
            >>> info = ffmpeg.probe_file("video.mp4")
            >>> print(info["duration"])
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        command = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            input_file
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFprobe failed: {result.stderr}")
        
        import json
        return json.loads(result.stdout)

    def validate_input_file(self, input_file: str) -> None:
        """
        Validate if input file exists and is accessible.

        Args:
            input_file (str): Path to input file.
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

    def ensure_output_dir(self, output_file: str) -> None:
        """
        Ensure output directory exists, create if necessary.

        Args:
            output_file (str): Path to output file.
        """
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def build_command(self, input_file: str, output_file: str, options: List[str],logs=False) -> List[str]:
        """
        Build FFmpeg command with input, output, and options.

        Args:
            input_file (str): Path to input file.
            output_file (str): Path to output file.
            options (List[str]): List of FFmpeg options.

        Returns:
            List[str]: Complete FFmpeg command as list of strings.
        """
        command = [self.ffmpeg_path, "-i", input_file]
        command.extend(options)
        if logs:
            command.append("-hide_banner")
            command.append("-loglevel")
            command.append("debug")
        command.append(output_file)
        return command
