import os
import moviepy.editor as mp
import librosa
import soundfile as sf
import numpy as np
import whisper
import spacy
import cv2                # <--- NEW (OpenCV for blurring)
import mediapipe as mp_face # <--- NEW (MediaPipe for face detection)
import warnings

# Suppress a specific UserWarning from librosa/soundfile
warnings.filterwarnings('ignore', message='PySoundFile failed. Trying audioread instead.')

# --- REVISED FUNCTION: Head Blurring (replaces blur_frame) -----------------
def blur_frame(frame, pose_detector):
    """
    Takes a single video frame (NumPy array) and blurs the entire head.
    """
    frame = frame.copy()
    # Process the frame and find the pose
    results = pose_detector.process(frame)
    
    # If no pose is found, return the original frame
    if not results.pose_landmarks:
        return frame

    # --- We found a pose, now find the head ---
    landmarks = results.pose_landmarks.landmark
    ih, iw, _ = frame.shape
    
    # We will build a box around key head landmarks
    # Indices 0-10 are (Nose, Eyes, Ears, Mouth)
    head_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    x_coords = []
    y_coords = []
    
    # Find all visible head landmarks
    for i in head_indices:
        landmark = landmarks[i]
        # Check if the landmark is on-screen and visible
        if landmark.visibility > 0.3 and 0 <= landmark.x <= 1 and 0 <= landmark.y <= 1:
            x_coords.append(landmark.x)
            y_coords.append(landmark.y)

    # If no head landmarks were visible, return
    if not x_coords or not y_coords:
        return frame

    # Find the min/max coordinates to create a bounding box
    x_min_rel, x_max_rel = min(x_coords), max(x_coords)
    y_min_rel, y_max_rel = min(y_coords), max(y_coords)
    
    # --- Apply padding (like before, but to our new box) ---
    width_rel = x_max_rel - x_min_rel
    height_rel = y_max_rel - y_min_rel
    
    width_padding = width_rel * 1.2
    height_padding = height_rel * 2
    
    x_min_new = x_min_rel - (width_padding / 2)
    y_min_new = y_min_rel - (height_padding / 2)
    width_new = width_rel + width_padding
    height_new = height_rel + height_padding
    
    # Convert padded coordinates to pixel values
    x, y, w, h = int(x_min_new * iw), int(y_min_new * ih), \
                 int(width_new * iw), int(height_new * ih)
    # --- End Padding ---

    # Ensure coordinates are valid
    x, y = max(0, x), max(0, y)
    w, h = min(iw - x, w), min(ih - y, h)

    # 1. Extract the region of interest (ROI)
    if w <= 0 or h <= 0:
        return frame
            
    face_roi = frame[y:y+h, x:x+w]
    
    # 2. Apply a heavy Gaussian blur
    blurred_face = cv2.GaussianBlur(face_roi, (99, 99), 30)
    
    # 3. Put the blurred face back into the frame
    frame[y:y+h, x:x+w] = blurred_face
    
    return frame
# --------------------------------------------------------------------------

def find_pii_intervals(whisper_result, spacy_model):
    """
    Analyzes a Whisper transcript with spaCy to find PII
    and returns a list of time intervals to mute.
    """
    full_text = whisper_result['text']
    print("Analyzing transcript with spaCy NER...")
    doc = spacy_model(full_text)
    
    target_labels = {'PERSON', 'ORG', 'GPE', 'LOC', 'DATE', 'TIME'}
    
    pii_words = set()
    for ent in doc.ents:
        if ent.label_ in target_labels:
            for token in ent:
                pii_words.add(token.text.lower())
                
    if pii_words:
        print(f"AI identified these sensitive words to redact: {pii_words}")
    else:
        print("AI found no sensitive PII words.")

    mute_intervals = []
    for segment in whisper_result['segments']:
        for word_info in segment['words']:
            clean_word = word_info['word'].strip(" .,!?").lower()
            if clean_word in pii_words:
                print(f"Redacting '{clean_word}' at {word_info['start']}s")
                mute_intervals.append((word_info['start'], word_info['end']))
                
    return mute_intervals

def redact_audio(y, sr, intervals):
    """
    Overwrites specific time intervals in the audio array with silence (0.0).
    """
    if not intervals:
        return y
        
    print(f"Redacting {len(intervals)} audio segments...")
    y_redacted = y.copy()
    for start_time, end_time in intervals:
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)
        y_redacted[start_sample:end_sample] = 0.0
        
    return y_redacted

