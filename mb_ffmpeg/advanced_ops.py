"""
Advanced FFmpeg operations module providing complex functionality like concatenation,
streaming, and advanced filtering capabilities.
"""
from .base import FFmpegBase
import os
from typing import Optional, Union, List, Dict, Tuple


class AdvancedOperations(FFmpegBase):
    def concat_videos(self, input_files: List[str], output_file: str, 
                     transition: Optional[str] = None, transition_duration: float = 1.0) -> str:
        """
        Concatenate multiple video files with optional transitions.

        Args:
            input_files (List[str]): List of input video file paths
            output_file (str): Path to output file
            transition (Optional[str]): Type of transition ('fade', 'dissolve', None)
            transition_duration (float): Duration of transition in seconds

        Returns:
            str: Path to the concatenated video file

        Example:
            >>> advanced_ops = AdvancedOperations()
            >>> merged = advanced_ops.concat_videos(
            ...     ["part1.mp4", "part2.mp4", "part3.mp4"],
            ...     "merged.mp4",
            ...     transition="dissolve",
            ...     transition_duration=0.5
            ... )
            >>> print(f"Concatenated video saved as: {merged}")
        """
        for input_file in input_files:
            self.validate_input_file(input_file)
        
        self.ensure_output_dir(output_file)
        
        if transition:
            # Complex concatenation with transitions
            filter_complex = []
            for i in range(len(input_files)):
                filter_complex.append(f"[{i}:v]format=yuva420p,fade=d={transition_duration}:t=in:alpha=1,setpts=PTS-STARTPTS[v{i}]")
            
            for i in range(len(input_files) - 1):
                filter_complex.append(f"[v{i}][v{i+1}]overlay=format=yuv420[v{i+1}out]")
            
            filter_str = ";".join(filter_complex)
            
            inputs = []
            for input_file in input_files:
                inputs.extend(["-i", input_file])
            
            command = [self.ffmpeg_path] + inputs + ["-filter_complex", filter_str, output_file]
        else:
            # Simple concatenation
            concat_file = "concat_list.txt"
            with open(concat_file, "w") as f:
                for input_file in input_files:
                    f.write(f"file '{input_file}'\n")
            
            command = self.build_command(
                concat_file,
                output_file,
                ["-f", "concat", "-safe", "0"]
            )
        
        self._run_command(command)
        
        # Clean up concat list file if it was created
        if not transition and os.path.exists(concat_file):
            os.remove(concat_file)
        
        return output_file

    def create_streaming_variant(self, input_file: str, output_dir: str, 
                               resolutions: List[Tuple[int, int]], 
                               segment_duration: int = 6) -> str:
        """
        Create HLS streaming variants of a video with multiple resolutions.

        Args:
            input_file (str): Path to input video file
            output_dir (str): Directory to store streaming files
            resolutions (List[Tuple[int, int]]): List of (width, height) tuples for different qualities
            segment_duration (int): Duration of each segment in seconds

        Returns:
            str: Path to the master playlist file

        Example:
            >>> advanced_ops = AdvancedOperations()
            >>> master_playlist = advanced_ops.create_streaming_variant(
            ...     "input.mp4",
            ...     "stream",
            ...     [(1920, 1080), (1280, 720), (854, 480)],
            ...     segment_duration=4
            ... )
            >>> print(f"Streaming files created in: {output_dir}")
        """
        self.validate_input_file(input_file)
        os.makedirs(output_dir, exist_ok=True)
        
        master_playlist = os.path.join(output_dir, "master.m3u8")
        master_content = "#EXTM3U\n"
        
        for width, height in resolutions:
            variant_name = f"{width}x{height}"
            variant_dir = os.path.join(output_dir, variant_name)
            os.makedirs(variant_dir, exist_ok=True)
            
            playlist_file = os.path.join(variant_dir, "playlist.m3u8")
            
            command = self.build_command(
                input_file,
                os.path.join(variant_dir, "segment%d.ts"),
                [
                    "-vf", f"scale={width}:{height}",
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-f", "hls",
                    "-hls_time", str(segment_duration),
                    "-hls_playlist_type", "vod",
                    "-hls_segment_filename",
                    os.path.join(variant_dir, "segment%d.ts"),
                    playlist_file
                ]
            )
            
            self._run_command(command)
            
            # Add variant to master playlist
            bandwidth = int(width * height * 0.1 * 1024)  # Rough estimate of bandwidth
            master_content += f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={width}x{height}\n"
            master_content += f"{variant_name}/playlist.m3u8\n"
        
        # Write master playlist
        with open(master_playlist, "w") as f:
            f.write(master_content)
        
        return master_playlist

    def apply_complex_filter(self, input_file: str, filter_graph: str, output_file: str) -> str:
        """
        Apply a complex filter graph to a video.

        Args:
            input_file (str): Path to input video file
            filter_graph (str): FFmpeg filter graph string
            output_file (str): Path to output file

        Returns:
            str: Path to the processed video file

        Example:
            >>> advanced_ops = AdvancedOperations()
            >>> # Split screen effect
            >>> filtered = advanced_ops.apply_complex_filter(
            ...     "input.mp4",
            ...     "[0:v]split[left][right];[left]crop=iw/2:ih:0:0[l];[right]crop=iw/2:ih:iw/2:0[r];[l][r]vstack",
            ...     "split_screen.mp4"
            ... )
            >>> print(f"Filtered video saved as: {filtered}")
        """
        self.validate_input_file(input_file)
        self.ensure_output_dir(output_file)
        
        command = self.build_command(
            input_file,
            output_file,
            ["-filter_complex", filter_graph]
        )
        
        self._run_command(command)
        return output_file

    def create_video_wall(self, input_files: List[str], layout: Tuple[int, int], 
                         output_file: str, duration: Optional[str] = None) -> str:
        """
        Create a video wall from multiple input videos.

        Args:
            input_files (List[str]): List of input video file paths
            layout (Tuple[int, int]): Grid layout as (rows, columns)
            output_file (str): Path to output file
            duration (Optional[str]): Duration of output video (default: shortest input)

        Returns:
            str: Path to the video wall file

        Example:
            >>> advanced_ops = AdvancedOperations()
            >>> wall = advanced_ops.create_video_wall(
            ...     ["video1.mp4", "video2.mp4", "video3.mp4", "video4.mp4"],
            ...     (2, 2),
            ...     "video_wall.mp4",
            ...     duration="00:01:00"
            ... )
            >>> print(f"Video wall saved as: {wall}")
        """
        for input_file in input_files:
            self.validate_input_file(input_file)
        
        rows, cols = layout
        if len(input_files) != rows * cols:
            raise ValueError(f"Number of input files ({len(input_files)}) must match layout size ({rows}x{cols})")
        
        self.ensure_output_dir(output_file)
        
        # Build complex filter for video wall
        filter_complex = []
        
        # Scale each input
        for i in range(len(input_files)):
            filter_complex.append(f"[{i}:v]scale=iw/{cols}:ih/{rows}[v{i}]")
        
        # Create rows
        for row in range(rows):
            row_filters = []
            for col in range(cols):
                idx = row * cols + col
                row_filters.append(f"[v{idx}]")
            row_filters.append(f"hstack=inputs={cols}[row{row}]")
            filter_complex.append("".join(row_filters))
        
        # Stack rows
        row_names = [f"[row{i}]" for i in range(rows)]
        filter_complex.append(f"{''.join(row_names)}vstack=inputs={rows}")
        
        # Build command
        inputs = []
        for input_file in input_files:
            inputs.extend(["-i", input_file])
        
        duration_args = ["-t", duration] if duration else []
        
        command = [self.ffmpeg_path] + inputs + \
                 ["-filter_complex", ";".join(filter_complex)] + \
                 duration_args + [output_file]
        
        self._run_command(command)
        return output_file

    def create_picture_in_picture(self, main_video: str, pip_video: str, 
                                position: str = "bottom_right", scale: float = 0.3,
                                output_file: Optional[str] = None) -> str:
        """
        Create a picture-in-picture effect with two videos.

        Args:
            main_video (str): Path to main video file
            pip_video (str): Path to video to be shown as picture-in-picture
            position (str): Position of PiP ('top_left', 'top_right', 'bottom_left', 'bottom_right')
            scale (float): Scale factor for PiP video (0.0 to 1.0)
            output_file (Optional[str]): Path to output file. If None, appends "_pip" to main video filename

        Returns:
            str: Path to the output video file

        Example:
            >>> advanced_ops = AdvancedOperations()
            >>> pip = advanced_ops.create_picture_in_picture(
            ...     "main.mp4",
            ...     "small.mp4",
            ...     position="bottom_right",
            ...     scale=0.25
            ... )
            >>> print(f"PiP video saved as: {pip}")
        """
        self.validate_input_file(main_video)
        self.validate_input_file(pip_video)
        
        if output_file is None:
            name, ext = os.path.splitext(main_video)
            output_file = f"{name}_pip{ext}"
        
        self.ensure_output_dir(output_file)
        
        # Define position calculations
        position_map = {
            "top_left": "10:10",
            "top_right": "main_w-overlay_w-10:10",
            "bottom_left": "10:main_h-overlay_h-10",
            "bottom_right": "main_w-overlay_w-10:main_h-overlay_h-10"
        }
        
        if position not in position_map:
            raise ValueError(f"Invalid position. Must be one of: {', '.join(position_map.keys())}")
        
        filter_complex = [
            "[0:v]setpts=PTS-STARTPTS[main]",
            f"[1:v]scale=iw*{scale}:ih*{scale}[pip]",
            f"[main][pip]overlay={position_map[position]}"
        ]
        
        command = [
            self.ffmpeg_path,
            "-i", main_video,
            "-i", pip_video,
            "-filter_complex", ";".join(filter_complex),
            "-map", "0:a",
            output_file
        ]
        
        self._run_command(command)
        return output_file
