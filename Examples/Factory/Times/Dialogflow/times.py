import csv, os

times_nm = {}
for f in os.listdir("no-monitor"):
    reader = csv.DictReader(open(os.path.join("no-monitor", f)))
    for i, row in enumerate(reader):
        # print(row)
        if i not in times_nm:
            times_nm[i] = []
        times_nm[i].append(float(row["ms"]))
        # for item in row:
        #     if item not in times_nm:
        #         times_nm[item] = []
        #     times_nm[item].append(float(row[item]))

print("\n=== NO MONITOR AVERAGES ===")
for i in times_nm:
    print(i, sum(times_nm[i]) / len(times_nm[i]))
# print(times_nm)

print("\n=== NO MONITOR RAW DATA ===")
for i in range(len(times_nm[0])):
    print("\draw[gray!30] plot [smooth, tension=1] coordinates {(1, " + str(times_nm[0][i]) + ") (2, " + \
        str(times_nm[1][i]) + ") (3, " + str(times_nm[2][i]) + ") (4, " + str(times_nm[3][i]) + ") (5, "\
            + str(times_nm[4][i]) + ") (6, " + str(times_nm[5][i]) + ")};")

times_dm = {}
times_dm_steps = {}
for f in os.listdir("dummy-monitor"):
    reader = csv.DictReader(open(os.path.join("dummy-monitor", f)))
    for i, row in enumerate(reader):
        # print(row)
        if i not in times_dm:
            times_dm[i] = []
        times_dm[i].append(float(row["total"]))
        if i not in times_dm_steps:
            times_dm_steps[i] = {}
        for item in row:
            if item not in times_dm_steps[i]:
                times_dm_steps[i][item] = []
            times_dm_steps[i][item].append(float(row[item]))

print("\n=== DUMMY MONITOR AVERAGES ===")
for i in times_dm:
    print(i, sum(times_dm[i]) / len(times_dm[i]))
# print(times_dm)

max_time = max(sum(l)/len(l) for l in times_dm.values())
# max_time = max(max(l) for l in times_dm.values())
print(max_time)

print("\n===DUMMY MONITOR RAW DATA ===")
for i in range(len(times_dm[0])):
    print("\draw[gray!30] plot [smooth, tension=1] coordinates {(1, " + str(times_dm[0][i]) + ") (2, " + \
        str(times_dm[1][i]) + ") (3, " + str(times_dm[2][i]) + ") (4, " + str(times_dm[3][i]) + ") (5, "\
            + str(times_dm[4][i]) + ") (6, " + str(times_dm[5][i]) + ")};")


bar_length = 10
line_points_nm = []
for i in times_nm:
    line_points_nm.append((i + 0.75, round(sum(times_nm[i]) / len(times_nm[i]) / max_time * bar_length, 3)))


line_points = []
print("\n===DUMMY MONITOR STORY TIME ===")
for i in times_dm_steps:
    print("% MESSAGE", i)
    # for item in times_dm_steps[i]:
    #     print(item, str(sum(times_dm_steps[i][item]) / len(times_dm_steps[i][item])))

    header =    sum(times_dm_steps[i]["header"]) / len(times_dm_steps[i]["header"])
    intent =    sum(times_dm_steps[i]["intent"]) / len(times_dm_steps[i]["intent"]) - header
    perform =   sum(times_dm_steps[i]["perform"]) / len(times_dm_steps[i]["perform"]) - (header + intent)
    bot =       sum(times_dm_steps[i]["bot"]) / len(times_dm_steps[i]["bot"]) - (header + intent + perform)
    total =     sum(times_dm_steps[i]["total"]) / len(times_dm_steps[i]["total"]) - (header + intent + perform + bot)

    header =    round(header / max_time * bar_length, 3)
    intent =    round(intent / max_time * bar_length, 3)
    perform =   round(perform / max_time * bar_length, 3)
    bot =       round(bot / max_time * bar_length, 3)
    total =     round(total / max_time * bar_length, 3)

    # print(perform - line_points_nm[i][1])
    # print(header)
    # print(intent)
    # print(perform)
    # print(bot)
    # print(total)

    print("\draw[green, fill=green] (" + str(i + 0.5) + ", 0.05) rectangle ++ (0.5, " + str(header) + ");")
    print("\draw[blue, fill=blue] (" + str(i + 0.5) + ", " + str(header + 0.1) + ") rectangle ++ (0.5, " + str(intent) +");")
    print("\draw[red, fill=red] (" + str(i + 0.5) + ", " + str(header + intent + 0.15) + ") rectangle ++ (0.5, " + str(perform) + ");")
    print("\draw[orange, fill=orange] (" + str(i + 0.5) + ", " + str(header + intent + perform + 0.20) + ") rectangle ++ (0.5, " + str(bot) + ");")
    print("\draw[yellow, fill=yellow] (" + str(i + 0.5) + ", " + str(header + intent + perform + bot + 0.25) + ") rectangle ++ (0.5, " + str(total) + ");")
    line_points.append((i + 0.5, round(header + intent + perform + bot + total + 0.25, 3)))

print(line_points)
print(line_points_nm)

# Print grid
for i in range(1, 25):
    i_norm = round(i / max_time * bar_length, 3)
    print("\draw[gray!20] (-0.1, " + str(i_norm) + ") node[left]{\\footnotesize " + str(i) + "}-- (7, " + str(i_norm) + ");")