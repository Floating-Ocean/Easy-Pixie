"""
有关文本的工具类 text.py
Copyright (c) 2025 Floating Ocean. License under MIT.
"""

import os
import re

import pixie

from .color import decode_color_object

_MAX_WIDTH = 1024


class StyledString:
    """包装类，打包文本绘制参数"""

    font: pixie.Font

    # 默认参数配置
    _DEFAULTS = {
        "font_color": pixie.Color(0, 0, 0, 1),
        "line_multiplier": 1.0,
        "padding_bottom": 0,
        "max_width": -1,
        "custom_font_path": None
    }

    def __init__(self, content: str, font_weight: str, font_size: int, **kwargs):
        """
        StyledString

        :param content: 文本内容（必需）
        :param font_weight: 字重 (必需, 可选: "L", "R", "M", "B", "H")
        :param font_size: 字号
        :param kwargs: 可选参数包括:
            - font_color: 颜色 (支持元组或 pixie.Color, 默认: 黑色)
            - line_multiplier: 行距倍数 (默认: 1.0)
            - padding_bottom: 底部间距 (默认: 0)
            - max_width: 最大宽度 (默认: -1, 指代 _MAX_WIDTH = 1024)
            - custom_font_path: 自定义字体路径, 留空则使用 OPPOSans (默认: None)
        """
        self.content = content

        config = {**self._DEFAULTS, **kwargs}

        self.line_multiplier = config["line_multiplier"]
        self.padding_bottom = config["padding_bottom"]
        self.max_width = config["max_width"]

        font_color = decode_color_object(config["font_color"])

        font_path = config["custom_font_path"] or os.path.join(
            os.path.dirname(__file__),
            "data",
            "font",
            f'OPPOSans-{font_weight}.ttf'
        )

        self._init_font(font_path, font_size, font_color)
        self.height = draw_text(None, self, 0, 0, draw=False)

    def _init_font(self, font_path: str, font_size: int, font_color: pixie.Color):
        """初始化字体对象"""
        self.set_font(font_path)
        self.font.size = font_size
        self.font.paint.color = font_color

    def __repr__(self) -> str:
        """调试用字符串表示"""
        return f"<StyledString: '{self.content[:15]}...'>"

    def set_font(self, font_path: str):
        """
        设置字体
        注意，设置字体后，字体大小和颜色信息会丢失
        """
        try:
            self.font = pixie.read_font(font_path)
        except IOError as e:
            raise IOError(f"无法加载字体文件: {font_path}") from e

    def set_font_size(self, font_size: int):
        """设置字体大小"""
        self.font.size = font_size

    def set_font_color(self, font_color: pixie.Color):
        """设置字体颜色"""
        self.font.paint.color = font_color


def _text_size(content: str, font: pixie.Font) -> tuple[int, int]:
    """
    获取指定字体下文本的大小

    :return: [width, height]
    """
    bounds = font.layout_bounds(content)
    return bounds.x, bounds.y


def calculate_width(strings: list[StyledString | None] | StyledString) -> int:
    """
    计算多个文本的宽度。

    :param strings: 文本
    :return: 文本的总宽度（像素）
    """

    if isinstance(strings, StyledString):
        strings = [strings]

    width = 0
    for string in strings:
        if string:  # 允许传None，降低代码复杂度
            width += _text_size(string.content, string.font)[0]
    return width


def calculate_height(strings: list[StyledString | None] | StyledString) -> int:
    """
    计算多个文本的高度。

    :param strings: 文本
    :return: 文本的总高度（像素）
    """

    if isinstance(strings, StyledString):
        strings = [strings]

    height = 0
    for string in strings:
        if string:  # 允许传None，降低代码复杂度
            height += string.height
    return height


def draw_text(image: pixie.Image | None, text: StyledString, x: int, y: int,
              draw: bool = True) -> int:
    """
    绘制文本

    :param image            目标图片
    :param text             包装后的文本内容
    :param x                文本左上角的横坐标
    :param y                文本左上角的纵坐标
    :param draw             是否绘制
    :return                 文本基线的高度
    """

    def _draw_token(token_buffer: str, current_offset: int):
        """绘制单词"""
        if draw and image:
            image.fill_text(text.font, token_buffer, pixie.translate(x, y + current_offset))

    def _accumulate_offset() -> int:
        """获取行高"""
        _text_height = text.font.layout_bounds("A").y
        return int(_text_height * text.line_multiplier)

    def _split_long_token(current_line: str) -> list[str]:
        tokens: list[str] = re.findall(r'\s+\S+|\S+|\s+', current_line)  # 分割为单词，并把空格放在单词前面处理
        line_width = 0
        split_tokens = [""]
        for token in tokens:
            text_width = _text_size(token, font=text.font)[0]
            line_width += text_width

            if line_width <= text.max_width:
                split_tokens[-1] += token
            else:
                if len(split_tokens[-1]) > 0:
                    split_tokens.append("")  # 将该单词移到下一行

                if len(split_tokens) > 1:
                    token = token.lstrip()  # 保证除了第一行，每一行开头不是空格
                    text_width = _text_size(token, font=text.font)[0]

                while text_width > text.max_width:  # 简单的文本分割逻辑，一行塞不下就断开
                    n = text_width // text.max_width
                    cut_pos = int(len(token) // n)
                    split_tokens[-1] = token[:cut_pos]
                    draw_width = _text_size(split_tokens[-1], font=text.font)[0]

                    while draw_width > text.max_width and cut_pos > 0:  # 微调，保证不溢出
                        cut_pos -= 1
                        split_tokens[-1] = token[:cut_pos]
                        draw_width = _text_size(split_tokens[-1], font=text.font)[0]

                    split_tokens.append("")
                    token = token[cut_pos:]
                    text_width -= draw_width

                split_tokens[-1] = token
                line_width = text_width

        return [split for split in split_tokens if len(split) > 0]

    if draw and image is None:
        raise RuntimeError('Image should not be None for drawing.')

    text.max_width = text.max_width if text.max_width != -1 else _MAX_WIDTH
    offset = 0

    for line in text.content.split("\n"):
        if not line.strip():  # 忽略空行
            offset += _accumulate_offset()
            continue
        for current_token in _split_long_token(line):
            _draw_token(current_token, offset)
            offset += _accumulate_offset()

    return y + offset + text.padding_bottom
