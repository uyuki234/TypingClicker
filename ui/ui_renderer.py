"""UI描画を管理するモジュール"""

import pygame


class UIRenderer:
    """UI描画を管理するクラス"""
    
    def __init__(self, config, fonts, left_width, right_width, screen_height):
        """
        Args:
            config (Config): ゲーム設定
            fonts (dict): フォント辞書
            left_width (int): 左側領域の幅
            right_width (int): 右側領域の幅
            screen_height (int): 画面高さ
        """
        self.config = config
        self.label_font = fonts['label']
        self.right_label_font = fonts['right_label']
        self.right_sublabel_font = fonts['right_sublabel']
        self.left_width = left_width
        self.right_width = right_width
        self.screen_height = screen_height
        self.right_button_rects = []
    
    def draw_right_panel(self, surface, game_state, right_images, right_image_max_width):
        """右パネルのUI（長方形3つ）を描画"""
        margin = 24
        rect_width = self.right_width - margin * 2
        available_height = self.screen_height - margin * 4
        rect_height = available_height / 3
        image_padding = 16
        text_padding = 16
        labels = ["Typing Skill", "Auto Typing", "CPU"]
        sublabels = [
            f"+ {game_state['power_per_click']:,} Per Click",
            f"+ {game_state['power_per_second']:,} Per Second",
            f"× {game_state['multiplier']:.2f} All",
        ]
        level_labels = [
            f"Level {game_state['practice_level']}",
            f"Level {game_state['auto_level']}",
            f"Level {game_state['multiplier_level']}",
        ]
        costs = game_state['costs']

        # ボタン領域をクリック判定用に初期化
        self.right_button_rects = []

        # ボタンサイズ（各枠の中で下部に配置）
        button_width = int(rect_width * 0.55)
        button_height = int(rect_height * 0.28)
        button_padding_x = 16
        button_padding_y = 12

        # 画像の最大幅を使ってラベルの基準X座標を決定（全行共通）
        label_base_left = (
            self.left_width
            + margin
            + image_padding
            + right_image_max_width
            + image_padding
        )

        for i in range(3):
            top = margin + i * (rect_height + margin)
            rect_x = self.left_width + margin
            rect = pygame.Rect(
                rect_x,
                top,
                rect_width,
                rect_height,
            )
            pygame.draw.rect(
                surface,
                self.config.PANEL_RECT,
                rect,
                border_radius=12,
            )
            pygame.draw.rect(
                surface,
                self.config.PANEL_RECT_BORDER,
                rect,
                width=2,
                border_radius=12,
            )

            # 画像を長方形の上に重ねて表示（左寄せ＋余白）
            img = right_images[i]
            img_rect = img.get_rect()
            img_rect.left = rect.left + image_padding
            img_rect.centery = rect.centery
            surface.blit(img, img_rect)

            # 下部ボタンの左端を先に計算
            btn_left = label_base_left
            btn_top = rect.bottom - button_padding_y - button_height
            btn_width = min(button_width, rect.right - button_padding_x - btn_left)
            btn_rect = pygame.Rect(
                btn_left,
                btn_top,
                btn_width,
                button_height,
            )

            # メインラベル（Typing Skill等）を枠の上側に配置
            label_surface = self.right_label_font.render(labels[i], True, self.config.TEXT_COLOR)
            label_rect = label_surface.get_rect()
            label_rect.left = btn_left
            label_rect.top = rect.top + 8
            surface.blit(label_surface, label_rect)

            # サブラベル（効果概要）をメインラベルの下に配置（左端を揃える）
            sub_surface = self.right_sublabel_font.render(sublabels[i], True, self.config.TEXT_COLOR)
            sub_rect = sub_surface.get_rect()
            sub_rect.left = btn_left
            sub_rect.top = label_rect.bottom + 2
            surface.blit(sub_surface, sub_rect)

            # レベルラベルをボタンの上側中央に配置
            level_surface = self.label_font.render(level_labels[i], True, self.config.TEXT_COLOR)
            level_rect = level_surface.get_rect()
            level_rect.centerx = btn_rect.centerx
            level_rect.bottom = btn_rect.top - 4
            surface.blit(level_surface, level_rect)

            pygame.draw.rect(
                surface,
                self.config.PANEL_BTN,
                btn_rect,
                border_radius=10,
            )
            pygame.draw.rect(
                surface,
                self.config.PANEL_BTN_BORDER,
                btn_rect,
                width=2,
                border_radius=10,
            )

            # ボタン中央にコスト表示
            cost_text = f"Cost: {costs[i]:,}"
            cost_surface = self.right_sublabel_font.render(cost_text, True, self.config.TEXT_COLOR)
            cost_rect = cost_surface.get_rect(center=btn_rect.center)
            surface.blit(cost_surface, cost_rect)

            # クリック判定用に保持
            self.right_button_rects.append(btn_rect)
    
    def draw_level_bar(self, surface, level_state):
        """左下にレベル進捗バーを描画"""
        margin = 24
        bar_width = int(self.left_width * 0.85)
        bar_height = 24
        bar_left = (self.left_width - bar_width) // 2  # 左側領域内で中央配置
        bar_top = self.screen_height - margin - bar_height - 18

        # 背景と枠
        bar_rect = pygame.Rect(bar_left, bar_top, bar_width, bar_height)
        pygame.draw.rect(surface, self.config.LEVEL_BAR_BG, bar_rect, border_radius=8)
        pygame.draw.rect(surface, self.config.LEVEL_BAR_BORDER, bar_rect, width=2, border_radius=8)

        # 進捗
        progress = level_state['progress']
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_left, bar_top, fill_width, bar_height)
            pygame.draw.rect(surface, self.config.LEVEL_BAR_FILL, fill_rect, border_radius=8)

        # テキスト（バー内に%）
        percent_text = f"{progress * 100:5.1f}%"
        percent_surface = self.right_sublabel_font.render(percent_text, True, self.config.TEXT_COLOR)
        percent_rect = percent_surface.get_rect(center=bar_rect.center)
        surface.blit(percent_surface, percent_rect)

        # 下に Lv と Next を表示
        level_text = f"Lv {level_state['level']}"
        next_text = f"Next: {level_state['next_xp']:,} XP"
        level_surface = self.right_sublabel_font.render(level_text, True, self.config.TEXT_COLOR)
        next_surface = self.right_sublabel_font.render(next_text, True, self.config.TEXT_COLOR)

        # 配置: 左にLv、右にNext
        level_rect = level_surface.get_rect()
        next_rect = next_surface.get_rect()
        level_rect.left = bar_left
        level_rect.top = bar_rect.bottom + 2
        next_rect.right = bar_left + bar_width
        next_rect.top = bar_rect.bottom + 2

        surface.blit(level_surface, level_rect)
        surface.blit(next_surface, next_rect)
