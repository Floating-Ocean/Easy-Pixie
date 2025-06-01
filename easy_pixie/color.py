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



def apply_tint(img: pixie.Image, tint: pixie.Color | tuple[int, ...], ratio: int = 1,
               replace_alpha: bool = False) -> pixie.Image:
    """
    给图片应用覆盖色

    :param img              目标图片
    :param tint             覆盖色
    :param ratio            覆盖程度（1为完全覆盖）
    :param replace_alpha    覆盖透明度
    :return                 处理完后的图片
    """
    tint = decode_color_object(tint)
    width, height = img.width, img.height
    tinted_image = pixie.Image(width, height)
    for x in range(width):
        for y in range(height):
            orig_pixel = img.get_color(x, y)
            mixed_r = orig_pixel.r * (1 - ratio) + tint.r * ratio
            mixed_g = orig_pixel.g * (1 - ratio) + tint.g * ratio
            mixed_b = orig_pixel.b * (1 - ratio) + tint.b * ratio
            mixed_a = orig_pixel.a * (1 - ratio) + tint.a * ratio
            tinted_image.set_color(x, y, pixie.Color(mixed_r, mixed_g, mixed_b,
                                                     mixed_a if replace_alpha else orig_pixel.a))
    return tinted_image


def change_img_alpha(img: pixie.Image, alpha_ratio: float) -> pixie.Image:
    """
    更改图片透明度

    :param img          目标图片
    :param alpha_ratio  更改透明度，<1 则更加透明，>1则更加不透明，对透明像素无影响
    :return             处理完后的图片
    """
    width, height = img.width, img.height
    tinted_image = pixie.Image(width, height)
    for x in range(width):
        for y in range(height):
            orig_pixel = img.get_color(x, y)
            mixed_a = orig_pixel.a * alpha_ratio
            tinted_image.set_color(x, y, change_alpha(orig_pixel, f_alpha=mixed_a))
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
    json_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        "color",
        "ui-gradient.json"
    )
    with open(json_path, 'r', encoding='utf-8') as f:
        colors = json.load(f)
    return colors


def pick_gradient_color(colors: list[GradientItem] | None = None) -> GradientColor:
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


def choose_text_color(bg_color: pixie.Color | tuple[int, ...]) -> pixie.Color:
    """
    根据背景颜色的明度选择合适的字体颜色

    :return: 白 / 黑
    """
    bg_color = decode_color_object(bg_color)
    luminance = 0.299 * bg_color.r + 0.587 * bg_color.g + 0.114 * bg_color.b
    return (pixie.Color(0.0706, 0.0706, 0.0706, 1) if luminance > 0.502 else
            pixie.Color(0.9882, 0.9882, 0.9882, 1))


def darken_color(color: pixie.Color | tuple[int, ...],
                 ratio: float = 0.7) -> pixie.Color:
    """
    降低颜色明度
    """
    if ratio > 1:
        raise ValueError('ratio must be [0, 1]')

    color = decode_color_object(color)
    return pixie.Color(color.r * ratio, color.g * ratio, color.b * ratio, color.a)


def lighten_color(color: pixie.Color | tuple[int, ...],
                  ratio: float = 0.7) -> pixie.Color:
    """
    提高颜色明度
    """
    if ratio > 1:
        raise ValueError('ratio must be [0, 1]')

    color = decode_color_object(color)
    return pixie.Color(color.r + (1 - color.r) * ratio,
                       color.g + (1 - color.g) * ratio,
                       color.b + (1 - color.b) * ratio,
                       color.a)


def change_alpha(color: pixie.Color | tuple[int, ...],
                 alpha: int = -1, f_alpha: float = -1) -> pixie.Color:
    """
    替换 color 中的 alpha 值，alpha 和 f_alpha 二选一，前者优先
    :param color: 待替换颜色
    :param alpha: 整数 alpha 值 (0~255)
    :param f_alpha: 浮点数 alpha 值 (0~1)
    :return: 替换后的颜色
    """
    color = decode_color_object(color)
    if 0 <= alpha <= 255:
        return pixie.Color(color.r, color.g, color.b, alpha / 255)
    if 0 <= f_alpha <= 1:
        return pixie.Color(color.r, color.g, color.b, f_alpha)

    raise ValueError('Invalid alpha and f_alpha')


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


def hex_to_color(hex_str: str) -> pixie.Color:
    """
    转换 16进制颜色 为 pixie.Color
    """
    if not hex_str.startswith('#'):
        if len(hex_str) not in [3, 4, 6, 8]:
            raise ValueError('hex_str must be in hex format')
        hex_str = f"#{hex_str}"

    alpha = 1.0
    if len(hex_str) == 5:
        alpha = int(f"{hex_str[4:]}{hex_str[4:]}", 16) / 255
        hex_str = hex_str[:4]
    elif len(hex_str) == 9:
        alpha = int(hex_str[7:], 16) / 255
        hex_str = hex_str[:7]

    if len(hex_str) not in [4, 7]:
        raise ValueError('hex_str must be in hex format')

    return change_alpha(pixie.parse_color(hex_str), f_alpha=alpha)


def color_to_hex(color: pixie.Color, include_alpha: bool = True) -> str:
    """
    转换 pixie.Color 为 rgb/rgba 元组
    """
    r, g, b, a = color_to_tuple(color)
    color_hex = f"#{r:02x}{g:02x}{b:02x}{a:02x}"

    if not include_alpha:
        return color_hex[:7]

    return color_hex


def decode_color_object(color: pixie.Color | tuple[int, ...]) -> pixie.Color:
    """
    解析 union 为 pixie.Color
    """
    if isinstance(color, tuple):
        color = tuple_to_color(color)
    return color
