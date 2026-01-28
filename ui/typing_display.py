"""タイピング用の英文を表示するモジュール"""

import pygame


class TypingDisplay:
    """タイピング練習用の英文を表示するクラス"""
    
    def __init__(self, english_font, japanese_font, container_width, container_height, offset_x=0, offset_y=0):
        """
        Args:
            english_font (pygame.font.Font): 英文表示用フォント
            japanese_font (pygame.font.Font): 日本語表示用フォント
            container_width (int): コンテナの幅
            container_height (int): コンテナの高さ
            offset_x (int): X方向のオフセット
            offset_y (int): Y方向のオフセット
        """
        self.english_font = english_font
        self.japanese_font = japanese_font
        self.container_width = container_width
        self.container_height = container_height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.english_text = ""
        self.japanese_text = ""
        self.current_position = 0  # 現在の入力位置
    
    def set_sentence(self, english, japanese):
        """表示する文章を設定
        
        Args:
            english (str): 英文
            japanese (str): 日本語訳
        """
        self.english_text = english
        self.japanese_text = japanese
        self.current_position = 0
    
    def check_input(self, char):
        """入力文字をチェック
        
        Args:
            char (str): 入力された文字
            
        Returns:
            bool: 正しい入力の場合True
        """
        # 全て入力済みの場合
        if self.current_position >= len(self.english_text):
            return False
        
        # 期待される文字（大文字小文字を区別する）
        expected_char = self.english_text[self.current_position]
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
        return self.current_position >= len(self.english_text)
    
    def draw(self, surface, color):
        """テキストを2行で描画（上：日本語訳、下：英文）"""
        if not self.english_text:
            return
        
        # スペースを_に置換して表示
        display_text = self.english_text.replace(' ', '_')
        
        # 入力済み部分と未入力部分に分ける
        typed_part = display_text[:self.current_position]
        remaining_part = display_text[self.current_position:]
        
        # 灰色（入力済み）
        gray_color = (128, 128, 128)
        
        # 日本語訳をレンダリング
        japanese_surface = self.japanese_font.render(self.japanese_text, True, color)
        
        # 入力済み部分をレンダリング
        typed_surface = self.english_font.render(typed_part, True, gray_color)
        # 未入力部分をレンダリング
        remaining_surface = self.english_font.render(remaining_part, True, color)
        
        # 全体の幅を計算（英文）
        english_width = typed_surface.get_width() + remaining_surface.get_width()
        
        # 行間
        line_spacing = 15
        
        # 合計の高さ
        total_height = japanese_surface.get_height() + line_spacing + typed_surface.get_height()
        
        # 垂直方向の開始位置（中央揃え）
        start_y = self.offset_y + (self.container_height - total_height) // 2
        
        # 日本語訳を上に配置（中央揃え）
        japanese_x = self.offset_x + (self.container_width - japanese_surface.get_width()) // 2
        japanese_y = start_y
        surface.blit(japanese_surface, (japanese_x, japanese_y))
        
        # 英文を下に配置（中央揃え）
        english_start_x = self.offset_x + (self.container_width - english_width) // 2
        english_y = start_y + japanese_surface.get_height() + line_spacing
        
        # 入力済み部分を描画
        surface.blit(typed_surface, (english_start_x, english_y))
        # 未入力部分を描画
        surface.blit(remaining_surface, (english_start_x + typed_surface.get_width(), english_y))
