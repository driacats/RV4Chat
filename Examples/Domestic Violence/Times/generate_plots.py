import os

engines = ['Dialogflow']

folders = ['no-monitor']
colors = ['red']

times_dict = {}

for engine in engines:
    for color, folder in zip(colors, folders):
        for f in os.listdir(os.path.join(engine, folder)):
            f_read = open(os.path.join(engine, os.path.join(folder, f)))
            for i, line in enumerate(f_read.readlines()):
                if i not in times_dict:
                    times_dict[i] = []
                times_dict[i].append(float(line))

print("\draw [" + color + "] plot [smooth, tension=1, mark=*] coordinates {", end="")
times_avg = []
for i in times_dict:
    avg = round(sum(times_dict[i]) / len(times_dict[i]) / 10, 3)
    print((i+1, avg), end=" ")
print("};")
    