"""ゲームロジック（計算処理）を管理するモジュール"""

import math


class GameLogic:
    """ゲームのビジネスロジックを提供するクラス"""

    @staticmethod
    def xp_required(level):
        """指定レベルに到達するために必要な累計XP

        Args:
            level (int): 目標レベル

        Returns:
            int: 必要な累計XP
        """
        return math.ceil(125 * (1.5 ** (level - 1)))

    @staticmethod
    def current_multiplier(multiplier_level):
        """現在の倍率を計算

        Args:
            multiplier_level (int): 倍率レベル

        Returns:
            float: 倍率
        """
        return 1.5 ** multiplier_level

    @staticmethod
    def current_power_per_click(power_per_click_base, multiplier):
        """現在のクリック当たりパワーを計算

        Args:
            power_per_click_base (int): 基本クリックパワー
            multiplier (float): 倍率

        Returns:
            int: クリック当たりパワー
        """
        return math.floor(power_per_click_base * multiplier)

    @staticmethod
    def current_power_per_second(power_per_second_base, multiplier):
        """現在の毎秒パワーを計算

        Args:
            power_per_second_base (int): 基本毎秒パワー
            multiplier (float): 倍率

        Returns:
            int: 毎秒パワー
        """
        return math.floor(power_per_second_base * multiplier)

    @staticmethod
    def calc_costs(practice_level, auto_level, multiplier_level):
        """各アップグレードのコストを計算

        Args:
            practice_level (int): タイピングスキルレベル
            auto_level (int): 自動タイピングレベル
            multiplier_level (int): CPU倍率レベル

        Returns:
            list[int]: [practice_cost, auto_cost, multiplier_cost]
        """
        practice_cost = math.ceil(10 * (1.35 ** practice_level))
        auto_cost = math.ceil(50 * (1.60 ** auto_level))
        multiplier_cost = math.ceil(500 * (3.00 ** multiplier_level))
        return [practice_cost, auto_cost, multiplier_cost]

    @staticmethod
    def xp_for_current_level(level):
        """現在レベルの開始累計XPを計算

        Args:
            level (int): 現在レベル

        Returns:
            int: レベル開始時の累計XP
        """
        return GameLogic.xp_required(level) if level > 1 else 0

    @staticmethod
    def xp_progress_ratio(current_xp, level, next_level_xp):
        """現在レベル内での進捗率を計算

        Args:
            current_xp (int): 現在の累計XP
            level (int): 現在レベル
            next_level_xp (int): 次レベルに必要な累計XP

        Returns:
            float: 進捗率 (0.0 ~ 1.0)
        """
        level_start_xp = GameLogic.xp_for_current_level(level)
        span = max(next_level_xp - level_start_xp, 1)
        return max(0.0, min(1.0, (current_xp - level_start_xp) / span))
