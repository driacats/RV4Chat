#/bin/python
# Author: Andrea Gatti

from aiohttp import web
import curses, threading, requests, asyncio, time, json

# The function creates two window:
# - chat_win: a window that displays the conversation
# - input_win: a window that takes user input
def create_windows():
    chat_win = curses.newwin(curses.LINES - 3, curses.COLS, 0, 0)
    chat_win.box()
    chat_win.refresh()

    input_win = curses.newwin(3, curses.COLS, curses.LINES - 3, 0)
    input_win.box()
    input_win.refresh()

    return chat_win, input_win

# The function frees n lines at the bottom of the conversation
# creating the space for the new message.
def free_lines(win, n):
    max_y, max_x = win.getmaxyx()
    # Move each line n lines above
    for y in range(n+1, max_y-1):
        line = win.instr(y, 1, max_x-2).decode('utf-8')
        win.addstr(y, 1, ' ' * (max_x-2))
        win.addstr(y-n, 1, line)
    # Empty the n bottom lines
    for y in range(max_y-n, max_y-1):
        win.addstr(y, 1, ' ' * (max_x-2))

# The function handles the user input
def user_msg(win, msg):
    max_y, max_x = win.getmaxyx()
    free_lines(win, 1)
    # Add the message to the chat
    win.addstr(max_y - 2, 1, 'USER: ' + msg)
    win.refresh()
    
    # Make the request at the chatbot for the answer and it handles it
    service_url = "http://0.0.0.0:5005/webhooks/rest/webhook"
    req = {}
    req['sender'] = 'user'
    req['message'] = msg
    answer = requests.post(service_url, json=req)
    answer = json.loads(answer.text)
    bot_msg(win, answer[0]['text'])

# The function handles bot messages
def bot_msg(win, msg):
    max_y, max_x = win.getmaxyx()
    # If the message is longer than one line it trims it and frees n lines
    msgs = trim_msg(msg, max_x - 9)
    msgs[0] = 'BOT: ' + msgs[0]
    free_lines(win, len(msgs))
    # Add the message on the chat
    for i, ms in enumerate(msgs):
        win.addstr(max_y - 1 - (len(msgs) - i), 1, ms)

    win.refresh()

# Creates a list of strings all with max length n
def trim_msg(msg, n):
    return [msg[i:i+n] for i in range(0, len(msg), n)]

# The function allows the user input capture.
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
                win.box()
                win.refresh()
        elif len(user_input) < curses.COLS - 9:
            user_input += chr(ch)
            win.addch(1, win.getyx()[1], ch)

# Handle POST is the callback function for POST requests
# It simply calls the correct msg handler function
# and sends back a 200 OK
async def handle_post(chat_win, request):
    data = await request.json()
    if (data['sender'] == 'user'):
        user_msg(chat_win, data['msg'])
    elif (data['sender'] == 'bot'):
        bot_msg(chat_win, data['msg'])
    return web.Response(status=200)

# The function loops on the user input
# Gets the message and makes a POST request to the chat_win
def handle_user_input(stdscr, input_win):
    try:
        while True:
            input_win.addstr(1, 2, "> ")
            input_win.refresh()
            user_input = get_user_input(input_win)
            requests.post('http://localhost:8888', json={'sender': 'user', 'msg': user_input})
            input_win.addstr(1, 2, " " * (curses.COLS - 5))
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
    
    # The user input is handled in a subthread
    threading.Thread(target=handle_user_input, args=(stdscr, input_win)).start()

    # Launch the POST server
    app = web.Application()
    app.add_routes([(web.post('/', lambda request : handle_post(chat_win, request)))])
    web.run_app(app, port=8888, print=False)

if __name__ == '__main__':
    curses.wrapper(main)