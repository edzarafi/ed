"""מתמלל קבצי שמע בעזרת Whisper (sherpa-onnx), כדי לבדוק שהקריינות מובנת.

הרצה:  .venv/bin/python asr.py קובץ1.wav [קובץ2.wav ...]"""
import sys, sherpa_onnx, soundfile as sf, numpy as np
d="sherpa-onnx-whisper-small/"
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=d+"small-encoder.int8.onnx", decoder=d+"small-decoder.int8.onnx", tokens=d+"small-tokens.txt", language="he", task="transcribe", num_threads=4)
for f in sys.argv[1:]:
    a, sr = sf.read(f, dtype="float32")
    if a.ndim>1: a=a.mean(1)
    if sr!=16000:
        import math
        n=int(len(a)*16000/sr); a=np.interp(np.linspace(0,len(a)-1,n),np.arange(len(a)),a).astype(np.float32)
    s=rec.create_stream(); s.accept_waveform(16000,a); rec.decode_stream(s)
    print(f, "=>", s.result.text)
