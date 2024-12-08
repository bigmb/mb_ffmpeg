"""
Video operations module providing specialized video processing functionality using FFmpeg.
"""
from .base import FFmpegBase
import os
from typing import Optional, Union, List, Tuple


class VideoOperations(FFmpegBase):
    def crop_video(self, input_file: str, width: int, height: int, x: int, y: int, output_file: Optional[str] = None) -> str:
        """
        Crop a video to specified dimensions from given coordinates.

        Args:
            input_file (str): Path to input video file
            width (int): Width of the crop area
            height (int): Height of the crop area
            x (int): X coordinate of the top-left corner of crop area
            y (int): Y coordinate of the top-left corner of crop area
            output_file (Optional[str]): Path to output file. If None, appends "_cropped" to input filename

        Returns:
            str: Path to the cropped video file

        Example:
            >>> video_ops = VideoOperations()
            >>> cropped = video_ops.crop_video("input.mp4", 1280, 720, 0, 140)
            >>> print(f"Cropped video saved as: {cropped}")
        """
        self.validate_input_file(input_file)
        
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_cropped{ext}"
        
        self.ensure_output_dir(output_file)
        command = self.build_command(
            input_file,
            output_file,
            ["-vf", f"crop={width}:{height}:{x}:{y}"]
        )
        
        self._run_command(command)
        return output_file

    def add_watermark(self, input_file: str, watermark_file: str, position: str = "center", 
                     opacity: float = 0.5, output_file: Optional[str] = None) -> str:
        """
        Add a watermark image to a video.

        Args:
            input_file (str): Path to input video file
            watermark_file (str): Path to watermark image file
            position (str): Position of watermark ('center', 'top_left', 'top_right', 'bottom_left', 'bottom_right')
            opacity (float): Opacity of watermark (0.0 to 1.0)
            output_file (Optional[str]): Path to output file. If None, appends "_watermark" to input filename

        Returns:
            str: Path to the watermarked video file

        Example:
            >>> video_ops = VideoOperations()
            >>> watermarked = video_ops.add_watermark("input.mp4", "logo.png", "bottom_right", 0.3)
            >>> print(f"Watermarked video saved as: {watermarked}")
        """
        self.validate_input_file(input_file)
        self.validate_input_file(watermark_file)
        
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_watermark{ext}"
        
        self.ensure_output_dir(output_file)
        
        # Define position coordinates
        position_map = {
            "center": "overlay=(W-w)/2:(H-h)/2",
            "top_left": "overlay=10:10",
            "top_right": "overlay=W-w-10:10",
            "bottom_left": "overlay=10:H-h-10",
            "bottom_right": "overlay=W-w-10:H-h-10"
        }
        
        if position not in position_map:
            raise ValueError(f"Invalid position. Must be one of: {', '.join(position_map.keys())}")
        
        overlay_filter = f"{position_map[position]}:alpha={opacity}"
        command = self.build_command(
            input_file,
            output_file,
            ["-i", watermark_file, "-filter_complex", overlay_filter]
        )
        
        self._run_command(command)
        return output_file

    def add_text(self, input_file: str, text: str, position: str = "bottom", 
                font_size: int = 24, color: str = "white", output_file: Optional[str] = None) -> str:
        """
        Add text overlay to a video.

        Args:
            input_file (str): Path to input video file
            text (str): Text to overlay
            position (str): Position of text ('top', 'bottom', 'center')
            font_size (int): Font size in pixels
            color (str): Text color name or hex code
            output_file (Optional[str]): Path to output file. If None, appends "_text" to input filename

        Returns:
            str: Path to the video file with text overlay

        Example:
            >>> video_ops = VideoOperations()
            >>> with_text = video_ops.add_text("input.mp4", "Hello World", "bottom", 32, "yellow")
            >>> print(f"Video with text saved as: {with_text}")
        """
        self.validate_input_file(input_file)
        
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_text{ext}"
        
        self.ensure_output_dir(output_file)
        
        # Define position coordinates
        position_map = {
            "top": f"x=(w-text_w)/2:y=10",
            "bottom": f"x=(w-text_w)/2:y=h-th-10",
            "center": f"x=(w-text_w)/2:y=(h-text_h)/2"
        }
        
        if position not in position_map:
            raise ValueError(f"Invalid position. Must be one of: {', '.join(position_map.keys())}")
        
        filter_complex = f"drawtext=text='{text}':fontsize={font_size}:fontcolor={color}:{position_map[position]}"
        command = self.build_command(
            input_file,
            output_file,
            ["-vf", filter_complex]
        )
        
        self._run_command(command)
        return output_file

    def apply_video_filter(self, input_file: str, filter_name: str, 
                         filter_params: Optional[dict] = None, output_file: Optional[str] = None) -> str:
        """
        Apply a video filter with optional parameters.

        Args:
            input_file (str): Path to input video file
            filter_name (str): Name of the filter (e.g., 'eq' for color adjustment, 'unsharp' for sharpening)
            filter_params (Optional[dict]): Dictionary of filter parameters
            output_file (Optional[str]): Path to output file. If None, appends filter name to input filename

        Returns:
            str: Path to the filtered video file

        Example:
            >>> video_ops = VideoOperations()
            >>> # Adjust brightness and contrast
            >>> adjusted = video_ops.apply_video_filter(
            ...     "input.mp4",
            ...     "eq",
            ...     {"brightness": "0.1", "contrast": "1.2"}
            ... )
            >>> print(f"Filtered video saved as: {adjusted}")
        """
        self.validate_input_file(input_file)
        
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_{filter_name}{ext}"
        
        self.ensure_output_dir(output_file)
        
        # Build filter string
        if filter_params:
            filter_str = f"{filter_name}=" + ":".join(f"{k}={v}" for k, v in filter_params.items())
        else:
            filter_str = filter_name
        
        command = self.build_command(
            input_file,
            output_file,
            ["-vf", filter_str]
        )
        
        self._run_command(command)
        return output_file

    def create_gif(self, input_file: str, start_time: str, duration: str, 
                  output_file: Optional[str] = None, fps: int = 10, scale: int = -1) -> str:
        """
        Create an animated GIF from a video segment.

        Args:
            input_file (str): Path to input video file
            start_time (str): Start time in format "HH:MM:SS" or seconds
            duration (str): Duration in format "HH:MM:SS" or seconds
            output_file (Optional[str]): Path to output file. If None, uses input filename with .gif extension
            fps (int): Frames per second for the GIF
            scale (int): Width to scale the GIF to (-1 maintains aspect ratio)

        Returns:
            str: Path to the created GIF file

        Example:
            >>> video_ops = VideoOperations()
            >>> gif = video_ops.create_gif("input.mp4", "00:00:10", "5", fps=15, scale=480)
            >>> print(f"GIF created at: {gif}")
        """
        self.validate_input_file(input_file)
        
        if output_file is None:
            name = os.path.splitext(input_file)[0]
            output_file = f"{name}.gif"
        
        self.ensure_output_dir(output_file)
        
        filters = [f"fps={fps}"]
        if scale != -1:
            filters.append(f"scale={scale}:-1:flags=lanczos")
        
        filter_str = ",".join(filters)
        
        command = self.build_command(
            input_file,
            output_file,
            ["-ss", start_time, "-t", duration, "-vf", filter_str]
        )
        
        self._run_command(command)
        return output_file
