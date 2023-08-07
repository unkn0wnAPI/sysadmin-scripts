# Video Merger

This is a script that automates the task of merging separate video & audio files that were created by yt-dlp.

## Getting Started

The scripts is very basics and does not required additional software/packages (other than the ones that are stated in the [Prerequisites](#prerequisites)).

### Prerequisites

Tools and elements required to successfully use the script:

* [FFmpeg](https://ffmpeg.org/) installed on your machine;
  * On arch based systems: `pacman -S ffmpeg`
  * On debian based systems: `apt install ffmpeg`
* [Python 3](https://www.python.org/) installed your the machine.

## Configuration

The script use `argparse` allows users to tweak the following script parameters:

| Script argument           | Description                                                         | Default Value |
| ------------------------- | ------------------------------------------------------------------- | ------------- |
| `--video-ext/-v`          | Sets the input video file extension                                 | mp4           |
| `--audio-ext/-a`          | Sets the input audio file extension                                 | m4a           |
| `--target-ext/-e`         | Sets the output file extension                                      | mp4           |
| `--output/-o`             | Sets the output location                                            | Working dir   |
| `--create-output-subdir`  | Creates sub-dir in the output location, based on the input dir name | False         |

Detailed information can be found by running script with `-h` flag.

## Usage

To run this script you need to issue the following command script directory:

```properties
./main.py <options> <input_directory>
# or
python3 main.py <options> <input_directory>
```

Disclaimer: **IT IS IMPORTANT THAT THE VIDEO/AUDIO FILES ARE NAMED LIKE THIS -> video_name.quality.file_extension**
