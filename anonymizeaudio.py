import os
import moviepy.editor as mp
import librosa
import soundfile as sf
import numpy as np

def anonymize_video_audio(input_path, steps=-3):
    """
    Takes a video, extracts audio, shifts pitch, and saves a new video
    in the same directory with '_anonymized' suffix.
    
    :param input_path: Full path to the video file
    :param steps: Number of semitones to shift (negative is lower/deeper)
    """
    
    # 1. Setup Paths
    directory, filename = os.path.split(input_path)
    name, ext = os.path.splitext(filename)
    temp_audio_path = os.path.join(directory, "temp_audio.wav")
    temp_shifted_path = os.path.join(directory, "temp_shifted.wav")
    output_path = os.path.join(directory, f"{name}_anonymized{ext}")

    print(f"Processing: {filename}...")

    try:
        # 2. Extract Audio from Video
        video = mp.VideoFileClip(input_path)
        video.audio.write_audiofile(temp_audio_path, logger=None)

        # 3. Load and Pitch Shift Audio using Librosa
        # Librosa loads as floating point time series
        y, sr = librosa.load(temp_audio_path, sr=None) 
        
        # Shift pitch (n_steps is semitones). 
        # -3 makes it deeper.
        y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)

        # 4. Save the modified audio temporarily
        sf.write(temp_shifted_path, y_shifted, sr)

        # 5. Combine new audio with original video
        new_audio = mp.AudioFileClip(temp_shifted_path)
        
        # Set the video audio to the new shifted audio
        final_video = video.set_audio(new_audio)
        
        # Write the result
        final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

        print(f"Success! Saved to: {output_path}")

    except Exception as e:
        print(f"Error processing video: {e}")

    finally:
        # 6. Cleanup: Remove temp files to keep folder clean
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if os.path.exists(temp_shifted_path):
            os.remove(temp_shifted_path)
        
        # Close the clips to release memory
        if 'video' in locals(): video.close()
        if 'new_audio' in locals(): new_audio.close()

# --- EXECUTION ---
if __name__ == "__main__":

    video_file = "testvideo.MOV" #has to be in same folder as this script
    
    # Print what we are doing so you know it started
    print(f"Looking for: {video_file}")

    if os.path.exists(video_file):
        # Run the function
        anonymize_video_audio(video_file, steps=-3)
    else:
        print(f"Could not find '{video_file}'. Make sure it is in the same folder as this script.")