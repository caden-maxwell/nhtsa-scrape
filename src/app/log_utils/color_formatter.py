import logging

from PyQt6.QtGui import QColor


class ColorFormatter(logging.Formatter):

    level_colors = {
        'DEBUG': QColor(200, 200, 255), # light blue
        'INFO': QColor('white'), # light gray
        'WARNING': QColor('yellow'),
        'ERROR': QColor(255, 100, 100),
        'CRITICAL': QColor('red')
    }

    def format(self, record):
        color = self.level_colors.get(record.levelname, QColor('white')).name()
        curr_fmt = self._style._fmt
        log = logging.Formatter(curr_fmt).format(record)
        log = f'<pre style="color: {color}; font-family: consolas; white-space: pre-wrap;">{log}</pre>'
        return log
