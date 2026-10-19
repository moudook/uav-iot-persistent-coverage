"""
Synthesized 'Billie Jean'-style bassline groove as a wake-up alarm.
The original recording is copyrighted, so this is an original synthesized
tribute to the bassline pattern rather than the song.
"""
import numpy as np, wave, struct, sys, winsound, time, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SR = 44100
BPM = 117
BEAT = 60.0 / BPM
STEP = BEAT / 4.0          # 16th note
BARS = 8
steps = BARS * 16
dur = steps * STEP + 1.0
n = int(SR * dur)
buf = np.zeros(n, dtype=np.float64)

def env(i, a, d, s, r, sus):
    """simple ADSR over sample index i"""
    if i < a:  return i / a
    if i < a + d: return 1.0 - (1.0 - sus) * (i - a) / d
    if i < a + d + s: return sus
    if i < a + d + s + r: return sus * (1.0 - (i - a - d - s) / r)
    return 0.0

def add(start_s, sig):
    i0 = int(start_s * SR)
    k = min(len(sig), n - i0)
    if k > 0:
        buf[i0:i0 + k] += sig[:k]

# ---- bassline: the driving 16th-note octave pattern -----------------------
ROOT = 82.41                      # E2
MID = ROOT * 2                    # E3
P = [0,0,0,-1, 0,0,0,-1, 0,0,0,-1, 0,0,3,-1]   # semitone offsets, -1 = rest

def bass(f, t, dur_, gain=0.55):
    L = int(SR * dur_)
    i = np.arange(L)
    # saw-ish: odd harmonics with decaying amplitude
    y = np.zeros(L)
    for h in range(1, 13):
        if f * h > SR / 2: break
        y += np.sin(2 * np.pi * f * h * i / SR) / h
    y *= 0.55
    # pluck envelope: fast attack, exponential decay
    e = np.exp(-i / (0.055 * SR))
    a = np.minimum(1.0, i / (0.003 * SR))
    return (y * e * a * gain).astype(np.float64)

for s in range(steps):
    semi = P[s % 16]
    if semi < 0: continue
    f = ROOT * (2 ** (semi / 12.0))
    if s % 2 == 0 or semi == 3:
        add(s * STEP, bass(f, None, STEP * 0.95, 0.60))

# ---- kick ----------------------------------------------------------------
def kick(gain=0.85):
    L = int(0.30 * SR)
    i = np.arange(L)
    f = 118 * np.exp(-i / (0.030 * SR)) + 44
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-i / (0.10 * SR)) * gain).astype(np.float64)

# ---- snare ---------------------------------------------------------------
def snare(gain=0.34):
    L = int(0.20 * SR)
    i = np.arange(L)
    noise = np.random.RandomState(7).randn(L)
    e = np.exp(-i / (0.055 * SR))
    tone = np.sin(2 * np.pi * 190 * i / SR) * 0.4
    return ((noise * 0.8 + tone) * e * gain).astype(np.float64)

# ---- hat -----------------------------------------------------------------
def hat(gain=0.14):
    L = int(0.05 * SR)
    i = np.arange(L)
    noise = np.random.RandomState(3).randn(L)
    hp = np.diff(noise, prepend=0.0) * 0.6
    return (hp * np.exp(-i / (0.010 * SR)) * gain).astype(np.float64)

for s in range(steps):
    t = s * STEP
    if s % 8 == 0 or s % 8 == 6: add(t, kick())
    if s % 8 == 4:                   add(t, snare())
    if s % 2 == 0:                   add(t, hat())

# ---- the signature synth stab on the "and-2" ---------------------------
def stab(f, dur_, gain=0.20):
    L = int(SR * dur_)
    i = np.arange(L)
    y = np.zeros(L)
    for h, amp in [(1, 1.0), (2, 0.5), (3, 0.3), (4, 0.18), (6, 0.1)]:
        y += amp * np.sin(2 * np.pi * f * h * i / SR)
    e = np.exp(-i / (0.16 * SR))
    a = np.minimum(1.0, i / (0.006 * SR))
    return (y / 4.2 * e * a * gain).astype(np.float64)

CHORD = [329.63, 392.00, 493.88]     # E major voicing
for bar in range(BARS):
    add(bar * 4 * BEAT + 2 * BEAT, stab(CHORD[0], 0.9))
    add(bar * 4 * BEAT + 2 * BEAT, stab(CHORD[1], 0.9))
    add(bar * 4 * BEAT + 2 * BEAT, stab(CHORD[2], 0.9))

# ---- master: soft clip + normalize --------------------------------------
buf = np.tanh(buf * 1.25) * 0.92
peak = np.max(np.abs(buf))
if peak > 0: buf = buf / peak * 0.95

# short fade out
f = int(0.25 * SR)
buf[-f:] *= np.linspace(1, 0, f)

pcm = (buf * 32767).astype(np.int16)
path = os.path.abspath('wakeup_groove.wav')
w = wave.open(path, 'wb')
w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(pcm.tobytes()); w.close()

print(f'generated {path}')
print(f'duration {dur:.1f}s   peak {np.max(np.abs(pcm))/32767:.2f}   '
      f'bpm {BPM}   16th steps {steps}')
print('playing...')
sys.stdout.flush()

# play three times so it registers if you were dozing
for k in range(3):
    winsound.PlaySound(path, winsound.SND_FILENAME)
    time.sleep(0.4)
print('done')
