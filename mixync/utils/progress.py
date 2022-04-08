class ProgressLine:
    """An abstraction for printing an updating progress line."""

    def __init__(self, total: int, final_newline: bool=True):
        self.i = 0
        self.total = total
        self.last_msg = ''
        self.final_newline = final_newline
    
    def __enter__(self):
        return self
    
    def __exit__(self, t, v, tb):
        if self.final_newline:
            print()

    def print(self, msg: str):
        print(f'\r[{self.i + 1}/{self.total}] {msg}' + ' ' * (len(self.last_msg) - len(msg)), end='', flush=True)
        self.last_msg = msg
        self.i += 1
