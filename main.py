import pygame
import sys
import os
import random

from config import Config
from game_state import GameState
from game_logic import GameLogic
from ui import Button, Counter, UIRenderer, TypingDisplay
from sentences import sentences


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

        # レイアウト領域（右側は固定、左側は余った領域）
        self.right_width = self.config.RIGHT_WIDTH
        self.left_width = self.config.WIDTH - self.right_width
        
        # フォントファイルのパス
        font_path = os.path.join(
            os.path.dirname(__file__), "assets", "NotoSansJP-Black.ttf"
        )
        
        # フォント初期化
        base_size = int(min(self.left_width, self.config.HEIGHT) * 0.12)
        label_size = int(base_size * 0.6)  # 左側ラベル（Typing Power）用
        right_label_size = int(base_size * 0.65)  # 右側メインラベル用
        right_sublabel_size = int(base_size * 0.4)  # 右側サブラベル用
        self.counter_font = pygame.font.Font(font_path, base_size)
        self.label_font = pygame.font.Font(font_path, label_size)
        self.right_label_font = pygame.font.Font(font_path, right_label_size)
        self.right_sublabel_font = pygame.font.Font(font_path, right_sublabel_size)

        # ゲーム状態の初期化
        self.state = GameState()
        self.next_level_xp = GameLogic.xp_required(self.state.level + 1)
        
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

        # タイピング表示の初期化
        # ボタンは y = HEIGHT * 0.48 の中央、進捗バーは下から約 70px
        # この間に英文を配置
        typing_display_font_size = int(base_size * 0.55)
        typing_display_font = pygame.font.Font(font_path, typing_display_font_size)
        
        # 日本語フォント（Noto Sans JPを使用）
        japanese_font_size = int(base_size * 0.4)
        japanese_font = pygame.font.Font(font_path, japanese_font_size)
        
        button_center_y = int(self.config.HEIGHT * 0.48)
        button_size = int(self.config.HEIGHT * self.config.BTN_IMAGE_RATIO)
        button_bottom_y = button_center_y + button_size // 2
        
        progress_bar_top_y = self.config.HEIGHT - 24 - 18 - 24  # 進捗バーの上部Y座標
        typing_display_height = progress_bar_top_y - button_bottom_y - 20  # 20pxの余白
        typing_display_top_y = button_bottom_y + 10
        
        self.typing_display = TypingDisplay(
            typing_display_font,
            japanese_font,
            self.left_width,
            typing_display_height,
            offset_x=0,
            offset_y=typing_display_top_y,
        )
        
        # ランダムな文章を選択して表示
        self._set_random_sentence()

        # 右パネル用の画像を事前読み込み
        self.right_images, self.right_image_max_width = self._load_right_images()
        
        # UI描画クラスの初期化
        fonts = {
            'label': self.label_font,
            'right_label': self.right_label_font,
            'right_sublabel': self.right_sublabel_font,
        }
        self.ui_renderer = UIRenderer(
            self.config,
            fonts,
            self.left_width,
            self.right_width,
            self.config.HEIGHT
        )
        
        self.running = True
        self.auto_accumulator_ms = 0

        # 保存データの読み込み
        self.state.load()
        self.next_level_xp = GameLogic.xp_required(self.state.level + 1)
        self.counter.set_value(self.state.typing_power)
    
    def _init_button(self):
        """ボタンを初期化"""
        # ボタン画像の読み込み
        button_image_path = os.path.join(
            os.path.dirname(__file__), "assets", "keyboard.png"
        )
        original_image = pygame.image.load(button_image_path)
        
        # 画像をスケーリング（アスペクト比を保持）
        button_image = self._scale_button_image(original_image, self.config.HEIGHT)
        
        # ボタン中央座標
        center = pygame.Vector2(self.left_width // 2, self.config.HEIGHT * 0.48)
        
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
            "robot.png",
            "cpu.png",
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
    
    def _set_random_sentence(self):
        """ランダムな文章を選択して表示"""
        sentence = random.choice(sentences)
        # sentence = [id, english, japanese]
        english = sentence[1]
        japanese = sentence[2]
        self.typing_display.set_sentence(english, japanese)
    
    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button.is_clicked(event.pos):
                    multiplier = GameLogic.current_multiplier(self.state.multiplier_level)
                    power = GameLogic.current_power_per_click(self.state.power_per_click_base, multiplier)
                    self._add_typing_power(power)
                else:
                    for idx, rect in enumerate(self.ui_renderer.right_button_rects):
                        if rect.collidepoint(event.pos):
                            self._handle_purchase(idx)
                            break
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    # タイピング処理
                    if event.unicode:  # 入力可能な文字の場合
                        if self.typing_display.check_input(event.unicode):
                            # 正しい入力の場合、ポイント+1
                            self._add_typing_power(1)
                            
                            # タイピング完了チェック
                            if self.typing_display.is_complete():
                                self._set_random_sentence()
    
    def render(self):
        """画面に描画"""
        self.screen.fill(self.config.BG_COLOR)
        self.counter.set_value(self.state.typing_power)
        self.button.draw(self.screen)
        self.counter.draw(self.screen, self.config.TEXT_COLOR)
        
        # レベル進捗バーの描画
        level_state = {
            'level': self.state.level,
            'next_xp': self.next_level_xp,
            'progress': GameLogic.xp_progress_ratio(self.state.xp, self.state.level, self.next_level_xp),
        }
        self.ui_renderer.draw_level_bar(self.screen, level_state)
        
        # 右パネルの描画
        multiplier = GameLogic.current_multiplier(self.state.multiplier_level)
        game_state = {
            'power_per_click': GameLogic.current_power_per_click(self.state.power_per_click_base, multiplier),
            'power_per_second': GameLogic.current_power_per_second(self.state.power_per_second_base, multiplier),
            'multiplier': multiplier,
            'practice_level': self.state.practice_level,
            'auto_level': self.state.auto_level,
            'multiplier_level': self.state.multiplier_level,
            'costs': GameLogic.calc_costs(self.state.practice_level, self.state.auto_level, self.state.multiplier_level),
        }
        self.ui_renderer.draw_right_panel(
            self.screen,
            game_state,
            self.right_images,
            self.right_image_max_width
        )
        
        # タイピング表示の描画
        self.typing_display.draw(self.screen, self.config.TEXT_COLOR)
        
        pygame.display.flip()

    def _handle_purchase(self, idx):
        """アップグレード購入処理（資金確認のみ）"""
        costs = GameLogic.calc_costs(self.state.practice_level, self.state.auto_level, self.state.multiplier_level)
        cost = costs[idx]
        if self.state.typing_power < cost:
            return  # 資金不足

        # 支払い
        self.state.typing_power -= cost

        # レベル更新と効果反映
        if idx == 0:
            self.state.practice_level += 1
            self.state.power_per_click_base += 1
        elif idx == 1:
            self.state.auto_level += 1
            self.state.power_per_second_base += 2
        elif idx == 2:
            self.state.multiplier_level += 1

        # 表示更新
        self.counter.set_value(self.state.typing_power)
    
    def run(self):
        """メインループ"""
        while self.running:
            dt = self.clock.tick(self.config.FPS)
            self._update_auto(dt)
            self.handle_events()
            self.render()
        
        self.state.save()
        pygame.quit()
        sys.exit()

    def _update_auto(self, dt_ms):
        """毎秒加算の処理（Auto Typing）"""
        self.auto_accumulator_ms += dt_ms
        while self.auto_accumulator_ms >= 1000:
            self.auto_accumulator_ms -= 1000
            multiplier = GameLogic.current_multiplier(self.state.multiplier_level)
            gain = GameLogic.current_power_per_second(self.state.power_per_second_base, multiplier)
            if gain > 0:
                self._add_typing_power(gain)

    def _add_typing_power(self, amount):
        self.state.typing_power += amount
        self._add_xp(amount)
        self.counter.set_value(self.state.typing_power)

    def _add_xp(self, amount):
        self.state.xp += amount
        self._check_level_up()

    def _check_level_up(self):
        # 複数段のレベルアップにも対応
        while self.state.xp >= self.next_level_xp:
            self.state.level += 1
            self.next_level_xp = GameLogic.xp_required(self.state.level + 1)


if __name__ == "__main__":
    game = Game()
    game.run()
