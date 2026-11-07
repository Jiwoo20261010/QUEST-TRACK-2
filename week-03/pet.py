"""내 캐릭터 데스크톱 펫.

실행: week-03 폴더에서  .venv\\Scripts\\python pet.py
"""
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QPixmap
from PySide6.QtWidgets import QApplication, QLabel

FRAMES = Path(__file__).parent / "art" / "frames"
PET_HEIGHT = 160  # 화면에 보일 펫 높이(px)
MARGIN = 12       # 화면 구석에서 띄울 거리(px)


class Pet(QLabel):
    def __init__(self):
        super().__init__()
        # 테두리 없음 · 늘 맨 위 · 작업 표시줄에 안 나옴
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        # 창 배경 투명 (그림의 투명한 부분이 그대로 비쳐 보임)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.frames = {
            name: QPixmap(str(FRAMES / f"{name}.png")).scaledToHeight(
                PET_HEIGHT, Qt.SmoothTransformation
            )
            for name in ("idle", "type_a", "type_b", "sleep")
        }
        self.show_frame("idle")
        self.move_to_corner()

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

    def mouseDoubleClickEvent(self, event):
        # 임시: 단계 3 에서 오른쪽 클릭 "끄기" 메뉴가 생기면 없앤다
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    pet = Pet()
    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
