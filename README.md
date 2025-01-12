# mb_ffmpeg

A comprehensive Python package providing an object-oriented interface to FFmpeg operations, from basic to advanced functionalities.

## Features

- **Basic Operations**
  - Format conversion
  - Media trimming
  - Frame extraction
  - Resolution changes
  - Video compression

- **Audio Operations**
  - Audio extraction
  - Volume adjustment
  - Audio normalization
  - Fade effects
  - Audio mixing

- **Video Operations**
  - Video cropping
  - Watermark addition
  - Text overlay
  - Custom filter application
  - GIF creation

- **Advanced Operations**
  - Video concatenation with transitions
  - HLS streaming preparation
  - Complex filter graphs
  - Video wall creation
  - Picture-in-Picture effects

## Installation

```bash
pip install mb_ffmpeg
```

**Requirements:**
- Python 3.6+
- FFmpeg installed and accessible in system PATH

## Usage Examples

### Basic Operations

```python
from mb_ffmpeg.basic_ops import BasicOperations

# Initialize basic operations
basic = BasicOperations()

# Convert video format
converted = basic.convert_format("input.avi", "mp4")

# Trim video
trimmed = basic.trim_media("input.mp4", "00:00:30", "00:01:00")

# Extract frames
frames_dir = basic.extract_frames("input.mp4", fps=1)  # 1 frame per second

# Change resolution
resized = basic.change_resolution("input.mp4", (1280, 720))

# Compress video
compressed = basic.compress_video("input.mp4", crf=23)

# Video info
info = basic.video_info("input.mp4")
```

### Audio Operations

```python
from mb_ffmpeg.audio_ops import AudioOperations

# Initialize audio operations
audio = AudioOperations()

# Extract audio from video
audio_file = audio.extract_audio("video.mp4", "mp3")

# Adjust volume
louder = audio.change_volume("input.mp3", 1.5)  # 50% louder

# Normalize audio
normalized = audio.normalize_audio("input.mp3", target_level=-16.0)

# Add fade effects
with_fade = audio.apply_fade("input.mp3", fade_in=2.0, fade_out=3.0)

# Mix multiple audio files
mixed = audio.mix_audio(
    ["voice.mp3", "background.mp3"],
    "mixed.mp3",
    weights=[1.0, 0.5]
)
```

### Video Operations

```python
from mb_ffmpeg.video_ops import VideoOperations

# Initialize video operations
video = VideoOperations()

# Crop video
cropped = video.crop_video("input.mp4", 1280, 720, 0, 140)

# Add watermark
watermarked = video.add_watermark(
    "input.mp4",
    "logo.png",
    position="bottom_right",
    opacity=0.3
)

# Add text overlay
with_text = video.add_text(
    "input.mp4",
    "Hello World",
    position="bottom",
    font_size=32,
    color="yellow"
)

# Create GIF
gif = video.create_gif(
    "input.mp4",
    start_time="00:00:10",
    duration="5",
    fps=15,
    scale=480
)

change_aspect = video.change_aspect_ratio(
    "input.mp4",
    "9:16",
    "output.mp4",
)
```

### Advanced Operations

```python
from mb_ffmpeg.advanced_ops import AdvancedOperations

# Initialize advanced operations
advanced = AdvancedOperations()

# Concatenate videos with transition
merged = advanced.concat_videos(
    ["part1.mp4", "part2.mp4", "part3.mp4"],
    "merged.mp4",
    transition="dissolve",
    transition_duration=0.5
)

# Create streaming variants
master_playlist = advanced.create_streaming_variant(
    "input.mp4",
    "stream",
    [(1920, 1080), (1280, 720), (854, 480)],
    segment_duration=4
)

# Create video wall
wall = advanced.create_video_wall(
    ["video1.mp4", "video2.mp4", "video3.mp4", "video4.mp4"],
    (2, 2),
    "video_wall.mp4"
)

# Create picture-in-picture effect
pip = advanced.create_picture_in_picture(
    "main.mp4",
    "small.mp4",
    position="bottom_right",
    scale=0.25
)
```
