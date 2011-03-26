import os
import os.path
import sys
import re

def fail():
    print('FAIL')
    exit(1)

class Screen(object):
    def __init__(self, name):
        self._displays = []
        self._name = name

    def __str__(self):
        return "Screen (%s, %s)" % (self._name, map(str, self._displays))

    def add_display(self, display):
        self._displays.append(display)

class Display(object):
    def __init__(self, name):
        self._modes = []
        self._name = name

    def __str__(self):
        return "Display (%s, %s)" % (self._name, map(str, self._modes))

    def add_mode(self, mode):
        self._modes.append(mode)

    def get_best_mode(self):
        best_mode = None
        for mode in self._modes:
            if (not best_mode) or mode._res[0] > best_mode._res[0]:
                best_mode = mode
        return best_mode

    def use_mode(self, mode):
        yield '--output'
        yield self._name
        yield '--mode'
        yield '%sx%s' % (mode._res[0], mode._res[1])

class Mode(object):
    def __init__(self, res):
        self._res = map(int, res)

    def __str__(self):
        return "Mode (%s)" % str(self._res)

def run_xrandr(args):
    os.system("xrandr %s" % " ".join(args))

def parse_xrandr_output(output):
    screen_form = r'^Screen ([0-9]+): minimum ([0-9]+) x ([0-9]+), current ([0-9]+) x ([0-9]+), maximum ([0-9]+) x ([0-9]+)$'
    display_form = r'^([A-Z0-9]+) connected (?:([0-9]+)x([0-9]+))?.*$'
    mode_form = r'^ {3}([0-9]+)x([0-9]+).*$'
    screens = []
    current_screen = None
    current_display = None
    current_mode = None
    for line in output:
        screen_match = re.match(screen_form, line)
        display_match = re.match(display_form, line)
        mode_match = re.match(mode_form, line)
        if screen_match:
            groups = screen_match.groups()
            current_screen = Screen(groups[0])
            screens.append(current_screen)
        elif display_match:
            groups = display_match.groups()
            current_display = Display(groups[0])
            current_screen.add_display(current_display)
        elif mode_match:
            groups = mode_match.groups()
            current_mode = Mode((groups[0], groups[1]))
            current_display.add_mode(current_mode)
        else:
            print("Unknown line '%s'" % line[:-1])
    return screens

def fetch_display_order(display_names):
    try:
        pref_displays = list(open(os.path.join(os.environ['HOME'], '.asc-order')))
        def get_key(name):
            for (i, pref_display) in zip(range(len(pref_displays)), pref_displays):
                pref_display = pref_display[:-1]
                if pref_display and re.search(pref_display, name):
                    return i
            return 42
        return sorted(display_names, key = get_key)
    except IOError:
        return display_names
        

def set_display_order(display_names):
    first = display_names[0]
    for second in display_names[1:]:
        yield '--output'
        yield first
        yield '--left-of'
        yield second

def main():
    xrandr_args = []
    xrandr_output = list(os.popen('xrandr'))
    data = parse_xrandr_output(xrandr_output)
    screen = data[0]
    for display in screen._displays:
        best_mode = display.get_best_mode()
        xrandr_args += display.use_mode(best_mode)
    display_names = map(lambda(d): d._name, screen._displays)
    display_names = fetch_display_order(display_names)
    xrandr_args += set_display_order(display_names)
    if len(sys.argv) < 2:
        print('Need argument.')
        exit(1)
    action = sys.argv[1]
    if action == 'set-best':
        run_xrandr(xrandr_args)
    elif action == 'list-displays':
        for display in display_names:
            print(display)
    else:
        print('Unknown action.')
        exit(1)

main()
