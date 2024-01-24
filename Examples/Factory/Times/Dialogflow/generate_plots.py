import os

class times:
    header = []
    intent = []
    perform = []
    bot = []
    total = []

    def __init__(self):
        self.header = []
        self.intent = []
        self.perform = []
        self.bot = []
        self.total = []


    def get_iteration(self, i):
        if len(self.header) > 0:
            return [self.header[i], self.intent[i], self.perform[i], self.bot[i], self.total[i]]
        else:
            return self.total[i]

folders = ['./no-monitor/', './dummy-monitor/', './real-monitor/']
colors = ['red', 'blue', 'green']

# times_list = {}
for folder, color in zip(folders, colors):
    # print(folder, color)
    print("\n")
    # times_list[folder] = []
    times_list = []
    for f in os.listdir(folder):
        t = times()
        with open(os.path.join(folder, f), 'r') as csv:
            for line in csv:
                info_line = line.replace('\n', '').split(',')
                if not (info_line[0] == "header" or info_line[0] == "total"):
                    if len(info_line) > 1:
                        t.header.append(float(info_line[0]))
                        t.intent.append(float(info_line[1]))
                        t.perform.append(float(info_line[2]))
                        t.bot.append(float(info_line[3]))
                        t.total.append(float(info_line[4]))
                    else:
                        t.total.append(float(info_line[0]))
        times_list.append(t)
        couples = [(i+1, t1) for i, t1 in enumerate(t.total)]
        print("\draw [" + color + "!20!white] plot [smooth, tension=1] coordinates {" + str(couples).replace("[", "").replace("]", "").replace("),", ")") + " };")
    
    print("\draw [" + color + "] plot [smooth, tension=1] coordinates {", end="")
    t_aux = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    for it in times_list:
        for i in range(6):
            v = it.get_iteration(i)
            if type(v) == list:
                t_aux[i] += v[-1]
            else:
                t_aux[i] += v
    for i in range(6):
        # print(t_aux[i])
        print((i+1, round(t_aux[i] / 10, 3)), end="")
    print("};")
        
        # print(it.get_iteration(0))

# print(t.get_total_avg())