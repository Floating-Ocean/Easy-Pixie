"""
有关颜色的工具类 color.py
Copyright (c) 2025 Floating Ocean. License under MIT.
"""
import json
import os
import random
from dataclasses import dataclass
from typing import TypedDict

import pixie



def apply_tint(image_path: str, tint: pixie.Color) -> pixie.Image:
    """
    给图片应用覆盖色

    :param image_path   目标图片位置
    :param tint         覆盖色
    :return             处理完后的图片
    """
    image = pixie.read_image(image_path)
    width, height = image.width, image.height
    tinted_image = pixie.Image(width, height)
    alpha = 1
    for x in range(width):
        for y in range(height):
            orig_pixel = image.get_color(x, y)
            mixed_r = orig_pixel.r * (1 - alpha) + tint.r * alpha
            mixed_g = orig_pixel.g * (1 - alpha) + tint.g * alpha
            mixed_b = orig_pixel.b * (1 - alpha) + tint.b * alpha
            tinted_image.set_color(x, y, pixie.Color(mixed_r, mixed_g, mixed_b, orig_pixel.a))
    return tinted_image


class GradientItem(TypedDict):
    """
    单个渐变色
    """
    name: str
    colors: list[str]


@dataclass
class GradientColor:
    """
    打包后的单个渐变色数据类
    """
    color_list: list[str]
    pos_list: list[float]
    name: str


def _get_ui_gradient_colors() -> list[GradientItem]:
    colors = []
    json_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        "color"
        f'ui-gradient.json'
    )
    with open(json_path, 'r') as f:
        colors = json.load(f)
    return colors


def pick_gradient_color(colors: list[GradientItem] | None) -> GradientColor:
    """
    从渐变色列表中选择一个颜色，只支持 2~3 种颜色
    列表留空则将从 ui-gradient 中选择

    :param colors: 包含 name 和 colors 的字典列表
    :return: 选中的渐变色的颜色列表, 渐变色坐标列表（均匀分布）, 颜色的名称（包含编号）
    """

    if colors is None:
        colors = _get_ui_gradient_colors()

    valid_colors = [color for color in colors if 2 <= len(color['colors']) <= 3]
    if len(valid_colors) == 0:
        raise RuntimeError('No valid colors found')

    picked_colors, color_name = [], ""
    while not 2 <= len(picked_colors) <= 3:
        color_idx = random.randint(0, len(colors) - 1)
        picked_colors = colors[color_idx]["colors"]
        color_name = f"#{color_idx + 1} {colors[color_idx]['name']}"

    if random.randint(0, 1):
        picked_colors.reverse()

    position_list = [0.0, 1.0] if len(picked_colors) == 2 else [0.0, 0.5, 1.0]
    return GradientColor(picked_colors, position_list, color_name)


def choose_text_color(bg_color: pixie.Color) -> pixie.Color:
    """
    根据背景颜色的明度选择合适的字体颜色

    :return: 白 / 黑
    """
    luminance = 0.299 * bg_color.r + 0.587 * bg_color.g + 0.114 * bg_color.b
    return (pixie.Color(0.0706, 0.0706, 0.0706, 1) if luminance > 0.502 else
            pixie.Color(0.9882, 0.9882, 0.9882, 1))


def darken_color(color: pixie.Color, ratio: float = 0.7) -> pixie.Color:
    """
    降低颜色明度
    """
    return pixie.Color(color.r * ratio, color.g * ratio, color.b * ratio, color.a)


def tuple_to_color(color: tuple[int, ...]) -> pixie.Color:
    """
    转换 rgb/rgba 元组为 pixie.Color
    """
    if len(color) == 3:
        return pixie.Color(color[0] / 255, color[1] / 255, color[2] / 255, 1)

    return pixie.Color(color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)


def color_to_tuple(color: pixie.Color, include_alpha: bool = True) -> tuple[int, ...]:
    """
    转换 pixie.Color 为 rgb/rgba 元组
    """
    if include_alpha:
        return (round(color.r * 255), round(color.g * 255), round(color.b * 255),
                round(color.a * 255))

    return round(color.r * 255), round(color.g * 255), round(color.b * 255)
