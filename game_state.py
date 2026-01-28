"""ゲーム状態を管理するモジュール"""

import os
import json


class GameState:
    """ゲーム状態を管理するクラス"""

    def __init__(self, save_path=None):
        """
        Args:
            save_path (str | None): セーブファイルのパス
        """
        self.save_path = save_path or os.path.join(
            os.path.dirname(__file__), "save.json"
        )

        # ゲーム状態
        self.typing_power = 0
        self.power_per_click_base = 1
        self.power_per_second_base = 0
        self.practice_level = 0
        self.auto_level = 0
        self.multiplier_level = 0
        self.level = 1
        self.xp = 0

    def save(self):
        """現在の状態をJSONファイルに保存"""
        data = {
            "typing_power": self.typing_power,
            "power_per_click_base": self.power_per_click_base,
            "power_per_second_base": self.power_per_second_base,
            "practice_level": self.practice_level,
            "auto_level": self.auto_level,
            "multiplier_level": self.multiplier_level,
            "level": self.level,
            "xp": self.xp,
        }
        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except OSError:
            # 保存失敗時は黙って続行
            pass

    def load(self):
        """JSONファイルから状態を読み込み"""
        if not os.path.exists(self.save_path):
            return

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return

        self.typing_power = int(data.get("typing_power", self.typing_power))
        self.power_per_click_base = int(
            data.get("power_per_click_base", self.power_per_click_base)
        )
        self.power_per_second_base = int(
            data.get("power_per_second_base", self.power_per_second_base)
        )
        self.practice_level = int(data.get("practice_level", self.practice_level))
        self.auto_level = int(data.get("auto_level", self.auto_level))
        self.multiplier_level = int(data.get("multiplier_level", self.multiplier_level))
        self.level = int(data.get("level", self.level))
        self.xp = int(data.get("xp", self.xp))
