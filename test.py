import unittest

import pixie

from easy_pixie import draw_text, StyledString


class Test(unittest.TestCase):
    def test_font(self):
        output_img = pixie.Image(400, 200)
        output_img.fill(pixie.Color(1, 1, 1, 1))

        raw_text = ("Typesetting is the arrangement and composition of text in "
                    "graphic design and publishing in both digital and traditional medias. "
                    "π 錩 旸 堉 峣 垚 鋆 旻 淏 珺 玥 炘.")
        text = StyledString(raw_text, 'H', 20, max_width=380)

        draw_text(output_img, text, 10, 10)

        output_img.write_file("test_font.png")
        self.assertIsNotNone(output_img)


if __name__ == '__main__':
    unittest.main()
