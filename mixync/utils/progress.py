class ProgressLine:
    """An abstraction for printing an updating progress line."""

    def __init__(self, total: int, with_bar: bool=True, bar_length: int=10, final_newline: bool=True):
        self.i = 0
        self.total = total
        self.last_msg = ''
        self.with_bar = with_bar
        self.bar_length = bar_length
        self.final_newline = final_newline
    
    def __enter__(self):
        return self
    
    def __exit__(self, t, v, tb):
        if self.final_newline:
            print()

    def print(self, msg: str):
        progress = (self.i + 1) / self.total
        steps = int(progress * self.bar_length)
        bar = f"[{'█' * steps + '░' * (self.bar_length - steps)}]" if self.with_bar else ''
        output = ' '.join(s for s in [
            bar,
            f'[{self.i + 1}/{self.total}]',
            msg,
            ' ' * (len(self.last_msg) - len(msg)),
        ] if s)
        print(f'\r{output}', end='', flush=True)
        self.last_msg = msg
        self.i += 1
