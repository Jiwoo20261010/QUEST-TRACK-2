"""앞발이 패드를 칠 때 낼 짧은 "탁" 소리를 만든다 (Python 기본 기능만 사용).

실행: week-03 폴더에서  python make_sound.py
결과: art/tak.wav
"""
import math
import random
import struct
import wave
from pathlib import Path

OUT = Path(__file__).parent / "art" / "tak.wav"
RATE = 44100      # 1초에 소리 조각 44100개
LENGTH = 0.06     # 소리 길이 0.06초
VOLUME = 0.35     # 0~1, 너무 크지 않게

random.seed(7)  # 매번 똑같은 소리가 나오게


def sample(t):
    fade = math.exp(-t * 90)                       # 빨리 사라지는 소리
    thump = math.sin(2 * math.pi * 180 * t)        # 낮은 "툭"
    click = random.uniform(-1, 1) * math.exp(-t * 400)  # 처음 아주 짧은 "탁"
    return VOLUME * fade * (0.6 * thump + 0.4 * click)


def main():
    frames = b"".join(
        struct.pack("<h", int(max(-1, min(1, sample(i / RATE))) * 32767))
        for i in range(int(RATE * LENGTH))
    )
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(frames)
    print(f"saved: art/tak.wav ({LENGTH}s)")


if __name__ == "__main__":
    main()
