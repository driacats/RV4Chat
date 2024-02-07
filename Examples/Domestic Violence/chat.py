import curses

class Chat:

    last_msg_y = 1

    def init_curses(self):
        stdscr = curses.initscr()
        curses.cbreak()
        stdscr.keypad(True)
        curses.echo()
        return stdscr

    def create_windows(self):
        upper_win = curses.newwin(curses.LINES - 3, curses.COLS, 0, 0)
        upper_win.box()
        upper_win.refresh()

        lower_win = curses.newwin(3, curses.COLS, curses.LINES - 3, 0)
        lower_win.box()
        lower_win.refresh()

        return upper_win, lower_win

    def user_msg(self, win, msg):
        max_y, max_x = win.getmaxyx()
        win.addstr(self.last_msg_y, 1, "USER: " + msg)
        # win.addstr("\n")  # Aggiunge una nuova linea dopo il messaggio
        self.last_msg_y += 1
        win.refresh()
        

    def bot_msg(self, win, msg):
        max_y, max_x = win.getmaxyx()
        win.addstr(self.last_msg_y, max_x - len("BOT: " + msg) - 1, "BOT: " + msg)
        # win.addstr("\n")  # Aggiunge una nuova linea dopo il messaggio
        self.last_msg_y += 1
        win.refresh()

    def get_user_input(self, win):
        user_input = ""
        while True:
            ch = win.getch()
            if ch == ord('\n'):
                return user_input
            elif ch == curses.KEY_BACKSPACE or ch == 127:
                if user_input:
                    user_input = user_input[:-1]
                    win.delch(1, win.getyx()[1] - 1)
            elif len(user_input) < curses.COLS - 9:
                user_input += chr(ch)
                win.addch(1, win.getyx()[1], ch)

    def main(self, stdscr):
        upper_win, lower_win = self.create_windows()
        try:
            while True:
                lower_win.addstr(1, 2, "> ")
                lower_win.refresh()
                user_input = self.get_user_input(lower_win)
                self.user_msg(upper_win, user_input)
                lower_win.addstr(1, 2, " " * (curses.COLS - 5))  # Pulisce la riga dell'input
                lower_win.refresh()
                self.bot_msg(upper_win, "This is a response from the bot.")
        except KeyboardInterrupt:
            pass
        finally:
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()

class Engine:

    service = urllib3.PoolManager()

    service_url = 'http://localhost:8084'
    my_url = 'http:localhost:8888'

    def handle_user_input(self, msg):
        answer = service.request('POST', service_url, msg)
        return answer

    def handle_bot_input(self, msg):
        pass

if __name__ == "__main__":
    chat = Chat()
    curses.wrapper(chat.main)
