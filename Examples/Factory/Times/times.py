import csv, os

times_nm = {}
for f in os.listdir("no-monitor"):
    reader = csv.DictReader(open(os.path.join("no-monitor", f)))
    for row in reader:
        for item in row:
            if item not in times_nm:
                times_nm[item] = []
            times_nm[item].append(float(row[item]))

print("==== No Monitor Times ====")
for bp in times_nm:
    print(str(bp) + ": " + str(round(sum(times_nm[bp]) / len(times_nm[bp]),2)))

times_dm = {}
for f in os.listdir("dummy-monitor"):
    reader = csv.DictReader(open(os.path.join("dummy-monitor", f)))
    for row in reader:
        for item in row:
            if item not in times_dm:
                times_dm[item] = []
            times_dm[item].append(float(row[item]))

print("==== Dummy Monitor Times ====")
times_dm_avg = {}
for bp in times_dm:
    times_dm_avg[bp] = round(sum(times_dm[bp]) / len(times_dm[bp]),2)

times_dm_list = []
time_passed = 0.0
print("Header:", times_dm_avg["header"])
times_dm_list.append(times_dm_avg["header"])
time_passed = times_dm_avg["header"]

print("Intent:", times_dm_avg["intent"] - time_passed)
times_dm_list.append(times_dm_avg["intent"] - time_passed)
time_passed = times_dm_avg["intent"]

print("WebHook:", times_dm_avg["perform"] - time_passed)
times_dm_list.append(times_dm_avg["perform"] - time_passed)
time_passed = times_dm_avg["perform"]

print("Bot:", times_dm_avg["bot"] - time_passed)
times_dm_list.append(times_dm_avg["bot"] - time_passed)

print("Total:", times_dm_avg["total"])
times_dm_list.append(times_dm_avg["total"])

print(times_dm_list)