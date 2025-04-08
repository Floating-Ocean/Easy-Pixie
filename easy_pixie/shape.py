from enum import Enum

import pixie

from .color import apply_tint


def draw_rect(image: pixie.Image, paint: pixie.Paint, x: int, y: int, width: int, height: int, round_size: float = 0):
    """
    绘制一个矩形，可指定圆角大小
    """
    ctx = image.new_context()
    ctx.fill_style = paint
    ctx.rounded_rect(x, y, width, height, round_size, round_size, round_size, round_size)
    ctx.fill()


class GradientDirection(Enum):
    """
    渐变绘制方向

    VERTICAL: 从上往下
    HORIZONTAL: 从左往右
    DIAGONAL_LEFT_TO_RIGHT: 沿对角线从左上往右下
    DIAGONAL_RIGHT_TO_LEFT: 沿对角线从左下往右上
    """
    VERTICAL = 0,
    HORIZONTAL = 1,
    DIAGONAL_LEFT_TO_RIGHT = 2,
    DIAGONAL_RIGHT_TO_LEFT = 3


def draw_gradient_rect(image: pixie.Image, x: int, y: int, width: int, height: int,
                       colors: list[str], positions: list[float], direction: GradientDirection, round_size: float = 0):
    """
    绘制一个渐变矩形，可指定渐变方向，圆角大小
    """
    paint = pixie.Paint(pixie.LINEAR_GRADIENT_PAINT if len(colors) == 2 else pixie.RADIAL_GRADIENT_PAINT)  # 渐变色画笔

    for idx in range(len(colors)):
        color = pixie.parse_color(colors[idx])

        if direction == GradientDirection.VERTICAL:
            pixie.Vector2(x + width / 2,
                          y + height * positions[idx])
        elif direction == GradientDirection.HORIZONTAL:
            pixie.Vector2(x + width * positions[idx],
                          y + height / 2)
        elif direction == GradientDirection.DIAGONAL_LEFT_TO_RIGHT:
            pixie.Vector2(x + width * positions[idx],
                          y + height * positions[idx])
        else:
            pixie.Vector2(x + width * positions[idx],
                          y + height * (1.0 - positions[idx]))

        paint.gradient_handle_positions.append()
        paint.gradient_stops.append(pixie.ColorStop(color, idx))

    draw_rect(image, paint, x, y, width, height, round_size)


def draw_mask_rect(image: pixie.Image, x: int, y: int, width: int, height: int, color: pixie.Color,
                   round_size: float = 0, blend_mode: int = pixie.NORMAL_BLEND):
    """
    绘制一个蒙版矩形，可指定圆角大小
    """
    paint_mask = pixie.Paint(pixie.SOLID_PAINT)  # 蒙版画笔
    paint_mask.color = color
    mask = pixie.Image(width, height)
    draw_rect(mask, paint_mask, 0, 0, width, height, round_size)
    image.draw(mask, pixie.translate(x, y), blend_mode)


def draw_img(img: pixie.Image, img_path: str, x: int, y: int, img_size: tuple[int, int], color: pixie.Color):
    """
    绘制一个带着色的纯色图片
    """
    tinted_img = apply_tint(img_path, color).resize(img_size[0], img_size[1])
    img.draw(tinted_img, pixie.translate(x, y))
