"""Snapshot 测试：锁定 generator 在固定输入下的输出 hash。

目的：作为后续重构 / web 化的安全网。任何修改导致 prompt 文本变化都会让这些
测试失败，强迫修改方主动确认是预期内还是回归。

如何更新基线：
    1. 检查 hash 变化背后的 prompt 改动是不是预期。
    2. 若是预期（例如调优了模板措辞），运行：
           python -m tests.dump_snapshot
       并把输出粘贴到下方 EXPECTED 字典里。
    3. commit 时在消息里说明"调整 X，更新 snapshot"。

运行：
    python -m unittest tests.test_generators_snapshot
"""
import hashlib
import random
import unittest


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def _first(opts):
    return opts[0] if opts else ""


SPACESHIP_EXPECTED = {
    "Weapon|TIER_1_CIVILIAN|Kinetic": "08db382748c88bfc",
    "Weapon|TIER_2_INDUSTRIAL|Kinetic": "7d2b367489dc3e8b",
    "Weapon|TIER_3_MILITARY|Kinetic": "686cbf8b8b15c644",
    "Weapon|TIER_4_ELITE|Kinetic": "eeefa1cd50421bfe",
    "Weapon|TIER_5_LEGENDARY|Kinetic": "84de4c519dbbb874",
    "Shield|TIER_1_CIVILIAN|Bubble": "8ca5246b0e8cf6f1",
    "Shield|TIER_2_INDUSTRIAL|Bubble": "04a6c165803b0313",
    "Shield|TIER_3_MILITARY|Bubble": "8b907ea7cf74af96",
    "Shield|TIER_4_ELITE|Bubble": "820ddb667c529de3",
    "Shield|TIER_5_LEGENDARY|Bubble": "2fecfd09040ccc67",
    "Engine|TIER_1_CIVILIAN|Ion": "6368f4fa1d5723c2",
    "Engine|TIER_2_INDUSTRIAL|Ion": "a8d500972945dd3d",
    "Engine|TIER_3_MILITARY|Ion": "9782b5bbf64ea7d5",
    "Engine|TIER_4_ELITE|Ion": "75a194af76cdcb78",
    "Engine|TIER_5_LEGENDARY|Ion": "bd33795db6984e84",
    "Cargo|TIER_1_CIVILIAN|Standard": "3c365140c64dec71",
    "Cargo|TIER_2_INDUSTRIAL|Standard": "419606db3bfc557a",
    "Cargo|TIER_3_MILITARY|Standard": "2b00790859bef990",
    "Cargo|TIER_4_ELITE|Standard": "63ddc9894208447d",
    "Cargo|TIER_5_LEGENDARY|Standard": "0f550fab0aff31ac",
}

CHARACTER_DEFAULT_EN = "dc2b186f50c03855"
CLOTHING_DEFAULT_EN = "02207fd73ebc9b07"


class SpaceshipPromptSnapshot(unittest.TestCase):
    def test_all_categories_and_tiers(self):
        import prompt_generator as pg
        random.seed(42)
        actual = {}
        for cat, subs in pg.get_component_map().items():
            if not subs:
                continue
            sub = subs[0]
            for tier in pg.get_tier_list():
                key = f"{cat}|{tier}|{sub}"
                out = pg.generate_prompt_by_strings(
                    tier, cat, sub, "#445566", "#FFAA00", "None", "None"
                )
                actual[key] = _hash(out)
        self.assertEqual(actual, SPACESHIP_EXPECTED)


class CharacterPromptSnapshot(unittest.TestCase):
    def test_default_en(self):
        import character_generator as cg
        lang = "en"
        out = cg.generate_character_prompt(
            gender=_first(cg.get_gender_options(lang)), age=25,
            framing=_first(cg.get_framing_options(lang)),
            aspect_ratio=_first(cg.get_aspect_ratio_options(lang)),
            expression=_first(cg.get_expression_options(lang)),
            gaze=_first(cg.get_gaze_options(lang)),
            appearance_features=[],
            body_type=_first(cg.get_body_type_options(lang)),
            skin_tone=_first(cg.get_skin_tone_options(lang)),
            hair_style=_first(cg.get_hair_style_options(lang)),
            hair_color=_first(cg.get_hair_color_options(lang)),
            hair_colors=[],
            hair_bangs_presence=_first(cg.get_bangs_presence_options(lang)),
            hair_bangs_style=_first(cg.get_bangs_style_options(lang)),
            face_shape=_first(cg.get_face_shape_options(lang)),
            eye_size=_first(cg.get_eye_size_options(lang)),
            nose_size=_first(cg.get_nose_size_options(lang)),
            mouth_shape=_first(cg.get_mouth_shape_options(lang)),
            cheek_fullness=_first(cg.get_cheek_fullness_options(lang)),
            jaw_width=_first(cg.get_jaw_width_options(lang)),
            eye_color=_first(cg.get_eye_color_options(lang)),
            clothing_hint=_first(cg.get_clothing_hint_options(lang)),
            artists=[], lang=lang,
        )
        self.assertEqual(_hash(out), CHARACTER_DEFAULT_EN)


class ClothingPromptSnapshot(unittest.TestCase):
    def test_default_en(self):
        import clothing_generator as clg
        lang = "en"
        out = clg.generate_clothing_preset_prompt(
            faction=_first(clg.get_faction_options(lang)),
            gender=_first(clg.get_gender_options(lang)),
            role=_first(clg.get_role_options(lang)),
            outfit_category=_first(clg.get_outfit_category_options(lang)),
            silhouette=_first(clg.get_silhouette_options(lang)),
            layering=_first(clg.get_layering_options(lang)),
            material=_first(clg.get_material_options(lang)),
            palette=_first(clg.get_palette_options(lang)),
            wear_state=_first(clg.get_wear_state_options(lang)),
            presentation=_first(clg.get_presentation_options(lang)),
            pose=_first(clg.get_pose_options(lang)),
            view_mode=_first(clg.get_view_mode_options(lang)),
            aspect_ratio=_first(clg.get_aspect_ratio_options(lang)),
            detail_accents=[], accessories=[], insignia=[], lang=lang,
        )
        self.assertEqual(_hash(out), CLOTHING_DEFAULT_EN)


class ItemGeneratorBasics(unittest.TestCase):
    """item_generator 依赖网络翻译，只锁定 CSV 解析行为。"""

    def test_default_csv_loads(self):
        import item_generator as ig
        items = ig.read_items_from_csv(ig.DEFAULT_CSV_PATH) or []
        # 不锁数量（CSV 可能被用户更新），只断言能成功解析为 list。
        self.assertIsInstance(items, list)


class SharedOptionsHelpers(unittest.TestCase):
    """验证 character / clothing 都使用同一份共享 helper。"""

    def test_helpers_are_identical(self):
        from core import character_generator as cg
        from core import clothing_generator as clg
        from core import _options_shared as shared
        self.assertIs(cg._make_options, shared.make_options)
        self.assertIs(clg._make_options, shared.make_options)
        self.assertIs(cg._label_to_value, shared.label_to_value)
        self.assertIs(clg._label_to_value, shared.label_to_value)


if __name__ == "__main__":
    unittest.main()
