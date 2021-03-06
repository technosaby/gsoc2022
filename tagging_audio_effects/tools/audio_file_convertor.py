#!/usr/bin/python
import getopt
import subprocess
import os
import sys
import shutil

"""
This file do the following
1. Parses the video files and extracts audio from the video files.
2. This will copy the folder structure with all videos and create similar folder structure with generated audio files.
3. It generates mono audio because YaMNet needs only mono.
4. It generates sampling rate of 16k based on YaMNet's requirements.
5. If the video contains seg files, this parser also copies them and put it in the audio folders.
"""


class AudioFileConvertor:
    def __init__(self):
        self.ffmpeg_cmd = "ffmpeg"

    def extract_audio(self, input_video_path_with_file_name, output_audio_file_with_file_name, output_ext, logs):
        """
        This file extracts a single audio file from a video file using ffmpeg

        :param input_video_path_with_file_name: The file path of a single video file
        :param output_audio_file_with_file_name: The file path in which the single audio file is generated
        :param output_ext: The output format of the audio file, default is wav
        :param logs: Decides whether logs should be enabled or not
        :return: None
        """
        subprocess.call(
            [self.ffmpeg_cmd, "-i", input_video_path_with_file_name, "-vn", "-f", output_ext, "-ar", "16000",
             "-ac", "1", output_audio_file_with_file_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        if logs:
            print("Input Video File " + input_video_path_with_file_name)
            print("Generation of audio files complete with filename ", output_audio_file_with_file_name)

    def extract_audio_files(self, video_input_folder_path, audio_output_folder_path,
                            output_ext, extra_file_extensions, logs=0):
        """
        This file takes a folder with multiple video files and generates audio files as inputs. The audio file
        generation will follow the same folder structure as that of the video file.

        :param video_input_folder_path: The path from which video files will be read
        :param audio_output_folder_path: The path in which audio files will be generated
        :param output_ext: The output format in which audio files need to be extracted, default is wav
        :param extra_file_extensions: Along with the audio file generation, if we want to copy extra files
        :param logs: Determines whether logs should be enabled
        :return: None
        """
        exclude_prefixes = ('__', '.')  # exclusion prefixes

        # # For input as a single file
        # if "." + video_file_extensions in video_input_folder_path:
        #     filename = os.path.splitext(video_input_folder_path)[0] + "." + output_ext
        #     self.extract_audio(os.path.join(audio_output_folder_path, video_input_folder_path),
        #                        os.path.join(audio_output_folder_path, filename), output_ext, logs)
        #     if seg_file_available:
        #         filename_seg = os.path.splitext(video_input_folder_path)[0] + "." + seg_file_extension
        #         shutil.copyfile(os.path.join(audio_output_folder_path, video_input_folder_path),
        #                     os.path.join(audio_output_folder_path, filename_seg))
        # # Only for directories as input
        # else:
        for dir_path, dir_names, filenames in os.walk(video_input_folder_path):
            # exclude all dirs starting with exclude_prefixes
            filenames = [f for f in filenames if not f[0] in exclude_prefixes]
            dir_names[:] = [d for d in dir_names if not d[0] in exclude_prefixes]
            output_structure = os.path.join(audio_output_folder_path, dir_path[len(video_input_folder_path):])
            input_structure = os.path.join(video_input_folder_path, dir_path[len(video_input_folder_path):])
            if not os.path.isdir(output_structure):
                os.mkdir(output_structure)
            # # Copy the .seg files from the same path as the video files and place it in along with the audio files
            for extra_file_extension in extra_file_extensions:
                for filename in [f for f in filenames if f.endswith("." + extra_file_extension)]:
                    input_file_name = os.path.join(input_structure, filename)
                    output_file_name = os.path.join(output_structure, filename)
                    shutil.copyfile(input_file_name, output_file_name)
            for filename in filenames:
                output_file_name = os.path.join(output_structure, filename)
                output_file_name = os.path.splitext(output_file_name)[0] + "." + output_ext
                input_file_name = os.path.join(input_structure, filename)
                self.extract_audio(input_file_name, output_file_name, output_ext, logs)


def process_args(argv):
    """
    Process arguments passed to the file
    :param argv: The arguments passed to the file
    :return: Returns the processed variables
    """
    arg_video_input = ""
    arg_audio_output = "."
    arg_output_audio_format = "wav"
    arg_logs = "0"

    arg_help = "{0} -i <video input path> -a <audio input format (default: wav)> -o <audio output path (default: .)> " \
               " -l <logs enabled (default 0) >".format(argv[0])
    try:
        opts, args = getopt.getopt(argv[1:], "hi:a:o:l:", ["help", "video input path=", "audio input format=",
                                                           "audio output path=", "logs="])
    except:
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-i", "--video input path"):
            arg_video_input = arg
        elif opt in ("-a", "--audio input format"):
            arg_audio_output = arg
        elif opt in ("-o", "--audio output path"):
            arg_output_audio_format = arg
        elif opt in ("-l", "--logs"):
            arg_logs = arg

    return arg_video_input, arg_audio_output, arg_output_audio_format, int(arg_logs)


if __name__ == '__main__':
    INPUT_VIDEO_PATH, OUTPUT_AUDIO_FORMAT, OUTPUT_AUDIO_PATH, LOGS = process_args(sys.argv)
    extra_file_extensions_for_copy = ["seg", "eaf"]
    audio_processor = AudioFileConvertor()
    print("Starting generation of audio files from ", INPUT_VIDEO_PATH, " to ", OUTPUT_AUDIO_PATH
          + " with format " + OUTPUT_AUDIO_FORMAT)
    audio_processor.extract_audio_files(INPUT_VIDEO_PATH, OUTPUT_AUDIO_PATH, OUTPUT_AUDIO_FORMAT,
                                        extra_file_extensions_for_copy, int(LOGS))
