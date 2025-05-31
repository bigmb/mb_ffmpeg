"""
Video operations module providing specialized video processing functionality using FFmpeg.
"""
from .base import FFmpegBase
import os
from typing import Optional


class VideoOperations(FFmpegBase):
    def crop_video(self, input_file: str, width: int, height: int, 
                   x: Optional[int] = None, y: Optional[int] = None, output_file: Optional[str] = None) -> str:
        """
        Crop a video to specified dimensions from given coordinates.

        Args:
            input_file (str): Path to input video file
            width (int): Width of the crop area
            height (int): Height of the crop area
            x (Optional[int]): X coordinate of the top-left corner of crop area
            y (Optional[int]): Y coordinate of the top-left corner of crop area
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

        if x and y:
            command = self.build_command(
                input_file,
                output_file,
                ["-vf", f"crop={width}:{height}:{x}:{y}"]
            )
        else:
            command = self.build_command(
                input_file,
                output_file,
                ["-vf", f"crop=in_h*{width}/{height}:in_h"]
            )

        self._run_command(command)
        return output_file

    def add_watermark(self, input_file: str, watermark_file: str, position: str = "center", 
                     opacity: float = 0.5, output_file: Optional[str] = None, postion_value : Optional[str] = None) -> str:
        """
        Add a watermark image to a video.

        Args:
            input_file (str): Path to input video file
            watermark_file (str): Path to watermark image file
            position (str): Position of watermark ('center', 'top_left', 'top_right', 'bottom_left', 'bottom_right')
            opacity (float): Opacity of watermark (0.0 to 1.0)
            output_file (Optional[str]): Path to output file. If None, appends "_watermark" to input filename
            postition_value (Optional[str]): Position value of watermark. If None, uses default position. Format: "overlay=x:y"

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
        
        # Define position coordinates if position_value is not provided
        position_map = {
            "center": "overlay=(W-w)/2:(H-h)/2",
            "top_left": "overlay=10:10",
            "top_right": "overlay=W-w-10:10",
            "bottom_left": "overlay=10:H-h-10",
            "bottom_right": "overlay=W-w-10:H-h-10"
        }

        if postion_value:
            position = "custom"
            position_map["custom"] = postion_value
        
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
            ["-y","-ss", start_time, "-t", duration, "-vf", filter_str]
        )
        
        self._run_command(command)
        return output_file

    def change_aspect_ratio(self, input_file: str, aspect_ratio: str, output_file: Optional[str] = None,logs=False) -> str:
        """
        Change the aspect ratio of a video.

        Args:
            input_file (str): Path to input video file
            aspect_ratio (str): New aspect ratio (e.g., '0.5625' for 9:16, '1.3333' for 4:3)
            output_file (Optional[str]): Path to output file. If None, appends "_aspect" to input filename

        Returns:
            str: Path to the video with changed aspect ratio

        Example:
            >>> video_ops = VideoOperations()
            >>> adjusted = video_ops.change_aspect_ratio("input.mp4", "0.5625")
            >>> print(f"Aspect ratio adjusted video saved as: {adjusted}")
        """
        self.validate_input_file(input_file)
        
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_aspect{ext}"
        
        self.ensure_output_dir(output_file)

        # Build and execute the FFmpeg command
        command = self.build_command(
            input_file,
            output_file,
            ["-vf", f"setsar={aspect_ratio}"]
        )

        if logs:
            command.append(logs)

        self._run_command(command)
        return output_file

    def add_audio_to_video(self, video_file: str, audio_file: str, output_file: str) -> str:
        """
        Replace the audio of a video file with a new audio track.

        Args:
            video_file (str): Path to the input video file
            audio_file (str): Path to the audio file to use
            output_file (str): Path to save the new video

        Returns:
            str: Path to the output video file

        Example:
            >>> video_ops = VideoOperations()
            >>> final_video = video_ops.add_audio_to_video("input.mp4", "mixed.mp3", "output.mp4")
            >>> print(f"Final video saved as: {final_video}")
        """
        self.validate_input_file(video_file)
        self.validate_input_file(audio_file)
        self.ensure_output_dir(output_file)

        command = [
            self.ffmpeg_path,
            "-i", video_file,
            "-i", audio_file,
            "-c:v", "copy",        # Copy video stream without re-encoding
            "-map", "0:v:0",       # Map video stream from the first input
            "-map", "1:a:0",       # Map audio stream from the second input
            "-shortest",           # Cut output to shortest input length
            "-y",                  # Overwrite output if exists
            output_file
        ]

        self._run_command(command)
        return output_file
