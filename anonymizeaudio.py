import os
import moviepy.editor as mp
import librosa
import soundfile as sf
import numpy as np
import whisper
import spacy
import cv2                
import mediapipe as mp_face 
import warnings

# Suppress a specific UserWarning from librosa/soundfile
warnings.filterwarnings('ignore', message='PySoundFile failed. Trying audioread instead.')

# --- REVISED FUNCTION (FIX 2): Handle read-only frames ---
def blur_frame(frame, face_detector):
    """
    Takes a single video frame (as RGB) and blurs ALL faces found
    using the MediaPipe FaceDetection model. Handles read-only frames
    from moviepy.
    """
    
    # 1. Create a writeable copy of the frame immediately.
    #    The frame from moviepy is read-only, but MediaPipe
    #    needs a writeable array. .copy() solves this.
    frame_copy = frame.copy() 

    # 2. Process the writeable copy
    #    (We no longer need to toggle frame.flags.writeable)
    results_face = face_detector.process(frame_copy)
    
    # 3. If no faces, return the ORIGINAL frame (which is untouched)
    if not results_face.detections:
        return frame 

    # We will apply blur TO the frame_copy and return it.
    ih, iw, _ = frame_copy.shape
    
    # Loop through all detected faces
    for detection in results_face.detections:
        # Get the relative bounding box
        bbox_rel = detection.location_data.relative_bounding_box
        if not bbox_rel:
            continue
            
        x_min_rel = bbox_rel.xmin
        y_min_rel = bbox_rel.ymin
        width_rel = bbox_rel.width
        height_rel = bbox_rel.height
        
        # --- Apply padding (Using your original 100% padding logic) ---
        width_padding = width_rel * .4
        height_padding = height_rel * .6
        
        x_min_new_rel = x_min_rel - (width_padding / 2)
        y_min_new_rel = y_min_rel - (height_padding / 2)
        width_new_rel = width_rel + width_padding
        height_new_rel = height_rel + height_padding
        
        # Convert padded coordinates to pixel values
        x, y, w, h = int(x_min_new_rel * iw), int(y_min_new_rel * ih), \
                     int(width_new_rel * iw), int(height_new_rel * ih)
        # --- End Padding ---

        # Ensure coordinates are valid (clamping)
        x, y = max(0, x), max(0, y)
        x_end = min(iw, x + w)
        y_end = min(ih, y + h)
        
        # Recalculate w and h based on clamping
        w = x_end - x
        h = y_end - y

        # 1. Extract the region of interest (ROI)
        if w <= 0 or h <= 0:
            continue # Skip if box is off-screen
                
        face_roi = frame_copy[y:y_end, x:x_end] # Get ROI from the copy
        
        # 2. Apply a heavy Gaussian blur
        blurred_face = cv2.GaussianBlur(face_roi, (99, 99), 90)
        
        # 3. Put the blurred face back into the copy
        frame_copy[y:y_end, x:x_end] = blurred_face
    
    # 4. Return the modified, blurred copy
    return frame_copy
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

# --- REVISED FUNCTION (Accepts FaceDetector) ---
def anonymize_video(input_path, spacy_model, whisper_model, face_detector, steps=-3):
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
        if video.rotation in (90, 270):
            print(f"Detected rotation tag ({video.rotation}). Resizing to vertical...")
            video = video.resize(video.size[::-1]) # Swap w/h
            video.rotation = 0 
        else:
            print(f"Video is standard {video.w}x{video.h}. No resize needed.")
        video.audio.write_audiofile(temp_audio_path, logger=None)

        # 3. HIPAA Step 1: Transcribe (Whisper)
        print("Transcribing audio with Whisper...")
        whisper_result = whisper_model.transcribe(temp_audio_path, word_timestamps=True, fp16=False, language='en')

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
        
        # --- CHANGED: We pass FaceDetector ---
        final_video_blurred = final_video.fl_image(
            lambda frame: blur_frame(frame, face_detector) # Pass face_detector
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


# --- REVISED EXECUTION (Loads FaceDetection) ---
if __name__ == "__main__":
    
    # Load the AI models ONCE when the script starts
    print("Loading all AI models into memory...")
    try:
        # --- USE THE 'lg' MODEL FOR BEST PII DETECTION ---
        spacy_nlp = spacy.load("en_core_web_lg")
        whisper_model = whisper.load_model("base")
        
        # -----------------------------------------------------------------
        # --- THIS IS THE FIX: Load FaceDetection instead of Pose ---
        
        mp_face_detection = mp_face.solutions.face_detection
        face_detector = mp_face_detection.FaceDetection(
            min_detection_confidence=0.01  # 0.5 is a good, stable default
        )
        # We have removed the Pose detector as it's not needed for blurring
        # -----------------------------------------------------------------
        
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading AI models: {e}")
        print("Please ensure you have run:")
        print("1. python -m pip install spacy openai-whisper opencv-python mediapipe")
        print("2. python -m spacy download en_core_web_lg") # Make sure 'lg' is downloaded
        exit()

    video_file = "testvidGDG.MOV" #has to be in same folder as this script
    
    print(f"Looking for: {video_file}")
    if os.path.exists(video_file):
        # Run the master function, passing in all loaded models
        # --- CHANGED: Pass face_detector ---
        anonymize_video(
            video_file, 
            spacy_model=spacy_nlp, 
            whisper_model=whisper_model, 
            face_detector=face_detector, # Pass the correct detector
            steps=-3
        )
    else:
        print(f"Could not find '{video_file}'. Make sure it is in the same folder as this script.")