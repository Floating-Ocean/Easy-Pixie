import os
import re

import pixie


_MAX_WIDTH = 1024


class StyledString:
    def __init__(self, content: str, font_weight: str, font_size: int, font_color: tuple[float, ...] = (0, 0, 0, 1),
                 line_multiplier: float = 1.0, padding_bottom: int = 0, max_width: int = -1,
                 custom_font_path: str | None = None):
        self.content = content
        self.line_multiplier = line_multiplier
        self.padding_bottom = padding_bottom
        self.max_width = max_width

        font_path = os.path.join(os.path.dirname(__file__), "data", f'OPPOSans-{font_weight}.ttf')
        if custom_font_path is not None:
            font_path = custom_font_path
        try:  # 尝试加载字体
            self.font = pixie.read_font(font_path)
            self.font.size = font_size
            if len(font_color) == 3:
                self.font.paint.color = pixie.Color(font_color[0], font_color[1], font_color[2], 1)
            else:
                self.font.paint.color = pixie.Color(font_color[0], font_color[1], font_color[2], font_color[3])
        except IOError as e:
            raise IOError(f"无法加载字体文件: {font_path}") from e

        self.height = draw_text(None, self, 0, 0, draw=False)

    def set_font_color(self, font_color: pixie.Color):
        self.font.paint.color = font_color


def text_size(content: str, font: pixie.Font) -> tuple[int, int]:
    """
    获取指定字体下文本的大小

    :return: [width, height]
    """
    bounds = font.layout_bounds(content)
    return bounds.x, bounds.y


def calculate_string_width(content: StyledString) -> int:
    """
    计算文本在给定字体和大小下的长度（宽度）。

    :param content: 要测量的文本内容
    :return: 文本的宽度（像素）
    """
    text_width, _ = text_size(content.content, content.font)
    return text_width


def calculate_height(strings: list[StyledString | None]) -> int:
    """
    计算多个文本的高度。

    :param strings: 文本
    :return: 总高度
    """

    height = 0
    for string in strings:
        if string:  # 允许传None，降低代码复杂度
            height += string.height
    return height


def draw_text(image: pixie.Image | None, styled_string: StyledString, x: int, y: int, draw: bool = True) -> int:
    """
    绘制文本

    :param image            目标图片
    :param styled_string    包装后的文本内容
    :param x                文本左上角的横坐标
    :param y                文本左上角的纵坐标
    :param draw             是否绘制
    :return                 文本基线的高度
    """
    if draw and image is None:
        raise RuntimeError('Image should not be None for drawing.')

    if styled_string.max_width == -1:
        styled_string.max_width = _MAX_WIDTH

    offset = 0
    lines = styled_string.content.split("\n")
    text_height = styled_string.font.layout_bounds("A").y

    for line in lines:
        if not line.strip():  # 忽略空行
            offset += int(text_height * styled_string.line_multiplier)
            continue

        text_width, _ = text_size(line, font=styled_string.font)
        words: list[str] = re.findall(r'\s+\S+|\S+|\s+', line)  # 分割为单词，并把空格放在单词前面处理
        draw_text = ""
        line_x = 0
        first_line = True

        for word in words:
            text_width, _ = text_size(word, font=styled_string.font)
            line_x += text_width

            if line_x <= styled_string.max_width:
                draw_text += word
            else:  # 将该单词移到下一行
                if len(draw_text) > 0:
                    if draw:
                        image.fill_text(styled_string.font, draw_text, pixie.translate(x, y + offset))
                    offset += int(text_height * styled_string.line_multiplier)
                    first_line = False

                if not first_line:
                    word = word.replace(" ", "")  # 保证除了第一行，每一行开头不是空格
                    text_width, _ = text_size(word, font=styled_string.font)

                while text_width > styled_string.max_width:  # 简单的文本分割逻辑，一行塞不下就断开
                    n = text_width // styled_string.max_width
                    sub_pos = int(len(word) // n)
                    draw_text = word[:sub_pos]
                    draw_width, _ = text_size(draw_text, font=styled_string.font)

                    while draw_width > styled_string.max_width and sub_pos > 0:  # 微调，保证不溢出
                        sub_pos -= 1
                        draw_text = word[:sub_pos]
                        draw_width, _ = text_size(draw_text, font=styled_string.font)

                    if draw:
                        image.fill_text(styled_string.font, draw_text, pixie.translate(x, y + offset))
                    offset += int(text_height * styled_string.line_multiplier)
                    first_line = False
                    word = word[sub_pos:]
                    text_width -= draw_width

                draw_text = word
                line_x = text_width

        if len(draw_text) > 0:
            if draw:
                image.fill_text(styled_string.font, draw_text, pixie.translate(x, y + offset))
            offset += int(text_height * styled_string.line_multiplier)

    return offset + styled_string.padding_bottom
