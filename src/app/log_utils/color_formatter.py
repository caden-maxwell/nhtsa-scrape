import logging

from PyQt6.QtGui import QColor


class ColorFormatter(logging.Formatter):

    level_colors = {
        'DEBUG': QColor('grey'),
        'INFO': QColor('white'),
        'WARNING': QColor('yellow'),
        'ERROR': QColor('red'),
        'CRITICAL': QColor('red')
    }

    def format(self, record):
        color = self.level_colors.get(record.levelname, QColor('white')).name()
        curr_fmt = self._style._fmt
        new_fmt = f'<span style="color:{color}">{curr_fmt}</span>'
        formatter = logging.Formatter(new_fmt)
        return formatter.format(record)