"""カウンター表示UIコンポーネント"""


class Counter:
    """カウンター表示を管理するクラス"""

    def __init__(self, font, width, height, offset_x=0, offset_y=0, label_font=None):
        """
        Args:
            font (pygame.font.Font): カウント表示用フォント
            width (int): レイアウト領域の幅
            height (int): レイアウト領域の高さ
            offset_x (int): 描画開始位置のXオフセット
            offset_y (int): 描画開始位置のYオフセット
            label_font (pygame.font.Font | None): 見出し用フォント
        """
        self.font = font
        self.label_font = label_font or font
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.value = 0

    def increment(self):
        """カウントを1増やす"""
        self.value += 1

    def reset(self):
        """カウントをリセット"""
        self.value = 0

    def set_value(self, value):
        """外部状態に合わせて値を更新"""
        self.value = value

    def draw(self, surface, text_color):
        """カウンターを描画"""
        center_x = self.offset_x + self.width // 2
        center_y = self.offset_y + int(self.height * 0.2)

        # ラベル
        label_surface = self.label_font.render("English Power", True, text_color)
        label_rect = label_surface.get_rect(
            center=(center_x, center_y - label_surface.get_height() - 20)
        )
        surface.blit(label_surface, label_rect)

        # 数値
        text = self.font.render(str(self.value), True, text_color)
        rect = text.get_rect(center=(center_x, center_y))
        surface.blit(text, rect)