def anonymize_video(input_path, spacy_model, whisper_model, pose_detector, steps=-3):
    """
    Full Pipeline: Extract -> Transcribe -> Find PII -> Redact -> Pitch Shift -> Blur -> Save
    """
    # 1. Setup Paths
    directory, filename = os.path.split(input_path)
    name, ext = os.path.splitext(filename)
    temp_audio_path = os.path.join(directory, "temp_audio.wav")
    temp_shifted_path = os.path.join(directory, "temp_shifted.wav")
    output_path = os.path.join(directory, f"{name}_anonymized{ext}")

    print(f"Processing: {filename}...")
    video = None
    new_audio = None
    
    try:
        # --- AUDIO PIPELINE ---
        
        # 2. Extract Audio
        video = mp.VideoFileClip(input_path)
        # Case 1: Metadata is correct (rotation tag is 90 or 270)
        if video.rotation in (90, 270):
            print("Detected rotation tag. Resizing to vertical...")
            video = video.resize(video.size[::-1]) # Swap w/h
            video.rotation = 0 
        # Case 2: Metadata is missing/wrong
        elif video.w > video.h and video.rotation in (0, None):
            print("Detected wide video with no/wrong rotation tag. Forcing vertical resize...")
            video = video.resize((video.h, video.w))
        video.audio.write_audiofile(temp_audio_path, logger=None)

        # 3. HIPAA Step 1: Transcribe (Whisper)
        print("Transcribing audio with Whisper...")
        whisper_result = whisper_model.transcribe(temp_audio_path, word_timestamps=True, fp16=False)

        # 4. HIPAA Step 2: Find PII (spaCy)
        mute_times = find_pii_intervals(whisper_result, spacy_model)

        # 5. Load Audio for Processing
        y, sr = librosa.load(temp_audio_path, sr=None) 

        # 6. Apply Redaction (Silence the PII)
        y = redact_audio(y, sr, mute_times)

        # 7. Apply Pitch Shift (Anonymize Voice)
        print("Applying pitch shift...")
        y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)

        # 8. Save Anonymized Audio
        print("Saving new audio...")
        sf.write(temp_shifted_path, y_shifted, sr)
        new_audio = mp.AudioFileClip(temp_shifted_path)
        
        # --- VIDEO PIPELINE ---

        # 9. Set the new audio to the original video clip
        final_video = video.set_audio(new_audio)
        
        # 10. Apply Facial Blurring (MediaPipe)
        print("Applying facial blurring (this is the slowest step)...")
        
        # --- CHANGED: We pass the 'pose_detector' ---
        final_video_blurred = final_video.fl_image(
            lambda frame: blur_frame(frame, pose_detector)
        )
        # ---
        
        # 11. Write the final, combined file
        print("Stitching final video file...")
        final_video_blurred.write_videofile(
            output_path, 
            codec='libx264', 
            audio_codec='aac', 
            logger=None, 
            bitrate='10M'
        )

        print(f"Success! Saved to: {output_path}")

    except Exception as e:
        print(f"Error processing video: {e}")

    finally:
        # 12. Cleanup
        if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
        if os.path.exists(temp_shifted_path): os.remove(temp_shifted_path)
        if video: video.close()
        if new_audio: new_audio.close()


# --- EXECUTION ---
if __name__ == "__main__":
    
    # Load the AI models ONCE when the script starts
    print("Loading all AI models into memory...")
    try:
        # --- USE THE 'lg' MODEL FOR BEST PII DETECTION ---
        spacy_nlp = spacy.load("en_core_web_lg")
        whisper_model = whisper.load_model("base")
        
        # -----------------------------------------------------------------
        # --- THIS IS THE CHANGE: Load Pose model, not Face model ---
        mp_pose = mp_face.solutions.pose
        pose_detector = mp_pose.Pose(
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5
        )
        # -----------------------------------------------------------------
        
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading AI models: {e}")
        print("Please ensure you have run:")
        print("1. python -m pip install spacy openai-whisper opencv-python mediapipe")
        print("2. python -m spacy download en_core_web_lg") # Make sure 'lg' is downloaded
        exit()

    video_file = "test2video.MOV" #has to be in same folder as this script
    
    print(f"Looking for: {video_file}")
    if os.path.exists(video_file):
        # Run the master function, passing in all loaded models
        # --- CHANGED: Pass 'pose_detector' ---
        anonymize_video(
            video_file, 
            spacy_model=spacy_nlp, 
            whisper_model=whisper_model, 
            pose_detector=pose_detector,
            steps=-3
        )
    else:
        print(f"Could not find '{video_file}'. Make sure it is in the same folder as this script.")