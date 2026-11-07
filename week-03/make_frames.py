"""sheet.png(2x2 칸)를 펫 그림 4장으로 자르고, 그려진 체크무늬 배경을 투명하게 지운다.

실행: week-03 폴더에서  python make_frames.py
결과: art/frames/idle.png, type_a.png, type_b.png, sleep.png
"""
from collections import deque
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
SHEET = HERE / "art" / "sheet.png"
OUT = HERE / "art" / "frames"

# 칸 위치 (열, 행) → 저장할 이름
CELLS = {
    (0, 0): "idle",    # ① 두 팔 들기
    (1, 0): "type_a",  # ② 오른쪽 위 · 한 팔 + 느낌표
    (0, 1): "type_b",  # ③ 왼쪽 아래 · 반대 팔 + 느낌표
    (1, 1): "sleep",   # ④ 졸기 Zz
}

BG_MIN = 190    # 체크무늬는 밝다 (흰색 ~255, 회색 ~213)
BG_SPREAD = 20  # 체크무늬는 색이 거의 없다 (R,G,B 가 비슷함)
EDGE_MIN = 140  # 배경 바로 옆의 밝은 회색 테두리 찌꺼기도 지운다
PAD = 6         # 잘라낸 그림 둘레 여백


def is_background(px, limit):
    r, g, b = px[:3]
    return min(r, g, b) >= limit and max(r, g, b) - min(r, g, b) <= BG_SPREAD


def remove_background(cell):
    """칸의 바깥 테두리에서 시작해 체크무늬 색만 투명하게 채워 들어간다.
    검은 외곽선에서 멈추므로 눈 속 흰 점은 지워지지 않는다."""
    img = cell.convert("RGBA")
    w, h = img.size
    px = img.load()
    bg = [[False] * h for _ in range(w)]
    queue = deque()
    for x in range(w):
        queue.extend([(x, 0), (x, h - 1)])
    for y in range(h):
        queue.extend([(0, y), (w - 1, y)])

    while queue:
        x, y = queue.popleft()
        if bg[x][y] or not is_background(px[x, y], BG_MIN):
            continue
        bg[x][y] = True
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not bg[nx][ny]:
                queue.append((nx, ny))

    # 배경과 맞닿은 밝은 회색 한 겹(외곽선 둘레 찌꺼기)도 지운다
    fringe = []
    for x in range(w):
        for y in range(h):
            if bg[x][y] or not is_background(px[x, y], EDGE_MIN):
                continue
            if any(0 <= x + dx < w and 0 <= y + dy < h and bg[x + dx][y + dy]
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                fringe.append((x, y))
    for x, y in fringe:
        bg[x][y] = True

    for x in range(w):
        for y in range(h):
            if bg[x][y]:
                px[x, y] = (0, 0, 0, 0)
    return img


def main():
    sheet = Image.open(SHEET)
    cw, ch = sheet.width // 2, sheet.height // 2
    frames = {}
    for (col, row), name in CELLS.items():
        cell = sheet.crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch))
        frames[name] = remove_background(cell)

    # 4장을 같은 크기로 잘라야 그림이 바뀔 때 펫이 들썩이지 않는다
    boxes = [f.getbbox() for f in frames.values()]
    left = max(min(b[0] for b in boxes) - PAD, 0)
    top = max(min(b[1] for b in boxes) - PAD, 0)
    right = min(max(b[2] for b in boxes) + PAD, cw)
    bottom = min(max(b[3] for b in boxes) + PAD, ch)

    OUT.mkdir(parents=True, exist_ok=True)
    for name, img in frames.items():
        img.crop((left, top, right, bottom)).save(OUT / f"{name}.png")
        # 출력은 영어로: 일부 콘솔에서 한글 출력이 오류를 낸다
        print(f"saved: art/frames/{name}.png  ({right - left}x{bottom - top})")


if __name__ == "__main__":
    main()
