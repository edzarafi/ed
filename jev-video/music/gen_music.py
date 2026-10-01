"""מוזיקת רקע מקורית, אמביינט-אלקטרונית (לה מינור, 100 BPM).

הרצה:  python gen_music.py <שניות> <קובץ_פלט.wav>"""
import sys, numpy as np, soundfile as sf
SR = 44100
dur = float(sys.argv[1]); out = sys.argv[2]
N = int(dur * SR); t = np.arange(N) / SR
bpm = 100; beat = 60 / bpm; bar = 4 * beat
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def midi(m): return 440 * 2 ** ((m - 69) / 12)
def env_adsr(n, a, d, s, r):
    e = np.ones(n) * s
    ai, di, ri = int(a*SR), int(d*SR), int(r*SR)
    e[:ai] = np.linspace(0, 1, ai); e[ai:ai+di] = np.linspace(1, s, di)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e
def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):  # מספיק טוב לצלילים קצרים
        acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y
def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR); j = min(N, i + len(sig))
    if i >= N: return
    s = sig[:j-i] * gain
    L[i:j] += s * np.sqrt((1 - pan) / 2) * 1.414 / 1.414
    R[i:j] += s * np.sqrt((1 + pan) / 2)

# אקורדים: Am, F, C, G (בתווי MIDI)
prog = [[57, 60, 64, 69], [53, 57, 60, 65], [55, 60, 64, 67], [55, 59, 62, 67]]
bass = [45, 41, 48, 43]
nbars = int(np.ceil(dur / bar))
# חישוב מראש של צלילי הפד (גלי מסור מעט מכוונים זה מזה, מסוננים ב-FFT לטובת מהירות)
def pad_chord(notes, length):
    n = int(length * SR); tt = np.arange(n) / SR; x = np.zeros(n)
    for m in notes:
        for det in (-0.12, 0.0, 0.11):
            f = midi(m) * 2 ** (det / 12)
            ph = rng.random()
            x += 2 * ((tt * f + ph) % 1) - 1
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1/SR)
    X *= 1 / (1 + (fr / 900) ** 4)
    x = np.fft.irfft(X, n)
    return x / np.abs(x).max() * env_adsr(n, 0.9, 0.5, 0.85, 1.0)

for b in range(nbars):
    st = b * bar; c = prog[b % 4]
    add(pad_chord(c, bar + 1.0), st, pan=0, gain=0.16)
    # סאב-בס: גל סינוס ארוך על הצליל הבסיסי
    n = int(bar * SR); tt = np.arange(n) / SR
    add(np.sin(2*np.pi*midi(bass[b % 4] - 12)*tt) * env_adsr(n, 0.02, 0.3, 0.7, 0.3), st, gain=0.22)
    section = b // 8
    # ארפג'ו אחרי תיבות הפתיחה
    if b >= 2:
        pattern = [0, 2, 1, 3, 2, 1, 3, 2]
        for k in range(8):
            m = c[pattern[k]] + 12
            n = int(0.5 * SR); tt = np.arange(n) / SR
            s = (np.sin(2*np.pi*midi(m)*tt) + 0.3*np.sin(4*np.pi*midi(m)*tt)) * np.exp(-tt * 9)
            add(s, st + k * beat / 2, pan=0.35 if k % 2 else -0.35, gain=0.10)
    # תופים מהתיבה הרביעית
    if b >= 4:
        for k in range(4):
            if k in (0, 2):
                n = int(0.35 * SR); tt = np.arange(n) / SR
                f = 50 + 90 * np.exp(-tt * 30)
                kick = np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-tt * 9)
                add(kick, st + k * beat, gain=0.33)
            if k in (1, 3):
                n = int(0.18 * SR); tt = np.arange(n) / SR
                clap = rng.standard_normal(n) * np.exp(-tt * 22)
                clap = np.diff(np.concatenate([[0], clap]))
                add(clap, st + k * beat, gain=0.06)
        for k in range(8):
            n = int(0.05 * SR); tt = np.arange(n) / SR
            hat = np.diff(np.concatenate([[0], rng.standard_normal(n)])) * np.exp(-tt * 80)
            add(hat, st + k * beat / 2 + beat / 4 * 0, pan=0.2, gain=0.035 if k % 2 else 0.02)

# דיליי סטריאו פשוט / תחושת חדר
for d, g in ((0.183, 0.25), (0.297, 0.18)):
    k = int(d * SR)
    L[k:] += R[:-k] * g; R[k:] += L[:-k] * g
mix = np.stack([L, R], 1)
fade_in, fade_out = int(1.5 * SR), int(4 * SR)
mix[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
mix[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None]
mix = np.tanh(mix * 1.2)
mix = mix / np.abs(mix).max() * 0.8
sf.write(out, mix.astype(np.float32), SR)
print("music", dur)
