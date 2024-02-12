from aiohttp import web
import curses, logging, threading, requests, asyncio, time, json

def create_windows():
    chat_win = curses.newwin(curses.LINES - 3, curses.COLS, 0, 0)
    chat_win.box()
    chat_win.refresh()

    input_win = curses.newwin(3, curses.COLS, curses.LINES - 3, 0)
    input_win.box()
    input_win.refresh()

    return chat_win, input_win

def get_window_strings(win):
    max_y, max_x = win.getmaxyx()
    strings = []

    for y in range(6, max_y-1):
        line = win.instr(y, 1, max_x-2).decode('utf-8')
        if not line.isspace():
            strings.append(line.rstrip('\n'))

    strings.reverse()

    return strings

def user_msg(win, msg):
    max_y, max_x = win.getmaxyx()
    # msgs = get_window_strings(win)
    # for i, m in enumerate(msgs):
    #     win.addstr(max_y - i - 3, 1, m)
    free_lines(win, 1)
    win.addstr(max_y - 2, 1, ' ' * (max_x - 2))
    win.addstr(max_y - 2, 1, 'USER: ' + msg)
    win.refresh()
    # requests.post('http://localhost:8080', msg)
    service_url = "http://0.0.0.0:5005/webhooks/rest/webhook"
    req = {}
    req['sender'] = 'user'
    req['message'] = msg
    answer = requests.post(service_url, json=req)
    answer = json.loads(answer.text)
    bot_msg(win, answer[0]['text'])

def free_lines(win, n):
    max_y, max_x = win.getmaxyx()
    for i in range(5+n, max_y-1-n):
        i_line = win.instr(i, 1, max_x-2).decode('utf-8')
        win.addstr(i-1, 1, i_line)
    for i in range(max_y-1-n, max_y-1):
        win.addstr(i, 1, ' ' * (max_x - 6))

# def bot_msg(self, win, msg):
#     max_y, max_x = win.getmaxyx()
#     # msgs = self.get_window_strings(win)

#     if len(msg) > max_x:
#         msg_1 = msg[:max_x-9]
#         msg_2 = msg[max_x-9:]
#         for i, m in enumerate(msgs):
#             win.addstr(max_y - i - 3 - 1, 1, m)
#         win.addstr(max_y - 2 - 1, 1, 'BOT: ' + str(msg_1))
#         win.addstr(max_y - 2, 1, '    ' + str(msg_2))
#     else:
#         for i, m in enumerate(msgs):
#             win.addstr(max_y - i - 3, 1, m)
#         win.addstr(max_y - 2, 1, ' ' * (max_x - 2))
#         win.addstr(max_y - 2, 1, 'BOT: ' + msg)
#     win.refresh()

def bot_msg(win, msg):
    max_y, max_x = win.getmaxyx()
    msgs = trim_msg(msg, max_x - 9)
    msgs[0] = 'BOT: ' + msgs[0]
    free_lines(win, len(msgs))
    for i, ms in enumerate(msgs):
        win.addstr(max_y - 1 - (len(msgs) - i), 1, ms)

    win.refresh()

def trim_msg(msg, n):
    return [msg[i:i+n] for i in range(0, len(msg), n)]

def get_user_input(win):
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

async def handle_post(chat_win, request):
    data = await request.json()
    if (data['sender'] == 'user'):
        user_msg(chat_win, data['msg'])
    elif (data['sender'] == 'bot'):
        bot_msg(chat_win, data['msg'])
    return web.Response(status=200)

def handle_user_input(stdscr, input_win):
    try:
        while True:
            input_win.addstr(1, 2, "> ")
            input_win.refresh()
            user_input = get_user_input(input_win)
            requests.post('http://localhost:8888', json={'sender': 'user', 'msg': user_input})
            input_win.addstr(1, 2, " " * (curses.COLS - 5))  # Pulisce la riga dell'input
            input_win.refresh()
            
    except KeyboardInterrupt:
        pass
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

def main(stdscr):
    chat_win, input_win = create_windows()

    threading.Thread(target=handle_user_input, args=(stdscr, input_win)).start()

    logging.basicConfig(level=logging.WARNING)
    app = web.Application()
    app.add_routes([(web.post('/', lambda request : handle_post(chat_win, request)))])
    web.run_app(app, port=8888, print=False)

if __name__ == '__main__':
    curses.wrapper(main)