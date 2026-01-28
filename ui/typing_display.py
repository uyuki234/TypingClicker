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
        self.text = ""
        self.current_position = 0  # 現在の入力位置
    
    def set_text(self, text):
        """表示するテキストを設定
        
        Args:
            text (str): 表示する英文
        """
        self.text = text
        self.current_position = 0
    
    def check_input(self, char):
        """入力文字をチェック
        
        Args:
            char (str): 入力された文字
            
        Returns:
            bool: 正しい入力の場合True
        """
        # 全て入力済みの場合
        if self.current_position >= len(self.text):
            return False
        
        # 期待される文字（大文字小文字を区別する）
        expected_char = self.text[self.current_position]
        input_char = char
        
        # 正しい入力の場合
        if expected_char == input_char:
            self.current_position += 1
            return True
        
        return False
    
    def is_complete(self):
        """タイピングが完了したかチェック
        
        Returns:
            bool: 完了している場合True
        """
        # 最後まで到達しているかチェック
        return self.current_position >= len(self.text)
    
    def draw(self, surface, color):
        """テキストを描画（入力済みの文字は灰色、スペースは_で表示）"""
        if not self.text:
            return
        
        # スペースを_に置換して表示
        display_text = self.text.replace(' ', '_')
        
        # 入力済み部分と未入力部分に分ける
        typed_part = display_text[:self.current_position]
        remaining_part = display_text[self.current_position:]
        
        # 灰色（入力済み）
        gray_color = (128, 128, 128)
        
        # 入力済み部分をレンダリング
        typed_surface = self.font.render(typed_part, True, gray_color)
        # 未入力部分をレンダリング
        remaining_surface = self.font.render(remaining_part, True, color)
        
        # 全体の幅を計算
        total_width = typed_surface.get_width() + remaining_surface.get_width()
        
        # 中央揃えの開始位置
        start_x = self.offset_x + (self.container_width - total_width) // 2
        text_y = self.offset_y + (self.container_height - typed_surface.get_height()) // 2
        
        # 入力済み部分を描画
        surface.blit(typed_surface, (start_x, text_y))
        # 未入力部分を描画
        surface.blit(remaining_surface, (start_x + typed_surface.get_width(), text_y))
