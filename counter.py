class Counter:
    """カウンター表示を管理するクラス"""
    
    def __init__(self, font, width, height):
        """
        Args:
            font (pygame.font.Font): カウント表示用フォント
            width (int): 画面幅
            height (int): 画面高さ
        """
        self.font = font
        self.width = width
        self.height = height
        self.value = 0
    
    def increment(self):
        """カウントを1増やす"""
        self.value += 1
    
    def reset(self):
        """カウントをリセット"""
        self.value = 0
    
    def draw(self, surface, text_color):
        """カウンターを描画"""
        text = self.font.render(str(self.value), True, text_color)
        rect = text.get_rect(center=(self.width // 2, int(self.height * 0.2)))
        surface.blit(text, rect)
