import curses, urllib3, json, requests, threading
from aiohttp import web

class Visualize:

    def init_curses(self):
        stdscr = curses.initscr()
        curses.cbreak()
        stdscr.keypad(True)
        curses.echo()
        return stdscr

    # def init_listener(self, listener):
    #     self.listener = listener

    def create_windows(self):
        chat_win = curses.newwin(curses.LINES - 3, curses.COLS, 0, 0)
        chat_win.box()
        chat_win.refresh()

        input_win = curses.newwin(3, curses.COLS, curses.LINES - 3, 0)
        input_win.box()
        input_win.refresh()

        return chat_win, input_win

    def get_window_strings(self, win):
        max_y, max_x = win.getmaxyx()
        strings = []

        for y in range(6, max_y-1):
            line = win.instr(y, 1, max_x-2).decode('utf-8')
            if not line.isspace():
                strings.append(line.rstrip('\n'))

        strings.reverse()

        return strings

    def user_msg(self, win, msg):
        max_y, max_x = win.getmaxyx()
        msgs = self.get_window_strings(win)
        for i, m in enumerate(msgs):
            win.addstr(max_y - i - 3, 1, m)
        win.addstr(max_y - 2, 1, ' ' * (max_x - 2))
        win.addstr(max_y - 2, 1, 'USER: ' + msg)
        win.refresh()

    def bot_msg(self, win, msg):
        max_y, max_x = win.getmaxyx()
        msgs = self.get_window_strings(win)
        if len(msg) > max_x:
            msg_1 = msg[:max_x-9]
            msg_2 = msg[max_x-9:]
            for i, m in enumerate(msgs):
                win.addstr(max_y - i - 3 - 1, 1, m)
            win.addstr(max_y - 2 - 1, 1, 'BOT: ' + str(msg_1))
            win.addstr(max_y - 2, 1, '    ' + str(msg_2))
        else:
            for i, m in enumerate(msgs):
                win.addstr(max_y - i - 3, 1, m)
            win.addstr(max_y - 2, 1, ' ' * (max_x - 2))
            win.addstr(max_y - 2, 1, 'BOT: ' + msg)
        win.refresh()

    def handle_bot_input(self, msg):
        self.bot_msg(self.chat_win, msg)

    def get_user_input(self, win):
        user_input = ''
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

    async def handle_bot_messages(self, request):
        data = await request.json()
        msg = data.get('message')
        self.bot_msg(self.chat_win, msg)
        return web.Response(text='Message received by the bot')

    async def start_server(self):
        app = web.Application()
        app.router.add_post('/bot', self.handle_bot_messages)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8888)
        await site.start()

    def main(self, stdscr):
        chat_win, input_win = self.create_windows()
        self.chat_win = chat_win
        threading.Thread(target=self.start_server, daemon=True).start()
        try:
            while True:
                input_win.addstr(1, 2, "> ")
                input_win.refresh()
                user_input = self.get_user_input(input_win)
                self.user_msg(chat_win, user_input)
                input_win.addstr(1, 2, " " * (curses.COLS - 5))  # Pulisce la riga dell'input
                input_win.refresh()
                answer = self.listener.handle_user_input(user_input)
                self.bot_msg(chat_win, answer)
        except KeyboardInterrupt:
            pass
        finally:
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()

class Listener:

    # service = urllib3.PoolManager()

    # service_url = 'http://0.0.0.0:5005'
    service_url = "http://0.0.0.0:5005/webhooks/rest/webhook"
    # my_url = 'http://localhost:8888'

    def init_visualize(self, vs):
        self.vs = vs

    def handle_user_input(self, msg):
        request = {'sender': 'user', 'message': msg}
        # answer = self.service.request('POST', self.service_url, body=json.dumps(request))
        answer = requests.post(self.service_url, json=request)
        answer = answer.text
        answer = json.loads(answer)

        return answer[0]['text']

    async def handle_bot_input(self, request):
        data = await request.json()
        data = data['message']
        self.vs.handle_bot_input(json.dumps(data))
       
    def listen(self):
        app = web.Application()
        app.add_routes([(web.post('/', self.handle_bot_input))])
        web.run_app(app, port=8888)


if __name__ == '__main__':
    vs = Visualize()

    # listener = Listener()

    # vs.init_listener(listener)
    # listener.init_visualize(vs)
    # interface = threading.Thread(target=curses.wrapper(vs.main), daemon=True)
    # interface.start()
    # engine = threading.Thread(target=listener.listen(), daemon=True)
    # engine.start()
    curses.wrapper(vs.main)

    # interface.join()
    # engine.join()
