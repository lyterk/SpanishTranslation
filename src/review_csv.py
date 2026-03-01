from pynput import keyboard as kb


def on_press(key):
    print(type(key))
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    if key == kb.Key.esc:
        # Stop listener
        return False

DIRECTIONS = {"up": "\x1b[A", "down": "\x1b[B", "left": "\x1b[D", "right": "\x1b[C"}
