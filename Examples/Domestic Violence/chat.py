import threading, queue, curses
from aiohttp import web

class Chat:

    PORT = 8888

    def init_curses(self):
        stdscr = curses.initscr()
        curses.cbreak()
        stdscr.keypad(True)
        curses.echo()
        return stdscr

    def create_windows(self):
        # self.stdscr = self.init_curses()

        self.chat_win = curses.newwin(curses.LINES - 3, curses.COLS, 0, 0)
        self.chat_win.box()
        self.chat_win.refresh()

        self.input_win = curses.newwin(3, curses.COLS, curses.LINES - 3, 0)
        self.input_win.box()
        self.input_win.refresh()

    def get_window_strings(self):
        max_y, max_x = self.chat_win.getmaxyx()
        strings = []

        for y in range(6, max_y-1):
            line = self.chat_win.instr(y, 1, max_x-2).decode('utf-8')
            if not line.isspace():
                strings.append(line.rstrip('\n'))

        strings.reverse()

        return strings

    def user_msg(self, msg):
        max_y, max_x = self.chat_win.getmaxyx()
        msgs = self.get_window_strings()
        for i, m in enumerate(msgs):
            self.chat_win.addstr(max_y - i - 3, 1, m)
        self.chat_win.addstr(max_y - 2, 1, ' ' * (max_x - 2))
        self.chat_win.addstr(max_y - 2, 1, 'USER: ' + msg)
        self.chat_win.refresh()

    def bot_msg(self, msg):
        max_y, max_x = self.chat_win.getmaxyx()
        msgs = self.get_window_strings(self.chat_win)
        if len(msg) > max_x:
            msg_1 = msg[:max_x-9]
            msg_2 = msg[max_x-9:]
            for i, m in enumerate(msgs):
                self.chat_win.addstr(max_y - i - 3 - 1, 1, m)
            self.chat_win.addstr(max_y - 2 - 1, 1, 'BOT: ' + str(msg_1))
            self.chat_win.addstr(max_y - 2, 1, '    ' + str(msg_2))
        else:
            for i, m in enumerate(msgs):
                self.chat_win.addstr(max_y - i - 3, 1, m)
            self.chat_win.addstr(max_y - 2, 1, ' ' * (max_x - 2))
            self.chat_win.addstr(max_y - 2, 1, 'BOT: ' + msg)
        self.chat_win.refresh()

    def handle_bot_input(self, msg):
        self.bot_msg(self.chat_win, msg)

    def get_user_input(self):
        user_input = ''
        while True:
            ch = self.input_win.getch()
            if ch == ord('\n'):
                return user_input
            elif ch == curses.KEY_BACKSPACE or ch == 127:
                if user_input:
                    user_input = user_input[:-1]
                    self.input_win.delch(1, self.input_win.getyx()[1] - 1)
            elif len(user_input) < curses.COLS - 9:
                user_input += chr(ch)
                self.input_win.addch(1, self.input_win.getyx()[1], ch)
    
    def run(self, stdscr):
        self.create_windows()
        try:
            while True:
                self.input_win.addstr(1, 2, "> ")
                self.input_win.refresh()
                user_input = self.get_user_input()
                self.user_msg(user_input)
                self.input_win.addstr(1, 2, " " * (curses.COLS - 5))  # Pulisce la riga dell'input
                self.input_win.refresh()
                # answer = self.listener.handle_user_input(user_input)
                # self.bot_msg(answer)
        except KeyboardInterrupt:
            pass
        finally:
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()

def run_chat(chat):
    curses.wrapper(chat.run)

def main():
    # print('Welcome to the chat.')
    chat = Chat()
    # curses.wrapper(chat.run)
    threading.Thread(target=run_chat(chat)).start()
    # threading.Thread(target=visualize).start()

if __name__ == '__main__':
    main()
