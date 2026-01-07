
import pygame
import sys
import os
import math

from counter import Counter


class Config:
    """ゲーム設定を管理するクラス"""
    WIDTH = 960
    HEIGHT = 640
    BG_COLOR = (24, 24, 32)
    TEXT_COLOR = (235, 235, 235)
    FPS = 60
    BTN_IMAGE_RATIO = 0.35
    PANEL_BG = (34, 34, 46)
    PANEL_RECT = (58, 92, 130)
    PANEL_RECT_BORDER = (120, 160, 200)
    PANEL_BTN = (80, 140, 200)
    PANEL_BTN_BORDER = (180, 210, 240)
    LEVEL_BAR_BG = (40, 40, 50)
    LEVEL_BAR_FILL = (90, 170, 120)
    LEVEL_BAR_BORDER = (180, 210, 240)


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


class Game:
    """ゲーム全体を管理するクラス"""
    
    def __init__(self):
        """ゲーム初期化"""
        pygame.init()
        
        self.config = Config()
        self.screen = pygame.display.set_mode(
            (self.config.WIDTH, self.config.HEIGHT)
        )
        pygame.display.set_caption("TypingClicker")
        self.clock = pygame.time.Clock()

        # レイアウト領域
        self.left_width = self.config.WIDTH // 2
        self.right_width = self.config.WIDTH - self.left_width
        
        # フォント初期化
        base_size = int(min(self.left_width, self.config.HEIGHT) * 0.12)
        label_size = int(base_size * 0.6)  # 左側ラベル（Typing Power）用
        right_label_size = int(base_size * 0.8)  # 右側メインラベル用（少し控えめ）
        right_sublabel_size = int(base_size * 0.5)  # 右側サブラベル用
        self.counter_font = pygame.font.SysFont(None, base_size)
        self.label_font = pygame.font.SysFont(None, label_size)
        self.right_label_font = pygame.font.SysFont(None, right_label_size)
        self.right_sublabel_font = pygame.font.SysFont(None, right_sublabel_size)

        # ゲーム状態（タイピング力とレベル）
        self.typing_power = 0
        self.power_per_click_base = 1
        self.power_per_second_base = 0
        self.practice_level = 0
        self.auto_level = 0
        self.multiplier_level = 0
        self.level = 1
        self.xp = 0
        self.next_level_xp = self._xp_required(self.level + 1)
        
        # ボタン初期化
        self.button = self._init_button()
        
        # カウンター初期化
        self.counter = Counter(
            self.counter_font,
            self.left_width,
            self.config.HEIGHT,
            offset_x=0,
            offset_y=0,
            label_font=self.label_font,
        )

        # 右パネル用の画像を事前読み込み
        self.right_images, self.right_image_max_width = self._load_right_images()
        
        self.right_button_rects = []
        self.running = True
        self.auto_accumulator_ms = 0
    
    def _init_button(self):
        """ボタンを初期化"""
        # ボタン画像の読み込み
        button_image_path = os.path.join(
            os.path.dirname(__file__), "assets", "computer_keyboard_black.png"
        )
        original_image = pygame.image.load(button_image_path)
        
        # 画像をスケーリング（アスペクト比を保持）
        button_image = self._scale_button_image(original_image, self.config.HEIGHT)
        
        # ボタン中央座標
        center = pygame.Vector2(self.left_width // 2, self.config.HEIGHT * 0.55)
        
        return Button(center, button_image)

    def _scale_image_keep_aspect(self, image, max_width, max_height):
        """アスペクト比を保ったまま、指定サイズに収まるようスケーリング"""
        width, height = image.get_size()
        scale = min(max_width / width, max_height / height, 1)  # 拡大はしない
        new_size = (int(width * scale), int(height * scale))
        return pygame.transform.scale(image, new_size)

    def _load_right_images(self):
        """右パネルで使う画像を読み込み＆スケーリング。最大幅も返す"""
        asset_dir = os.path.join(os.path.dirname(__file__), "assets")
        filenames = [
            "keyboard_typing.png",
            "ai_computer_sousa_robot.png",
            "computer_cpu.png",
        ]

        margin = 24
        available_height = self.config.HEIGHT - margin * 4
        rect_height = available_height / 3

        # 画像は右パネルの幅の約35%、高さは矩形高さの80%以内で比率維持
        max_width = int(self.right_width * 0.35)
        max_height = int(rect_height * 0.8)

        images = []
        max_loaded_width = 0
        for name in filenames:
            path = os.path.join(asset_dir, name)
            img = pygame.image.load(path)
            scaled = self._scale_image_keep_aspect(img, max_width, max_height)
            images.append(scaled)
            if scaled.get_width() > max_loaded_width:
                max_loaded_width = scaled.get_width()
        return images, max_loaded_width
    
    def _scale_button_image(self, original_image, reference_h):
        """
        ボタン画像をアスペクト比を保ったままスケーリング
        
        Args:
            original_image (pygame.Surface): 元画像
            reference_h (int): 参照する高さ
        
        Returns:
            pygame.Surface: スケーリング済み画像
        """
        max_size = int(reference_h * self.config.BTN_IMAGE_RATIO)
        
        orig_width, orig_height = original_image.get_size()
        aspect_ratio = orig_width / orig_height
        
        if aspect_ratio >= 1:  # 横長
            new_width = max_size
            new_height = int(max_size / aspect_ratio)
        else:  # 縦長
            new_height = max_size
            new_width = int(max_size * aspect_ratio)
        
        return pygame.transform.scale(original_image, (new_width, new_height))

    def _xp_required(self, n):
        return math.ceil(125 * (1.5 ** (n - 1)))

    def _current_multiplier(self):
        return 1.5 ** self.multiplier_level

    def _current_power_per_click(self):
        return math.floor(self.power_per_click_base * self._current_multiplier())

    def _current_power_per_second(self):
        return math.floor(self.power_per_second_base * self._current_multiplier())
    
    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button.is_clicked(event.pos):
                    self._add_typing_power(self._current_power_per_click())
                else:
                    for idx, rect in enumerate(self.right_button_rects):
                        if rect.collidepoint(event.pos):
                            self._handle_purchase(idx)
                            break
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.typing_power = 0
                    self.counter.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def render(self):
        """画面に描画"""
        self.screen.fill(self.config.BG_COLOR)
        self.counter.set_value(self.typing_power)
        self.button.draw(self.screen)
        self.counter.draw(self.screen, self.config.TEXT_COLOR)
        self._draw_level_bar()
        self._draw_right_panel()
        pygame.display.flip()

    def _draw_right_panel(self):
        """右パネルのUI（長方形3つ）を描画"""
        margin = 24
        rect_width = self.right_width - margin * 2
        available_height = self.config.HEIGHT - margin * 4
        rect_height = available_height / 3
        image_padding = 16
        text_padding = 16
        labels = ["Typing Skill", "Auto Typing", "CPU"]
        sublabels = [
            f"+ {self._current_power_per_click():,} Per Click",
            f"+ {self._current_power_per_second():,} Per Second",
            f"× {self._current_multiplier():.2f} All",
        ]
        level_labels = [
            f"Level {self.practice_level}",
            f"Level {self.auto_level}",
            f"Level {self.multiplier_level}",
        ]
        costs = self._calc_costs()

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
            + self.right_image_max_width
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
                self.screen,
                self.config.PANEL_RECT,
                rect,
                border_radius=12,
            )
            pygame.draw.rect(
                self.screen,
                self.config.PANEL_RECT_BORDER,
                rect,
                width=2,
                border_radius=12,
            )

            # 画像を長方形の上に重ねて表示（左寄せ＋余白）
            img = self.right_images[i]
            img_rect = img.get_rect()
            img_rect.left = rect.left + image_padding
            img_rect.centery = rect.centery
            self.screen.blit(img, img_rect)

            # ラベルを画像の右隣・上部に配置（枠内に収まるよう調整）
            label_surface = self.right_label_font.render(labels[i], True, self.config.TEXT_COLOR)
            label_rect = label_surface.get_rect()
            desired_left = label_base_left
            max_left = rect.right - text_padding - label_rect.width
            label_rect.left = min(desired_left, max_left)
            label_rect.top = rect.top + text_padding
            self.screen.blit(label_surface, label_rect)

            # サブラベル（効果概要）をラベルの下に表示
            sub_surface = self.right_sublabel_font.render(sublabels[i], True, self.config.TEXT_COLOR)
            sub_rect = sub_surface.get_rect()
            sub_rect.left = label_rect.left
            sub_rect.top = label_rect.bottom + 6
            self.screen.blit(sub_surface, sub_rect)

            # 下部ボタンとその上のレベル表示（デザインのみ）
            # ボタンをラベル左位置に揃え、右余白を確保
            btn_left = label_base_left
            btn_top = rect.bottom - button_padding_y - button_height
            # 右端は既存パディングを尊重し、必要に応じて幅を調整
            btn_width = min(button_width, rect.right - button_padding_x - btn_left)
            btn_rect = pygame.Rect(
                btn_left,
                btn_top,
                btn_width,
                button_height,
            )
            pygame.draw.rect(
                self.screen,
                self.config.PANEL_BTN,
                btn_rect,
                border_radius=10,
            )
            pygame.draw.rect(
                self.screen,
                self.config.PANEL_BTN_BORDER,
                btn_rect,
                width=2,
                border_radius=10,
            )

            # ボタン上のラベル（中央揃え）
            level_surface = self.label_font.render(level_labels[i], True, self.config.TEXT_COLOR)
            level_rect = level_surface.get_rect()
            level_rect.centerx = btn_rect.centerx
            level_rect.bottom = btn_rect.top - 4
            self.screen.blit(level_surface, level_rect)

            # ボタン中央にコスト表示（UIのみ）
            cost_text = f"Cost: {costs[i]:,}"
            cost_surface = self.right_sublabel_font.render(cost_text, True, self.config.TEXT_COLOR)
            cost_rect = cost_surface.get_rect(center=btn_rect.center)
            self.screen.blit(cost_surface, cost_rect)

            # クリック判定用に保持
            self.right_button_rects.append(btn_rect)

    def _draw_level_bar(self):
        """左下にレベル進捗バーを描画（経済に影響しない）"""
        margin = 24
        bar_width = int(self.left_width * 0.85)
        bar_height = 24
        bar_left = margin
        bar_top = self.config.HEIGHT - margin - bar_height - 18  # 余白分上に

        # 背景と枠
        bar_rect = pygame.Rect(bar_left, bar_top, bar_width, bar_height)
        pygame.draw.rect(self.screen, self.config.LEVEL_BAR_BG, bar_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.config.LEVEL_BAR_BORDER, bar_rect, width=2, border_radius=8)

        # 進捗
        needed = max(self.next_level_xp - self._xp_for_current_level(), 1)
        progress = self._xp_for_current_level_progress_ratio()
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_left, bar_top, fill_width, bar_height)
            pygame.draw.rect(self.screen, self.config.LEVEL_BAR_FILL, fill_rect, border_radius=8)

        # テキスト（バー内に%）
        percent_text = f"{progress * 100:5.1f}%"
        percent_surface = self.right_sublabel_font.render(percent_text, True, self.config.TEXT_COLOR)
        percent_rect = percent_surface.get_rect(center=bar_rect.center)
        self.screen.blit(percent_surface, percent_rect)

        # 下に Lv と Next を表示
        level_text = f"Lv {self.level}"
        next_text = f"Next: {self.next_level_xp:,} XP"
        level_surface = self.right_sublabel_font.render(level_text, True, self.config.TEXT_COLOR)
        next_surface = self.right_sublabel_font.render(next_text, True, self.config.TEXT_COLOR)

        # 配置: 左にLv、右にNext、下にRemain
        level_rect = level_surface.get_rect()
        next_rect = next_surface.get_rect()
        level_rect.left = bar_left
        level_rect.top = bar_rect.bottom + 2
        next_rect.right = bar_left + bar_width
        next_rect.top = bar_rect.bottom + 2

        self.screen.blit(level_surface, level_rect)
        self.screen.blit(next_surface, next_rect)

    def _calc_costs(self):
        """UI表示用のコスト計算（購入ロジックなし）"""
        practice_cost = math.ceil(10 * (1.35 ** self.practice_level))
        auto_cost = math.ceil(50 * (1.60 ** self.auto_level))
        multiplier_cost = math.ceil(500 * (3.00 ** self.multiplier_level))
        return [practice_cost, auto_cost, multiplier_cost]

    def _handle_purchase(self, idx):
        """アップグレード購入処理（資金確認のみ）"""
        costs = self._calc_costs()
        cost = costs[idx]
        if self.typing_power < cost:
            return  # 資金不足

        # 支払い
        self.typing_power -= cost

        # レベル更新と効果反映
        if idx == 0:
            self.practice_level += 1
            self.power_per_click_base += 1
        elif idx == 1:
            self.auto_level += 1
            self.power_per_second_base += 2
        elif idx == 2:
            self.multiplier_level += 1

        # 表示更新
        self.counter.set_value(self.typing_power)
    
    def run(self):
        """メインループ"""
        while self.running:
            dt = self.clock.tick(self.config.FPS)
            self._update_auto(dt)
            self.handle_events()
            self.render()
        
        pygame.quit()
        sys.exit()

    def _update_auto(self, dt_ms):
        """毎秒加算の処理（Auto Typing）"""
        self.auto_accumulator_ms += dt_ms
        while self.auto_accumulator_ms >= 1000:
            self.auto_accumulator_ms -= 1000
            gain = self._current_power_per_second()
            if gain > 0:
                self._add_typing_power(gain)

    def _add_typing_power(self, amount):
        self.typing_power += amount
        self._add_xp(amount)
        self.counter.set_value(self.typing_power)

    def _add_xp(self, amount):
        self.xp += amount
        self._check_level_up()

    def _check_level_up(self):
        # 複数段のレベルアップにも対応
        while self.xp >= self.next_level_xp:
            self.level += 1
            self.next_level_xp = self._xp_required(self.level + 1)

    def _xp_for_current_level(self):
        # 現在レベルの開始累計XP
        return self._xp_required(self.level) if self.level > 1 else 0

    def _xp_for_current_level_progress_ratio(self):
        level_start_xp = self._xp_for_current_level()
        span = max(self.next_level_xp - level_start_xp, 1)
        return max(0.0, min(1.0, (self.xp - level_start_xp) / span))


if __name__ == "__main__":
    game = Game()
    game.run()
