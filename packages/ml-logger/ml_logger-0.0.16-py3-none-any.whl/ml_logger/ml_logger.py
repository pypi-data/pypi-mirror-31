import os
from datetime import datetime

from typing import Union, Callable, Any
from collections import OrderedDict, deque

from ml_logger.log_client import LogClient
from termcolor import colored as c
import numpy as np


class Stream:
    def __init__(self, len=100):
        self.d = deque(maxlen=len)

    def append(self, d):
        self.d.append(d)

    @property
    def latest(self):
        return self.d[-1]

    @property
    def mean(self):
        try:
            return np.mean(self.d)
        except ValueError:
            return None

    @property
    def max(self):
        try:
            return np.max(self.d)
        except ValueError:
            return None

    @property
    def min(self):
        try:
            return np.min(self.d)
        except ValueError:
            return None


class Color:
    # noinspection PyInitNewSignature
    def __init__(self, value, color=None, formatter: Union[Callable[[Any], Any], None] = lambda v: v):
        self.value = value
        self.color = color
        self.formatter = formatter

    def __str__(self):
        return str(self.formatter(self.value)) if callable(self.formatter) else str(self.value)

    def __len__(self):
        return len(str(self.value))

    def __format__(self, format_spec):
        if self.color in [None, 'default']:
            return self.formatter(self.value).__format__(format_spec)
        else:
            return c(self.formatter(self.value).__format__(format_spec), self.color)


def percent(v):
    return f'{round(v * 100):.1f}%'


def ms(v):
    return f'{v*1000:.1f}ms'


def sec(v):
    return f'{v:.3f}s'


def default(value, *args, **kwargs):
    return Color(value, 'default', *args, **kwargs)


def red(value, *args, **kwargs):
    return Color(value, 'red', *args, **kwargs)


def green(value, *args, **kwargs):
    return Color(value, 'green', *args, **kwargs)


def gray(value, *args, **kwargs):
    return Color(value, 'gray', *args, **kwargs)


def grey(value, *args, **kwargs):
    return Color(value, 'gray', *args, **kwargs)


def yellow(value, *args, **kwargs):
    return Color(value, 'yellow', *args, **kwargs)


def brown(value, *args, **kwargs):
    return Color(value, 'brown', *args, **kwargs)


class ML_Logger:
    logger = None

    # noinspection PyInitNewSignature
    def __init__(self, log_directory: str = None, prefix=""):
        # self.summary_writer = tf.summary.FileWriter(log_directory)
        self.step = None
        self.data = OrderedDict()
        self.do_not_print_list = set()
        assert not os.path.isabs(prefix), "prefix can not start with `/`"
        self.prefix = prefix

        # todo: add https support
        if log_directory:
            self.logger = LogClient(url=log_directory)

    configure = __init__

    @property
    def log_directory(self):
        return self.logger.local_server.data_dir if self.logger else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.summary_writer.close()
        # todo: wait for logger to finish upload in async mode.
        self.flush()

    def log_params(self, **kwargs):
        key_width = 30
        value_width = 20

        table = []
        for n, (title, section_data) in enumerate(kwargs.items()):
            table.append((title, ""))
            print('═' * (key_width + 1) + f"{'═' if n == 0 else '╧'}" + '═' * (value_width + 1))
            print(c(f'{title:^{key_width}}', 'yellow'))
            print('─' * (key_width + 1) + "┬" + '─' * (value_width + 1))
            for key, value in section_data.items():
                value_string = str(value)
                table.append((key, value_string))
                print(c(f'{key:^{key_width}}', 'white'), "│", f'{value_string:<{value_width}}')

        if "n" in locals():
            print('═' * (key_width + 1) + f"{'═' if n == 0 else '╧'}" + '═' * (value_width + 1))

        # todo: add logging hook
        # todo: add yml support
        self.logger.log(key=os.path.join(self.prefix, "parameters.pkl"), data=kwargs)

    def log_keyvalue(self, step: Union[int, Color], key: str, value: Any, silent=False) -> None:
        if self.step != step and self.step is not None:
            self.flush()
        self.step = step
        self.timestamp = np.datetime64(datetime.now())

        if silent:
            self.do_not_print_list.update([key])

        # todo: add logging hook
        self.data[key] = value.value if type(value) is Color else value

    def log(self, step: Union[int, Color], *dicts, silent=False, **kwargs) -> None:
        """
        :param step: the global step, be it the global timesteps or the epoch step
        :param dicts: a dictionary of key/value pairs, allowing more flexible key name with '/' etc.
        :param silent: Bool, log but do not print. To keep the standard out silent.
        :param kwargs: key/value arguments.
        :return:
        """
        if self.step != step and self.step is not None:
            self.flush()
        self.step = step
        self.timestamp = np.datetime64(datetime.now())

        data_dict = {}
        for d in dicts:
            data_dict.update(d)
        data_dict.update(kwargs)

        if silent:
            self.do_not_print_list.update(data_dict.keys())

        # todo: add logging hook
        for key, v in data_dict.items():
            self.data[key] = v.value if type(v) is Color else v

    def flush(self, min_key_width=20, min_value_width=20):
        if not self.data:
            return

        keys = [k for k in self.data.keys() if k not in self.do_not_print_list]

        if len(keys) > 0:
            max_key_len = max([min_key_width] + [len(k) for k in keys])
            max_value_len = max([min_value_width] + [len(str(self.data[k])) for k in keys])
            output = None
            for k in keys:
                v = str(self.data[k])
                if output is None:
                    output = "╒" + "═" * max_key_len + "╤" + "═" * max_value_len + "╕\n"
                else:
                    output += "├" + "─" * max_key_len + "┼" + "─" * max_value_len + "┤\n"
                if k not in self.do_not_print_list:
                    k = k.replace('_', " ")
                    v = "None" if v is None else v  # for NoneTypes which doesn't have __format__ method
                    output += f"│{k:^{max_key_len}}│{v:^{max_value_len}}│\n"
            output += "╘" + "═" * max_key_len + "╧" + "═" * max_value_len + "╛\n"
            print(output, end="")

        self.logger.log(key=os.path.join(self.prefix, "data.pkl"),
                        data=dict(_step=self.step, _timestamp=self.timestamp, **self.data))
        self.data.clear()
        self.do_not_print_list.clear()

    def log_image(self, step, namespace="plots", **kwargs):
        """Logs an image via the summary writer.
        TODO: add support for PIL images etc.
        reference: https://gist.github.com/gyglim/1f8dfb1b5c82627ae3efcfbbadb9f514
        """
        if self.step != step and self.step is not None:
            self.flush()
        self.step = step

        # todo: save image hook here
        for key, image in kwargs.items():
            self.logger.send_image(key=os.path.join(self.prefix, namespace, key, f"{step:04d}.png"), data=image)

    def log_json(self):
        raise NotImplementedError

    def log_text(self, text, filename="print.txt"):
        print(text)
        self.logger.log_text(key=os.path.join(self.prefix, filename), text=text)


logger = ML_Logger()
