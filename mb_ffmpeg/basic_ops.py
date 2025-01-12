"""
Basic FFmpeg operations module providing common video and audio processing tasks.
"""
from .base import FFmpegBase
import os
from typing import Optional, Union, Tuple


class BasicOperations(FFmpegBase):
    def convert_format(self, input_file: str, output_format: str, output_file: Optional[str] = None) -> str:
        """
        Convert media file to a different format.

        Args:
            input_file (str): Path to input media file
            output_format (str): Desired output format (e.g., 'mp4', 'mkv', 'avi')
            output_file (Optional[str]): Path to output file. If None, will use input filename with new extension

        Returns:
            str: Path to the converted file

        Example:
            >>> basic_ops = BasicOperations()
            >>> converted_file = basic_ops.convert_format("input.avi", "mp4")
            >>> print(f"Converted file saved as: {converted_file}")
        """
        self.validate_input_file(input_file)
        
        if output_file is None:
            output_file = os.path.splitext(input_file)[0] + f".{output_format}"
        
        self.ensure_output_dir(output_file)
        command = self.build_command(input_file, output_file, ["-c", "copy"])
        
        self._run_command(command)
        return output_file

    def trim_media(self, input_file: str, start_time: int, duration: int, output_file: Optional[str] = None) -> str:
        """
        Trim media file to specified duration.

        Args:
            input_file (str): Path to input media file
            start_time (int): Start time in format "HH:MM:SS" or seconds
            duration (int): Duration in format "HH:MM:SS" or seconds
            output_file (Optional[str]): Path to output file. If None, will append "_trimmed" to input filename

        Returns:
            str: Path to the trimmed file

        Example:
            >>> basic_ops = BasicOperations()
            >>> trimmed_file = basic_ops.trim_media("input.mp4", "00:00:30", "00:01:00")
            >>> print(f"Trimmed file saved as: {trimmed_file}")
        """
        self.validate_input_file(input_file)
        
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_trimmed{ext}"
        
        start_time = str(start_time) if isinstance(start_time, int) else start_time
        duration = str(duration) if isinstance(duration, int) else duration

        self.ensure_output_dir(output_file)
        command = self.build_command(
            input_file, 
            output_file,
            ["-ss", start_time, "-t", duration, "-c", "copy"]
        )
        
        self._run_command(command)
        return output_file

    def extract_frames(self, input_file: str, fps: Union[int, float], output_dir: Optional[str] = None) -> str:
        """
        Extract frames from video file at specified fps rate.

        Args:
            input_file (str): Path to input video file
            fps (Union[int, float]): Frames per second to extract
            output_dir (Optional[str]): Directory to save frames. If None, creates 'frames' directory

        Returns:
            str: Path to the directory containing extracted frames

        Example:
            >>> basic_ops = BasicOperations()
            >>> frames_dir = basic_ops.extract_frames("video.mp4", 1)  # 1 frame per second
            >>> print(f"Frames saved in: {frames_dir}")
        """
        self.validate_input_file(input_file)
        
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(input_file), "frames")
        
        os.makedirs(output_dir, exist_ok=True)
        output_pattern = os.path.join(output_dir, "frame_%04d.jpg")
        
        command = self.build_command(
            input_file,
            output_pattern,
            ["-vf", f"fps={fps}", "-frame_pts", "1"]
        )
        
        self._run_command(command)
        return output_dir

    def change_resolution(self, input_file: str, resolution: Tuple[int, int], output_file: Optional[str] = None) -> str:
        """
        Change video resolution while maintaining aspect ratio.

        Args:
            input_file (str): Path to input video file
            resolution (Tuple[int, int]): Desired width and height
            output_file (Optional[str]): Path to output file. If None, will append "_resized" to input filename

        Returns:
            str: Path to the resized video file

        Example:
            >>> basic_ops = BasicOperations()
            >>> resized_file = basic_ops.change_resolution("input.mp4", (1280, 720))
            >>> print(f"Resized video saved as: {resized_file}")
        """
        self.validate_input_file(input_file)
        
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_resized{ext}"
        
        self.ensure_output_dir(output_file)
        width, height = resolution
        command = self.build_command(
            input_file,
            output_file,
            ["-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"]
        )
        
        self._run_command(command)
        return output_file

    def compress_video(self, input_file: str, crf: int = 23, output_file: Optional[str] = None) -> str:
        """
        Compress video using H.264 codec with specified CRF value.
        Lower CRF means better quality but larger file size (range: 0-51, default: 23).

        Args:
            input_file (str): Path to input video file
            crf (int): Constant Rate Factor value (0-51)
            output_file (Optional[str]): Path to output file. If None, will append "_compressed" to input filename

        Returns:
            str: Path to the compressed video file

        Example:
            >>> basic_ops = BasicOperations()
            >>> compressed_file = basic_ops.compress_video("input.mp4", crf=28)  # More compression
            >>> print(f"Compressed video saved as: {compressed_file}")
        """
        self.validate_input_file(input_file)
        
        if not 0 <= crf <= 51:
            raise ValueError("CRF value must be between 0 and 51")
        
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_compressed{ext}"
        
        self.ensure_output_dir(output_file)
        command = self.build_command(
            input_file,
            output_file,
            ["-c:v", "libx264", "-crf", str(crf), "-preset", "medium"]
        )
        
        self._run_command(command)
        return output_file

    def video_info(self, input_file: str) -> dict:
        """
        Get video information using ffprobe.

        Args:
            input_file (str): Path to input video file

        Returns:
            dict: Dictionary containing video information

        Example:
            >>> basic_ops = BasicOperations()
            >>> info = basic_ops.video_info("video.mp4")
            >>> print(info["duration"])
        """
        return self.probe_file(input_file)