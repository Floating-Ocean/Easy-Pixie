"""
单元测试
"""

import unittest

import pixie

from easy_pixie import draw_text, StyledString, pick_gradient_color, hex_to_color, color_to_hex, \
    load_img, change_img_alpha, lighten_color


class Test(unittest.TestCase):
    """
    测试一些基础功能
    """
    def test_font(self):
        """
        测试字体
        """
        output_img = pixie.Image(1024, 320)
        output_img.fill(pixie.Color(1, 1, 1, 1))

        raw_text = ("Typesetting is the arrangement and composition of text in "
                    "graphic design and publishing in both digital and traditional medias. "
                    "π 錩 旸 堉 峣 垚 鋆 旻 淏 珺 玥 炘.")
        text = StyledString(raw_text, 'H', 36, max_width=960, line_multiplier=1.5)

        draw_text(output_img, text, 32, 32)

        output_img.write_file("test_font.png")
        self.assertIsNotNone(output_img)

        loaded_img = load_img("test_font.png")
        img_alpha = change_img_alpha(loaded_img, 100 / 255)
        img_alpha.write_file("test_font_alpha.png")
        self.assertIsNotNone(img_alpha)


    def test_gradient(self):
        """
        测试渐变色选取
        """
        picked = pick_gradient_color()
        self.assertIsNotNone(picked)
        print(picked)

    def test_color_type_transform(self):
        """
        测试不同类型颜色代码互转
        """
        color_hex_3 = "FFF"
        color_hex_4 = "#FFF"
        color_hex_4a = "FFFF"
        color_hex_5 = "#FFFF"
        color_hex_6 = "FFFFFF"
        color_hex_7 = "#FFFFFF"
        color_hex_8 = "FFFFFFFF"
        color_hex_9 = "#FFFFFFFF"
        for color_hex in [
            color_hex_3, color_hex_4, color_hex_4a,
            color_hex_5, color_hex_6, color_hex_7,
            color_hex_8, color_hex_9
        ]:
            print(f"Testing color type transform: {color_hex}")
            color_pixie = hex_to_color(color_hex)
            self.assertIsNotNone(color_pixie)
            print(f"Transformed pixie color: pixie.Color({color_pixie.r}. {color_pixie.g}, "
                  f"{color_pixie.r}, {color_pixie.a})")
            self.assertEqual(color_pixie, pixie.Color(1, 1, 1, 1))
            color_re_hex = color_to_hex(color_pixie)
            print(f"Retransformed hex color: {color_re_hex}\n")

    def test_color_lighten(self):
        """
        测试提升颜色亮度
        """
        output_img = pixie.Image(1024, 320)
        color = hex_to_color("#F4D03F")
        output_img.fill(color)

        raw_text = ("Typesetting is the arrangement and composition of text in "
                    "graphic design and publishing in both digital and traditional medias. "
                    "π 錩 旸 堉 峣 垚 鋆 旻 淏 珺 玥 炘.")

        text = StyledString(raw_text, 'H', 36, max_width=960, line_multiplier=1.5,
                            font_color=lighten_color(color, 0.2))

        draw_text(output_img, text, 32, 32)

        output_img.write_file("test_color_lighten.png")
        self.assertIsNotNone(output_img)


if __name__ == '__main__':
    unittest.main()
