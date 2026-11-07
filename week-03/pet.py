"""내 캐릭터 데스크톱 펫.

실행: week-03 폴더에서  .venv\\Scripts\\python pet.py
"""
import sys
from pathlib import Path

from pynput import keyboard
from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtGui import QGuiApplication, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QMenu

FRAMES = Path(__file__).parent / "art" / "frames"
PET_HEIGHT = 160  # 화면에 보일 펫 높이(px)
MARGIN = 12       # 화면 구석에서 띄울 거리(px)
REST_MS = 500     # 키를 멈추고 이만큼 지나면 평소 모습으로 (밀리초)
SLEEP_MS = 10_000 # 이만큼 안 치면 졸기 (밀리초)


class KeyTap(QObject):
    """키가 눌렸다는 '신호'만 보낸다.
    어떤 키인지는 보지도, 저장하지도, 보내지도 않는다 (이번 주 규칙)."""

    tapped = Signal()

    def __init__(self):
        super().__init__()
        # on_press 가 받는 key 값은 일부러 쓰지 않고 버린다
        self.listener = keyboard.Listener(on_press=lambda _key: self.tapped.emit())
        self.listener.daemon = True

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()


class Pet(QLabel):
    def __init__(self):
        super().__init__()
        # 테두리 없음 · 늘 맨 위 · 작업 표시줄에 안 나옴
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        # 창 배경 투명 (그림의 투명한 부분이 그대로 비쳐 보임)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.drag_offset = None

        self.frames = {
            name: QPixmap(str(FRAMES / f"{name}.png")).scaledToHeight(
                PET_HEIGHT, Qt.SmoothTransformation
            )
            for name in ("idle", "type_a", "type_b", "sleep")
        }
        self.show_frame("idle")
        self.move_to_corner()

        self.tap_count = 0      # 누른 횟수 (메모리에만, 파일 저장 없음)
        self.next_frame = "type_a"
        # 키를 멈추면 REST_MS 뒤에 평소 모습으로 돌아가는 타이머
        self.rest_timer = QTimer(self, singleShot=True, interval=REST_MS)
        self.rest_timer.timeout.connect(lambda: self.show_frame("idle"))
        # 마지막으로 친 뒤 SLEEP_MS 가 지나면 조는 타이머
        self.sleep_timer = QTimer(self, singleShot=True, interval=SLEEP_MS)
        self.sleep_timer.timeout.connect(lambda: self.show_frame("sleep"))
        self.sleep_timer.start()

    def on_tap(self):
        self.tap_count += 1
        # ② 와 ③ 을 번갈아 보여 줘서 두드리는 것처럼 보이게
        self.show_frame(self.next_frame)
        self.next_frame = "type_b" if self.next_frame == "type_a" else "type_a"
        self.rest_timer.start()  # 누를 때마다 다시 0.5초 세기
        self.sleep_timer.start()  # 누를 때마다 졸기까지 다시 10초 세기 (졸고 있었으면 깨어남)

    def show_frame(self, name):
        pixmap = self.frames[name]
        self.setPixmap(pixmap)
        self.resize(pixmap.size())

    def move_to_corner(self):
        # availableGeometry = 작업 표시줄을 뺀 화면 영역 → 오른쪽 아래 구석
        area = QGuiApplication.primaryScreen().availableGeometry()
        self.move(
            area.right() - self.width() - MARGIN,
            area.bottom() - self.height() - MARGIN,
        )

    # --- 끌어서 옮기기 (왼쪽 버튼) ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 펫 왼쪽 위 모서리에서 마우스까지의 거리를 기억해 둔다
            self.drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_offset is not None:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = None

    # --- 오른쪽 클릭 메뉴 ---
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        # 보기만 하는 줄 (눌러도 아무 일 없음). 숫자는 메모리에만 있다
        count = menu.addAction(f"지금까지 {self.tap_count:,}번 눌렀어")
        count.setEnabled(False)
        menu.addSeparator()
        menu.addAction("끄기", QApplication.quit)
        menu.exec(event.globalPos())


def main():
    app = QApplication(sys.argv)
    pet = Pet()
    pet.show()

    keys = KeyTap()
    # 키 듣기는 다른 스레드에서 돌아가므로, 시그널로 화면 쪽에 전달한다
    keys.tapped.connect(pet.on_tap)
    keys.start()
    app.aboutToQuit.connect(keys.stop)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
