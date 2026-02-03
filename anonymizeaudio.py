import os
import sys
import time
import cv2
import torch
import whisper
import spacy
import librosa
import soundfile as sf
import moviepy.editor as mp
from ultralytics import YOLO
import warnings

# Suppress annoying warnings
warnings.filterwarnings('ignore', message='PySoundFile failed.')
warnings.filterwarnings('ignore', category=FutureWarning)

# --- 1. SETTINGS & GLOBALS ---
TARGET_WIDTH = 640
TARGET_FPS = 15
last_boxes = []
frame_count = 0

# --- 2. YOLOv8 BLUR LOGIC ---
def blur_frame_yolo(frame, model):
    global last_boxes, frame_count
    h, w = frame.shape[:2]

    # SPEED: Only run AI detection every 5th frame (roughly 3x per second at 15fps)
    if frame_count % 5 == 0:
        # conf=0.4 is the "sweet spot" for medical environments
        results = model.predict(frame, conf=0.4, verbose=False, device=model.device)
        last_boxes = []
        for r in results:
            for box in r.boxes.xyxy:
                last_boxes.append(box.cpu().numpy().astype(int))
    
    frame_count += 1
    
    for (x1, y1, x2, y2) in last_boxes:
        # Medical Privacy: "Nose-Up" Blur (forehead to mid-nose)
        nose_cutoff = y1 + int((y2 - y1) * 0.5)
        
        # Ensure coordinates are within frame boundaries
        y_min, y_max = max(0, y1), min(h, nose_cutoff)
        x_min, x_max = max(0, x1), min(w, x2)
        
        roi = frame[y_min:y_max, x_min:x_max]
        if roi.size > 0:
            # Box blur is significantly faster than Gaussian
            frame[y_min:y_max, x_min:x_max] = cv2.blur(roi, (51, 51))
            
    return frame

# --- 3. AUDIO REDACTION LOGIC ---
def find_pii_intervals(whisper_result, spacy_model):
    doc = spacy_model(whisper_result['text'])
    target_labels = {'PERSON', 'ORG', 'GPE', 'LOC', 'DATE', 'TIME'}
    pii_words = {t.text.lower() for ent in doc.ents if ent.label_ in target_labels for t in ent}
    
    if pii_words:
        print(f"🔍 Redacting PII: {pii_words}")

    intervals = []
    for segment in whisper_result['segments']:
        for word_info in segment['words']:
            word_clean = word_info['word'].strip(" .,!?").lower()
            if word_clean in pii_words:
                intervals.append((word_info['start'], word_info['end']))
    return intervals

# --- 4. MASTER PIPELINE ---
def anonymize_video(input_path, nlp, whisper_ai, yolo_model):
    start_total = time.time()
    name, ext = os.path.splitext(input_path)
    output_path = f"{name}_yolo_anonymized.mp4"
    
    # Temporary working files
    temp_v = "temp_video_silent.mp4"
    temp_a_raw = "temp_audio_raw.wav"
    temp_a_mod = "temp_audio_final.wav"

    try:
        # --- STEP A: AUDIO (Whisper + Pitch Shift) ---
        print("🎙️ Processing Audio...")
        clip = mp.VideoFileClip(input_path)
        clip.audio.write_audiofile(temp_a_raw, fps=16000, logger=None)
        
        res = whisper_ai.transcribe(temp_a_raw, word_timestamps=True, fp16=False)
        mute_times = find_pii_intervals(res, nlp)
        
        y, sr = librosa.load(temp_a_raw, sr=16000)
        for s, e in mute_times:
            y[int(s*sr):int(e*sr)] = 0.0
            
        print("🎵 Applying Pitch Shift (-3 steps)...")
        y_shift = librosa.effects.pitch_shift(y, sr=sr, n_steps=-3)
        sf.write(temp_a_mod, y_shift, sr)

        # --- STEP B: VIDEO (OpenCV Turbo) ---
        cap = cv2.VideoCapture(input_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        orig_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        orig_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        target_h = int(orig_h * (TARGET_WIDTH / orig_w))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_v, fourcc, TARGET_FPS, (TARGET_WIDTH, target_h))

        print(f"🎬 Anonymizing {total_frames} frames with YOLOv8...")
        f_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            # Reduce FPS from ~30 to 15 to cut workload in half
            if f_idx % 2 == 0:
                frame = cv2.resize(frame, (TARGET_WIDTH, target_h))
                blurred = blur_frame_yolo(frame, yolo_model)
                out.write(blurred)
            
            f_idx += 1
            if f_idx % 100 == 0:
                print(f"  > Progress: {f_idx}/{total_frames} frames")

        cap.release()
        out.release()

        # --- STEP C: FINAL MERGE ---
        print("💾 Merging Resulting Video & Audio...")
        final_v = mp.VideoFileClip(temp_v)
        final_a = mp.AudioFileClip(temp_a_mod)
        final_v.set_audio(final_a).write_videofile(
            output_path, 
            codec='libx264', 
            audio_codec='aac', 
            preset='ultrafast', 
            logger=None
        )

        print(f"\n✅ Pipeline Complete in {time.time() - start_total:.2f}s")
        print(f"📁 Saved to: {output_path}")

    except Exception as e:
        print(f"❌ Pipeline Error: {e}")
    finally:
        # Cleanup
        for f in [temp_v, temp_a_raw, temp_a_mod]:
            if os.path.exists(f): os.remove(f)

if __name__ == "__main__":
    print("🚀 Initializing AI Models...")
    nlp_model = spacy.load("en_core_web_lg")
    whisper_model = whisper.load_model("base")
    
    # Check for Mac GPU
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"⚙️ Using Device: {dev.upper()}")
    
    # Load YOLOv8-Face (Nano version)
    # The '.pt' file will auto-download on first run
    yolo = YOLO("yolov8n-face.pt") 
    
    target_video = "testshortsimul.mp4"
    if os.path.exists(target_video):
        anonymize_video(target_video, nlp_model, whisper_model, yolo)
    else:
        print(f"❌ Error: {target_video} not found.")