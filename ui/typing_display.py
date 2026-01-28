"""タイピング用の英文を表示するモジュール"""

import pygame


class TypingDisplay:
    """タイピング練習用の英文を表示するクラス"""
    
    def __init__(self, font, container_width, container_height, offset_x=0, offset_y=0):
        """
        Args:
            font (pygame.font.Font): 表示用フォント
            container_width (int): コンテナの幅
            container_height (int): コンテナの高さ
            offset_x (int): X方向のオフセット
            offset_y (int): Y方向のオフセット
        """
        self.font = font
        self.container_width = container_width
        self.container_height = container_height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.text = "Please contact customer support for assistance."
    
    def set_text(self, text):
        """表示するテキストを設定"""
        self.text = text
    
    def draw(self, surface, color):
        """テキストを描画"""
        # テキストをレンダリング
        text_surface = self.font.render(self.text, True, color)
        
        # 水平・垂直センタリング
        text_x = self.offset_x + (self.container_width - text_surface.get_width()) // 2
        text_y = self.offset_y + (self.container_height - text_surface.get_height()) // 2
        
        surface.blit(text_surface, (text_x, text_y))
