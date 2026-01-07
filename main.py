
import pygame
import sys
import os

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
        label_size = int(base_size * 0.4)
        self.counter_font = pygame.font.SysFont(None, base_size)
        self.label_font = pygame.font.SysFont(None, label_size)
        
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
        
        self.running = True
    
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
    
    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button.is_clicked(event.pos):
                    self.counter.increment()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.counter.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def render(self):
        """画面に描画"""
        self.screen.fill(self.config.BG_COLOR)
        self.button.draw(self.screen)
        self.counter.draw(self.screen, self.config.TEXT_COLOR)
        self._draw_right_panel()
        pygame.display.flip()

    def _draw_right_panel(self):
        """右パネルのUI（長方形3つ）を描画"""
        margin = 24
        rect_width = self.right_width - margin * 2
        available_height = self.config.HEIGHT - margin * 4
        rect_height = available_height / 3

        for i in range(3):
            top = margin + i * (rect_height + margin)
            rect = pygame.Rect(
                self.left_width + margin,
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
    
    def run(self):
        """メインループ"""
        while self.running:
            self.clock.tick(self.config.FPS)
            self.handle_events()
            self.render()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
