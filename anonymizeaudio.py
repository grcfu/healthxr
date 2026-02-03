import os
import sys
import time
import moviepy.editor as mp
import librosa
import soundfile as sf
import numpy as np
import whisper
import spacy
import cv2
import torch
import warnings

# --- 1. EGOBLUR PATH LINKING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
paths_to_add = [
    os.path.join(BASE_DIR, "EgoBlur"),
    os.path.join(BASE_DIR, "EgoBlur", "egoblur")
]
for p in paths_to_add:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from egoblur.interface import DetectorIterative
    print("✅ EgoBlur Engine Linked Successfully.")
except ImportError as e:
    print(f"❌ Error linking EgoBlur: {e}")
    sys.exit()

warnings.filterwarnings('ignore', message='PySoundFile failed.')

# Global variables for frame skipping
last_detections = []
frame_count = 0

def blur_frame_egoblur(frame, detector):
    global last_detections, frame_count
    h, w = frame.shape[:2]
    
    # --- SPEED: Think every 15 frames (1x per second) ---
    if frame_count % 15 == 0:
        scale = 160 / w 
        small_frame = cv2.resize(frame, (160, int(h * scale)))
        last_detections = detector.predict(small_frame)
        last_detections = [[int(c / scale) for c in box] for box in last_detections]
    
    frame_count += 1
    if not last_detections:
        return frame

    for box in last_detections:
        x1, y1, x2, y2 = box
        h_half = int((y2 - y1) / 2)
        y_end = min(h, y1 + h_half)
        
        roi = frame[max(0, y1):y_end, max(0, x1):min(w, x2)]
        if roi.size > 0:
            # Fast Box Blur
            frame[max(0, y1):y_end, max(0, x1):min(w, x2)] = cv2.blur(roi, (51, 51))
            
    return frame

# --- 3. AI AUDIO PII IDENTIFICATION ---
def find_pii_intervals(whisper_result, spacy_model):
    doc = spacy_model(whisper_result['text'])
    target_labels = {'PERSON', 'ORG', 'GPE', 'LOC', 'DATE', 'TIME'}
    pii_words = {t.text.lower() for ent in doc.ents if ent.label_ in target_labels for t in ent}
    
    intervals = []
    for segment in whisper_result['segments']:
        for word_info in segment['words']:
            word_clean = word_info['word'].strip(" .,!?").lower()
            if word_clean in pii_words:
                intervals.append((word_info['start'], word_info['end']))
    return intervals

# --- 4. MASTER PROCESSING PIPELINE ---
def anonymize_video(input_path, spacy_model, whisper_model, ego_detector):
    start_time = time.time()
    name, ext = os.path.splitext(input_path)
    output_path = f"{name}_anonymized.mp4"
    temp_a, temp_s = "temp_audio_raw.wav", "temp_audio_mod.wav"
    temp_v = "temp_no_audio.mp4"

    try:
        # Step A: Audio Processing
        print("🎙️ Processing Audio (Whisper + Pitch Shift)...")
        video_clip = mp.VideoFileClip(input_path)
        video_clip.audio.write_audiofile(temp_a, fps=16000, logger=None)
        
        res = whisper_model.transcribe(temp_a, word_timestamps=True, fp16=False)
        mute_times = find_pii_intervals(res, spacy_model)
        
        y, sr = librosa.load(temp_a, sr=16000)
        for s, e in mute_times:
            y[int(s*sr):int(e*sr)] = 0.0
        y_shift = librosa.effects.pitch_shift(y, sr=sr, n_steps=-3)
        sf.write(temp_s, y_shift, sr)

        # Step B: Fast Video Loop (OpenCV)
        print("🎬 Processing Video via OpenCV (Turbo Mode)...")
        cap = cv2.VideoCapture(input_path)
        orig_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Target: 640p at 15fps
        target_w = 640
        target_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * (target_w / cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_v, fourcc, 15, (target_w, target_h))

        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            # Process every 2nd frame to drop FPS to ~15
            if frame_idx % 2 == 0:
                frame = cv2.resize(frame, (target_w, target_h))
                blurred_frame = blur_frame_egoblur(frame, ego_detector)
                out.write(blurred_frame)
            
            frame_idx += 1
            if frame_idx % 50 == 0:
                print(f"  > Processed {frame_idx}/{total_frames} frames...")

        cap.release()
        out.release()

        # Step C: Final Merge
        print("💾 Merging Result...")
        final_v = mp.VideoFileClip(temp_v)
        final_a = mp.AudioFileClip(temp_s)
        final_v.set_audio(final_a).write_videofile(
            output_path, 
            codec='libx264', 
            preset='ultrafast', 
            logger=None
        )

        print(f"\n✅ Pipeline Complete in {time.time() - start_time:.2f}s")

    except Exception as e:
        print(f"❌ Pipeline Error: {e}")
    finally:
        for f in [temp_a, temp_s, temp_v]:
            if os.path.exists(f): os.remove(f)

if __name__ == "__main__":
    print("🚀 Initializing AI Models...")
    nlp = spacy.load("en_core_web_lg")
    whisper_ai = whisper.load_model("base")
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    detector = DetectorIterative(model_path="ego_blur_face.jit", device=dev)
    
    target_video = "testshortsimul.mp4"
    if os.path.exists(target_video):
        anonymize_video(target_video, nlp, whisper_ai, detector)
    else:
        print(f"❌ Error: {target_video} not found.")