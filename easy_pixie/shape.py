"""
有关图形的工具类 shape.py
Copyright (c) 2025 Floating Ocean. License under MIT.
"""

from dataclasses import dataclass
from enum import Enum

import pixie

from .color import decode_color_object, GradientColor


@dataclass
class Loc:
    """绘制图形时的坐标信息"""
    x: int
    y: int
    width: int
    height: int


def draw_rect(img: pixie.Image, paint: pixie.Paint, loc: Loc, round_size: float = 0):
    """
    绘制一个矩形，可指定圆角大小
    """
    ctx = img.new_context()
    ctx.fill_style = paint
    ctx.rounded_rect(loc.x, loc.y, loc.width, loc.height,
                     round_size, round_size, round_size, round_size)
    ctx.fill()


class GradientDirection(Enum):
    """
    渐变绘制方向

    VERTICAL: 从上往下
    HORIZONTAL: 从左往右
    DIAGONAL_LEFT_TO_RIGHT: 沿对角线从左上往右下
    DIAGONAL_RIGHT_TO_LEFT: 沿对角线从左下往右上
    """
    VERTICAL = 0
    HORIZONTAL = 1
    DIAGONAL_LEFT_TO_RIGHT = 2
    DIAGONAL_RIGHT_TO_LEFT = 3


def draw_gradient_rect(img: pixie.Image, loc: Loc,
                       colors: GradientColor, direction: GradientDirection,
                       round_size: float = 0):
    """
    绘制一个渐变矩形，可指定渐变方向，圆角大小
    """
    paint = pixie.Paint(pixie.LINEAR_GRADIENT_PAINT if len(colors.color_list) == 2 else
                        pixie.RADIAL_GRADIENT_PAINT)  # 渐变色画笔

    for idx, raw_color in enumerate(colors.color_list):
        color = pixie.parse_color(raw_color)

        if direction == GradientDirection.VERTICAL:
            position = pixie.Vector2(loc.x + loc.width / 2,
                                     loc.y + loc.height * colors.pos_list[idx])
        elif direction == GradientDirection.HORIZONTAL:
            position = pixie.Vector2(loc.x + loc.width * colors.pos_list[idx],
                                     loc.y + loc.height / 2)
        elif direction == GradientDirection.DIAGONAL_LEFT_TO_RIGHT:
            position = pixie.Vector2(loc.x + loc.width * colors.pos_list[idx],
                                     loc.y + loc.height * colors.pos_list[idx])
        else:
            position = pixie.Vector2(loc.x + loc.width * colors.pos_list[idx],
                                     loc.y + loc.height * (1.0 - colors.pos_list[idx]))

        paint.gradient_handle_positions.append(position)
        paint.gradient_stops.append(pixie.ColorStop(color, idx))

    draw_rect(img, paint, loc, round_size)


def draw_mask_rect(img: pixie.Image, loc: Loc, color: pixie.Color | tuple[int, ...],
                   round_size: float = 0, blend_mode: int = pixie.NORMAL_BLEND):
    """
    绘制一个蒙版矩形，可指定圆角大小
    """
    color = decode_color_object(color)
    paint_mask = pixie.Paint(pixie.SOLID_PAINT)  # 蒙版画笔
    paint_mask.color = color
    mask = pixie.Image(loc.width, loc.height)
    draw_rect(mask, paint_mask, Loc(0, 0, loc.width, loc.height), round_size)
    img.draw(mask, pixie.translate(loc.x, loc.y), blend_mode)


def draw_full(img: pixie.Image, color: pixie.Color | tuple[int, ...]):
    """
    覆盖整个图片为一个颜色
    """
    color = decode_color_object(color)
    img.fill(color)


def load_img(img_path: str) -> pixie.Image:
    """
    加载图片
    """
    return pixie.read_image(img_path)


def draw_img(img: pixie.Image, img_to_draw: pixie.Image, loc: Loc):
    """
    绘制一个带着色的纯色图片
    """
    tinted_img = img_to_draw.resize(loc.width, loc.height)
    img.draw(tinted_img, pixie.translate(loc.x, loc.y))
