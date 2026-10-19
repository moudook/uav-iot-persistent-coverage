"""Loud repeating alarm to wake the user."""
import winsound, sys, time

def beep(freq, ms):
    winsound.Beep(freq, ms)

print('playing alert...')
sys.stdout.flush()

# classic wake-up alarm: 4 bursts, each 3 tones, twice
for burst in range(3):
    for f in (1800, 1400, 1800):
        beep(f, 260)
    time.sleep(0.35)

# second pattern, lower and longer, more penetrating
for burst in range(2):
    for f in (2000, 1600, 2000, 1600):
        beep(f, 320)
    time.sleep(0.5)

# final long tone
beep(2200, 1200)

print('done')
