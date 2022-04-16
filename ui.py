import numpy as np
import curses


class UI(object):

    def __init__(self, fg_color, bg_color):
        self.main_window = None
        self.levels_to_screen = None
        self.fg_color = fg_color
        self.bg_color = bg_color

    def init(self, window):
        self.main_window = window
        self.levels_to_screen = curses.LINES / 255

        curses.init_pair(1, self.fg_color, self.bg_color)
        curses.curs_set(0)
        window.attron(curses.color_pair(1))

    def map_levels_to_term_size(self, levels):
        levels = np.floor(levels * self.levels_to_screen)
        return levels.astype(int)

    def update_levels(self, levels):
        column_heights = self.map_levels_to_term_size(levels)

        self.main_window.erase()

        for i, height in enumerate(column_heights):
            if height == 0:
                continue

            self.main_window.vline(curses.LINES - height, i, '|', height)

        self.main_window.refresh()
