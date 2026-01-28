"""ボタンUIコンポーネント"""


class Button:
    """ボタンの状態と描画を管理するクラス"""

    def __init__(self, center_pos, button_image):
        """
        Args:
            center_pos (pygame.Vector2): ボタンの中央座標
            button_image (pygame.Surface): ボタン画像
        """
        self.center = center_pos
        self.image = button_image

    def is_clicked(self, mouse_pos):
        """マウス位置がボタン上かどうかを判定"""
        rect = self.image.get_rect(center=(int(self.center.x), int(self.center.y)))
        return rect.collidepoint(mouse_pos)

    def draw(self, surface):
        """ボタンを描画"""
        rect = self.image.get_rect(center=(int(self.center.x), int(self.center.y)))
        surface.blit(self.image, rect)
