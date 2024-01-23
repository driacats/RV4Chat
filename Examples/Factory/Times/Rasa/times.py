import os 

log_times = {}
for i, f in enumerate(os.listdir('./no-monitor')):
    print("===", f.upper(), "===")
    log = open(os.path.join('./no-monitor', f))#.read()
    c = 0
    # print(log)
    for j, line in enumerate(log):#.split('\n'):
        # print(line)
        # print("\n")
        # if "Starting a new session for conversation ID" in line:
        # if "Acquired lock for conversation " in line:
        if "Logged UserUtterance" in line:
            # print(j, line.split("[")[0].split(":")[-1])
            start_time = float(line.split("[")[0].split(":")[-1].replace(',', '.'))
        if "Calling action endpoint to run action 'action_reset_all_slots'" in line:
            # print(j, line.split("[")[0].split(":")[-1])
            print("[TIME]", float(line.split("[")[0].split(":")[-1].replace(',', '.')) - start_time)
            if c not in log_times:
                log_times[c] = []
            log_times[c].append(float(line.split("[")[0].split(":")[-1].replace(',', '.')) - start_time)
            c += 1

# print(log_times)
for msg in log_times:
    print(msg, round(sum(log_times[msg]) / len(log_times[msg]), 5) * 1000)

log_times = {}
for i, f in enumerate(os.listdir('./dummy-monitor')):
    print("===", f.upper(), "===")
    log = open(os.path.join('./dummy-monitor', f))#.read()
    c = 0
    # print(log)
    for j, line in enumerate(log):#.split('\n'):
        # print(line)
        # print("\n")
        # if "Starting a new session for conversation ID" in line:
        # if "Acquired lock for conversation " in line:
        if "Logged UserUtterance" in line:
            # print(j, line.split("[")[0].split(":")[-1])
            start_time = float(line.split("[")[0].split(":")[-1].replace(',', '.'))
        if "Calling action endpoint to run action 'action_reset_all_slots'" in line:
            # print(j, line.split("[")[0].split(":")[-1])
            print("[TIME]", float(line.split("[")[0].split(":")[-1].replace(',', '.')) - start_time)
            if c not in log_times:
                log_times[c] = []
            log_times[c].append(float(line.split("[")[0].split(":")[-1].replace(',', '.')) - start_time)
            c += 1

# print(log_times)
log_times_avg = []
for msg in log_times:
    print(msg, round(sum(log_times[msg]) / len(log_times[msg]) * 1000, 5))
    log_times_avg.append((msg, round(sum(log_times[msg]) / len(log_times[msg]) * 1000, 5)))
print(log_times_avg)
print("\draw[gray!40] plot [smooth, tension=1] coordinates {", log_times_avg[0], log_times_avg[1], log_times_avg[2], log_times_avg[3], log_times_avg[4], log_times_avg[5], "};") 