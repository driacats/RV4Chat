import os

folders = ['./no-monitor/', './dummy-monitor/', './real-monitor/']
colors = ['red', 'blue', 'teal']

plot_str = "\draw[COLOR] plot [smooth, tension=1] coordinates { "
plot_avg_str = "\draw[COLOR] plot [smooth, tension=1, mark=*] coordinates { "

all_times = {}
for folder in folders:
    times = {}
    for f in os.listdir(folder):
        with open(os.path.join(folder, f), 'r') as t:
            lines = t.readlines()
            for i in range(6):
                if i not in times:
                    times[i] = []
                ts = (float(lines[i*2+1].split(']')[1]) - float(lines[i*2].split(']')[1])) / 10
                times[i].append(ts)
    all_times[folder] = times

# print(all_times)

for folder, color in zip(folders, colors):
    for j in range(len(all_times[folder][0])):
        print(plot_str.replace("COLOR", color + "!20!white"), end="")
        for i in range(6):
            print((i+1, all_times[folder][i][j]), end="")
        print("};")
    print("\n")

for folder, color in zip(folders, colors):
    print(plot_avg_str.replace("COLOR", color), end="")
    for i in range(6):
        avg = sum(all_times[folder][i]) / len(all_times[folder][i])
        print((i+1, avg), end="")
    print("};")