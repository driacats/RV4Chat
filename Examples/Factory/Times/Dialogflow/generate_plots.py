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
colors = ['red', 'blue', 'teal']

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
                        t.header.append(float(info_line[0])/10)
                        t.intent.append(float(info_line[1])/10)
                        t.perform.append(float(info_line[2])/10)
                        t.bot.append(float(info_line[3])/10)
                        t.total.append(float(info_line[4])/10)
                    else:
                        t.total.append(float(info_line[0])/10)
        times_list.append(t)
        couples = [(i+1, t1) for i, t1 in enumerate(t.total)]
        print("\draw [" + color + "!20!white] plot [smooth, tension=1] coordinates {" + str(couples).replace("[", "").replace("]", "").replace("),", ")") + " };")
    
    # print("\draw [" + color + "] plot [smooth, tension=1] coordinates {", end="")
    # t_aux = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    t_real = {}
    for it in times_list:
        for i in range(6):
            if i not in t_real:
                t_real[i] = []
            v = it.get_iteration(i)
            if type(v) == list:
                # t_aux[i] += v[-1]
                t_real[i].append(v[-1])
            else:
                # t_aux[i] += v
                t_real[i].append(v)
    # for i in range(6):
    #     # print(t_aux[i])
    #     print((i+1, round(t_aux[i] / 10, 3)), end="")
    # print("};")
        
    # print(t_real)
    print("\draw [" + color + "] plot [smooth, tension=1, mark=*] coordinates {", end="")
    for i in t_real:
        # t_real[i].remove(max(t_real[i]))
        # t_real[i].remove(min(t_real[i]))
        avg = round(sum(t_real[i]) / len(t_real[i]), 3)
        print((i+1, avg), end="")
    print("};")