import os

engines = ['dialogflow', 'rasa']
markers = ['*', 'triangle*']

folders = ['no-monitor', 'dummy-monitor', 'real-monitor']
colors = ['red', 'blue', 'teal']

# times_dict = {}
tikz = open('times_plot.tex', 'w')
tikz.write("\\documentclass[tikz]{standalone}\n")
tikz.write("\\usepackage{pgfplots}")
tikz.write("\n\\begin{document}\n")
tikz.write("\n\n\\begin{tikzpicture}\n")
tikz.write("\\begin{axis}[axis lines=middle, grid=both, ymin=0, ymax=31, legend style={font=\\footnotesize}, xlabel=msgs, ylabel=ms,xlabel style={at={(ticklabel cs:0.5)}, anchor=north}, ylabel style={at={(ticklabel cs:0.5)}, anchor=east, rotate=90},]\n")

for engine, marker in zip(engines, markers):
    for color, folder in zip(colors, folders):
        times_dict = {}
        print(f'Engine: {engine}\nColor: {color}\nFolder: {folder}')
        for f in os.listdir(os.path.join(engine, folder)):
            f_read = open(os.path.join(engine, os.path.join(folder, f)))
            for i, line in enumerate(f_read.readlines()):
                if i not in times_dict:
                    times_dict[i] = []
                times_dict[i].append(float(line))

        # tikz.write("\draw [" + color + "] plot [smooth, tension=1, mark=*] coordinates {")
        var_str = '\\addplot[|-|, thin]'
        tikz.write("\\addplot [" + color + ", smooth, tension=1, mark=" + marker + "] coordinates {")
        # times_avg = []
        vars_list = []
        for i in times_dict:
            avg = round(sum(times_dict[i]) / len(times_dict[i]) / 10, 3)
            var = sum((v / 10 - avg) ** 2 for v in times_dict[i]) / len(times_dict[i])
            print(var)
            vars_list.append('\\addplot[|-|, thin] coordinates {(' + str(i+1) + ', ' + str(avg - var / 2) + ') (' + str(i+1) + ', ' + str(avg + var / 2) + ')};\n')
            # var = sum((xi - m) ** 2 for xi in results) / len(results)
            tikz.write(str((i+1, avg)))
        tikz.write("};\n")

        # for var in vars_list:
        #     tikz.write(var)
tikz.write('\\legend{Dialogflow No Monitor, Dialogflow Dummy Monitor, Dialogflow Real Monitor, Rasa No Monitor, Rasa Dummy Monitor, Rasa Real Monitor}\n')
tikz.write("\\end{axis}\n")
tikz.write("\\end{tikzpicture}\n")
tikz.write("\\end{document}")
