import os 

# log_times = {}
# for i, f in enumerate(os.listdir('./no-monitor')):
#     # print("===", f.upper(), "===")
#     log = open(os.path.join('./no-monitor', f))#.read()
#     c = 0
#     # print(log)
#     print("\draw[red!20!white] plot [smooth, tension=1] coordinates { ", end="")
#     for j, line in enumerate(log):#.split('\n'):
#         # print(line)
#         # print("\n")
#         # if "Starting a new session for conversation ID" in line:
#         # if "Acquired lock for conversation " in line:
#         if "Logged UserUtterance" in line:
#             # print(j, line.split("[")[0].split(":")[-1])
#             start_time = float(line.split("[")[0].split(":")[-1].replace(',', '.'))
#         if "Calling action endpoint to run action 'action_reset_all_slots'" in line:
#             # print(j, line.split("[")[0].split(":")[-1])
#             t = (float(line.split("[")[0].split(":")[-1].replace(',', '.')) - start_time) * 1000
#             # print("[TIME]", t)
#             print("( " + str(c + 1) + ", " + str(round(t, 3)) + ") ", end = "")
#             if c not in log_times:
#                 log_times[c] = []
#             log_times[c].append(float(line.split("[")[0].split(":")[-1].replace(',', '.')) - start_time)
#             c += 1
#     print("};")

# # print(log_times)
# # for msg in log_times:
# #     print(msg, round(sum(log_times[msg]) / len(log_times[msg]), 5) * 1000)
# print(log_times)

# log_times_avg = []
# for msg in log_times:
#     print(msg, round(sum(log_times[msg]) / len(log_times[msg]) * 1000, 5))
#     log_times_avg.append((msg + 1, round(sum(log_times[msg]) / len(log_times[msg]) * 1000, 5)))
# print(log_times_avg)
# print("\draw[red] plot [smooth, tension=1] coordinates {", log_times_avg[0], log_times_avg[1], log_times_avg[2], log_times_avg[3], log_times_avg[4], log_times_avg[5], "};")

# log_times = {}
# for i, f in enumerate(os.listdir('./dummy-monitor')):
#     # print("===", f.upper(), "===")
#     log = open(os.path.join('./dummy-monitor', f))#.read()
#     c = 0
#     # print(log)
#     print("\draw[blue!20!white] plot [smooth, tension=1] coordinates { ", end="")
#     for j, line in enumerate(log):#.split('\n'):
#         # print(line)
#         # print("\n")
#         # if "Starting a new session for conversation ID" in line:
#         # if "Acquired lock for conversation " in line:
#         if "Logged UserUtterance" in line:
#             # print(j, line.split("[")[0].split(":")[-1])
#             start_time = float(line.split("[")[0].split(":")[-1].replace(',', '.'))
#         if "Calling action endpoint to run action 'action_reset_all_slots'" in line:
#             # print(j, line.split("[")[0].split(":")[-1])
#             t = (float(line.split("[")[0].split(":")[-1].replace(',', '.')) - start_time) * 1000
#             # print("[TIME]", t)
#             print("( " + str(c + 1) + ", " + str(round(t, 3)) + ") ", end = "")
#             if c not in log_times:
#                 log_times[c] = []
#             log_times[c].append(float(line.split("[")[0].split(":")[-1].replace(',', '.')) - start_time)
#             c += 1
#     print("};")

# # print(log_times)
# log_times_avg = []
# for msg in log_times:
#     print(msg, round(sum(log_times[msg]) / len(log_times[msg]) * 1000, 5))
#     log_times_avg.append((msg + 1, round(sum(log_times[msg]) / len(log_times[msg]) * 1000, 5)))
# print(log_times_avg)
# print("\draw[blue] plot [smooth, tension=1] coordinates {", log_times_avg[0], log_times_avg[1], log_times_avg[2], log_times_avg[3], log_times_avg[4], log_times_avg[5], "};") 
folders = ['./dummy-monitor/', './no-monitor/', './real-monitor/']
colors = ['blue', 'red', 'teal']
# folder = './dummy-monitor/'
for folder, color in zip(folders, colors):
    avg_times = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    counter = 0
    for f in os.listdir(folder):
        if f.endswith('.log'):
            counter += 1
            send_times = []
            reset_times = []
            ff = open(os.path.join(folder, f))
            for line in ff:
                if 'SEND' in line:
                    send_times.append(float(line.split(']')[1]))
                elif 'RESET' in line:
                    reset_times.append(float(line.split(']')[1]))
            computed_times = [t2 - t1 for t1, t2 in zip(send_times, reset_times)]
            avg_times = [t1 + t2 for t1, t2 in zip(avg_times, computed_times)]
            computed_times_couple = [(i+1, round(t2 - t1, 3)) for i, (t1, t2) in enumerate(zip(send_times, reset_times))]
            # print(send_times)
            # print(reset_times)
            # print(computed_times)
            # print(computed_times_couple)
            print("\draw[" + color + "!20!white] plot [smooth, tension=1] coordinates { ", end="")
            for c in computed_times_couple:
                print(c, end=" ")
            print("};")
            # print(reset_times - send_times)

    # print(avg_times)
    print("\draw[" + color + "] plot [smooth, tension=1] coordinates { ", end="")
    for i, t in enumerate(avg_times):
        print((i+1, round(t/counter, 3)), end=" ")
    print("};")
