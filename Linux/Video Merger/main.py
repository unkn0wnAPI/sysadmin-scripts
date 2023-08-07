#!/usr/bin/python3

#
## Script Name: FFmpeg video/audio merge
## Author:      unkn0wnAPI [https://github.com/unkn0wnAPI]
## Information: Merge separate audio/video files created by yt-dlp into one .mp4 file
#

#
## Imports
#
import argparse, os

#
## Functions
#
def argumentParser():
    argParser = argparse.ArgumentParser(description=f'Merge separate audio & video files created by yt-dlp into one', epilog="Written by unkn0wnAPI, part of sysadmin-scripts [https://github.com/unkn0wnapi/sysadmin-scripts]")
    argParser.add_argument('input_directory', type=str, help='Input directory')
    argParser.add_argument('--video-ext', '-v', action='store', dest='vext', default="mp4", help='Sets video file extension [defaults to mp4]')
    argParser.add_argument('--audio-ext', '-a', action='store', dest='aext', default="m4a", help='Sets audio file extension [defaults to m4a]')
    argParser.add_argument('--target-ext', '-e', action='store', dest='fext', default="mp4", help='Sets output file extension [defaults to mp4]')
    argParser.add_argument('--output', '-o', action='store', dest='od', default='.', help='Output directory [defaults to current working directory]')
    argParser.add_argument('--create-output-subdir', action='store_true', dest='sb', help='Creates sub-directory in the output location, based on the top-directory name from input path')
    return argParser.parse_args()

def ffmpeg_merger(input_video: str, input_audio: str, output_file: str):
    os.system(f'ffmpeg -i "{input_video}" -i "{input_audio}" -c copy "{output_file}" >/dev/null 2>&1')

#
## Script Start point
#
def main():
    args = argumentParser()
    INPUT_DIR = args.input_directory
    VIDEO_EXT = args.vext
    AUDIO_EXT = args.aext
    OUTPUT_DIR = args.od
    OUTPUT_EXT = args.fext

    if args.sb == True:
        if OUTPUT_DIR[-1] != '/':
            OUTPUT_DIR += '/'

        if INPUT_DIR[-1] == '/':
            OUTPUT_DIR += INPUT_DIR.split('/')[-2]
        else:
            OUTPUT_DIR += INPUT_DIR.split('/')[-1]
        
        os.mkdir(OUTPUT_DIR)
    
    INPUT_DIR = INPUT_DIR.removesuffix('/')
    OUTPUT_DIR = OUTPUT_DIR.removesuffix('/')

    FILES = os.listdir(INPUT_DIR)
    AUDIO_QUALITY = ""

    # Find audio quality suffix
    for file in FILES:
        file_name, file_ext = os.path.splitext(file)

        if file_ext == f".{AUDIO_EXT}" and AUDIO_QUALITY == "":
            AUDIO_QUALITY = (file_name[file_name.rfind('.'):]).replace('.', '')
            break
    
    # Main loop for matching audio and video files
    for file in FILES:
        file_name, file_ext = os.path.splitext(file)

        if file_ext != f".{VIDEO_EXT}":
            continue

        file_quality = file_name[file_name.rfind('.'):]
        file_name = file_name.replace(file_quality, '')
        
        video_fullname = f"{file_name}{file_quality}.{VIDEO_EXT}"
        audio_fullname = f"{file_name}.{AUDIO_QUALITY}.{AUDIO_EXT}"

        print(f"[FFMPEG] Merging {VIDEO_EXT} & {AUDIO_EXT} -> {file_name}.mp4")
        ffmpeg_merger(input_video=f"{INPUT_DIR}/{video_fullname}", input_audio=f"{INPUT_DIR}/{audio_fullname}", output_file=f"{OUTPUT_DIR}/{file_name}.{OUTPUT_EXT}")

if __name__ == "__main__":
    main()