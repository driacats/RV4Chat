import os

engines = ['rasa']

folders = ['no-monitor', 'dummy-monitor']
colors = ['red', 'blue']

# times_dict = {}
tikz = open('times_plot.tex', 'w')
tikz.write("\\documentclass[tikz]{standalone}\n")
tikz.write("\\usepackage{pgfplots}")
tikz.write("\n\\begin{document}\n")
tikz.write("\n\n\\begin{tikzpicture}\n")

for engine in engines:
    for color, folder in zip(colors, folders):
        times_dict = {}
        for f in os.listdir(os.path.join(engine, folder)):
            f_read = open(os.path.join(engine, os.path.join(folder, f)))
            for i, line in enumerate(f_read.readlines()):
                if i not in times_dict:
                    times_dict[i] = []
                times_dict[i].append(float(line))

        tikz.write("\draw [" + color + "] plot [smooth, tension=1, mark=*] coordinates {")
        times_avg = []
        for i in times_dict:
            avg = round(sum(times_dict[i]) / len(times_dict[i]) / 10, 3)
            tikz.write(str((i+1, avg)))
        tikz.write("};\n")

tikz.write("\\end{tikzpicture}\n")
tikz.write("\\end{document}")