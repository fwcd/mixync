from re import A


class ProgressLine:
    """An abstraction for printing an updating progress line."""

    def __init__(self, total: int, with_bar: bool=True, bar_length: int=10, final_newline: bool=True):
        self.i = 0
        self.total = total
        self.last_msg = ''
        self.msg = ''
        self.with_bar = with_bar
        self.bar_length = bar_length
        self.final_newline = final_newline
    
    def __enter__(self):
        return self
    
    def __exit__(self, t, v, tb):
        if self.final_newline:
            print()

    def prefix(self):
        progress = (self.i + 1) / self.total
        steps = int(progress * self.bar_length)
        bar = f"[{'█' * steps + '░' * (self.bar_length - steps)}]" if self.with_bar else ''
        return f'{bar} [{self.i + 1}/{self.total}]'

    def current(self):
        return ' '.join(s for s in [
            self.prefix(),
            self.msg,
            ' ' * (len(self.last_msg) - len(self.msg)),
        ] if s)

    def update(self, msg: str):
        self.last_msg = self.msg
        self.msg = msg
        self.i += 1
        print(f'\r{self.current()}', end='', flush=True)
    
    def print(self, msg: str):
        print(f"\r{msg}{' ' * (len(self.last_msg) - len(msg))}\n{self.current()}", end='', flush=True)
        self.last_msg = msg
