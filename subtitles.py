#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import moviepy.editor as mp
import sys
import csv
import os


def add_subtitle_to_image(image, text, font_object, font_color):
    pil = Image.fromarray(image)
    draw = ImageDraw.Draw(pil)
    draw.text((30,30), text, font=font_object, color=font_color)
    return np.array(pil)


def add_subtitles_to_video(input_file, output_file,
                           output_width, output_height,
                           subtitles, font_object, font_color):
    try:
        capture = None
        writer = None
        
        capture = cv2.VideoCapture(input_file)
        input_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        input_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        input_fps = int(capture.get(cv2.CAP_PROP_FPS))
        num_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        writer = cv2.VideoWriter(output_file, fourcc, input_fps, (output_width, output_height))
        
        scale = min(output_width/input_width, output_height/input_height)
        
        for index_frames in range(num_frames):
            ret, input_frame = capture.read()
            if input_frame is None:
                break
            
            output_frame = np.zeros((output_height, output_width, 3), dtype=np.uint8)
            resized_frame = cv2.resize(input_frame, dsize=None, fx=scale, fy=scale)
            resized_height, resized_width = resized_frame.shape[:2]
        
            output_frame[-resized_height:, -resized_width:] = resized_frame
            
            lst = [text for (tim,text) in subtitles if tim <= index_frames/input_fps]
            if lst:
                output_frame = add_subtitle_to_image(output_frame, lst[-1], font_object, font_color)
            writer.write(output_frame)
    finally:
        if writer is not None:
            writer.release()
        if capture is not None:
            capture.release()


def copy_audio(input_file, subtitled_file, output_file, audio_file):
    clip_in = mp.VideoFileClip(input_file)
    clip_in.audio.write_audiofile(audio_file)
    
    clip_out = mp.VideoFileClip(subtitled_file)
    clip_out.write_videofile(output_file, audio=audio_file)
    

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("USAGE: python subtitles.py input_movie.mp4 subtitles.csv")
    else:
        input_file = sys.argv[1]
        subtitles_csv = sys.argv[2]
        subtitled_file = sys.argv[1]+".subtitled.mp4"
        output_file = sys.argv[1]+".output.mp4"
        audio_file = sys.argv[1]+".audio.mp3"
        
        output_width = 1280
        output_height = 720
        font_path = r"C:\Windows\Fonts\meiryo.ttc"
        font_size = 36
        font_color = (255, 255, 255, 0)
        
        with open(subtitles_csv) as fin:
            subtitles = []
            for row in csv.reader(fin):
                if row[0] == "output_width":
                    output_width = int(row[1])
                elif row[0] == "output_height":
                    output_height = int(row[1])
                elif row[0] == "font_path":
                    font_path = row[1]
                elif row[0] == "font_size":
                    font_size = int(row[1])
                elif row[0] == "font_color":
                    font_color = (int(row[1]), int(row[2]), int(row[3]), 0)
                else:
                    subtitles.append([float(row[0]), row[1]])
        
        font_object = ImageFont.truetype(font_path, font_size)
        
        print(output_width, output_height)
        print(subtitles)
        
        add_subtitles_to_video(input_file, subtitled_file,
                               output_width, output_height,
                               subtitles, font_object, font_color)
        copy_audio(input_file, subtitled_file, output_file, audio_file)
        
        if os.path.exists(subtitled_file):
            os.remove(subtitled_file)
        if os.path.exists(audio_file):
            os.remove(audio_file)

