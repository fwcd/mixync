from mixync.options import Options

RED_COLOR = '\033[91m'
YELLOW_COLOR = '\033[93m'
BLUE_COLOR = '\033[36m'
GRAY_COLOR = '\033[90m'
GREEN_COLOR = '\033[92m'
PINK_COLOR = '\033[95m'
CLEAR_COLOR = '\033[0m'

def message(msg: str, color: str=BLUE_COLOR):
    print(f'{color}==> {msg}{CLEAR_COLOR}')

def info(msg: str):
    message(msg, BLUE_COLOR)

def prompt(msg: str, choices: list[str], default: str, opts: Options):
    if opts.assume_yes:
        return default

    aliases = {}
    option_strs = []

    if choices:
        for choice in choices:
            i = 1
            while choice[:i] in aliases.keys():
                i += 1
            aliases[choice[:i]] = choice
            option_strs.append(f'[{choice[:i]}]{choice[i:]}')

    choices_str = f" - {', '.join(option_strs)}"
    response = input(f'{msg}{choices_str} ')

    return aliases.get(response, response)

def confirm(msg: str, opts: Options):
    response = prompt(msg, ['yes', 'no'], 'yes', opts)
    return response == 'yes'
