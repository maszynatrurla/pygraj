#!/usr/bin/env python

import os
import os.path
import cmd
import time

GPIO_Z = 4
GPIO_S = (22, 23, 6, 24)
GPIO_INT = 5

DEV_GPIO_LOC = "/sys/class/gpio"

def gpio_file(gpio, fname):
    return os.path.join(DEV_GPIO_LOC, "gpio" + str(gpio), fname)

def psztyk_init():
    try:
        with open(os.path.join(DEV_GPIO_LOC, "export"), "w") as fp:
            fp.write(str(GPIO_Z))
    except IOError:
        pass

    try:
        with open(os.path.join(DEV_GPIO_LOC, "export"), "w") as fp:
            fp.write(str(GPIO_INT))
    except IOError:
        pass

    for s_gpio in GPIO_S:
        try:
            with open(os.path.join(DEV_GPIO_LOC, "export"), "w") as fp:
                fp.write(str(s_gpio))
        except IOError:
            pass
    
    with open(gpio_file(GPIO_Z, "direction"), "w") as fp:
        fp.write("in")

    with open(gpio_file(GPIO_INT, "direction"), "w") as fp:
        fp.write("in")

    for s_gpio in GPIO_S:
        with open(gpio_file(s_gpio, "direction"), "w") as fp:
            fp.write("out")

def psztyk_setmux(snum):
    for bit in range(len(GPIO_S)):
        gpio = GPIO_S[bit]
        value = "1" if ((snum & (1 << bit)) != 0) else "0"
        with open(gpio_file(gpio, "value"), "w") as fp:
            fp.write(value)

def psztyk_get(snum = None):
    if snum is not None:
        psztyk_setmux(snum)
    with open(gpio_file(GPIO_Z, "value")) as fp:
        value = fp.read().strip()
        return value

def psztyk_get_int():
    with open(gpio_file(GPIO_INT, "value")) as fp:
        value = fp.read().strip()
        return value

class InteractivePlay(cmd.Cmd):
    intro = "Interactive app. Type help or ? to list commands.\n"
    prompt = "(psztyk)>"

    def do_get(self, args):
        button = None
        try:
            button = int(args.split()[0])
        except:
            pass
        print(psztyk_get(button))

    def do_gint(self, args):
        print(psztyk_get_int())

    def do_iloop(self, args):
        arr = args.split()
        cnt = int(arr[0])
        delay = .5
        if len(arr) > 1:
            delay = float(arr[1])
        for i in range(cnt):
            print(psztyk_get_int())
            time.sleep(delay)

    def do_set(self, args):
        button = int(args.split()[0])
        psztyk_setmux(button)
        print("OK")

    def do_loop(self, args):
        arr = args.split()
        cnt = int(arr[0])
        delay = .5
        if len(arr) > 1:
            delay = float(arr[1])
        for i in range(cnt):
            print(psztyk_get())
            time.sleep(delay)

    def do_EOF(self, args):
        return True

def main():
    psztyk_init()
    #app = InteractivePlay()
    #app.cmdloop()

if __name__ == "__main__":
    main()


