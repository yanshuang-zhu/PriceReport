from datetime import datetime
import time

target_time = "08:00"
with open("run_time.txt", "r") as run_time:
    if ":" in run_time:
        target_time = run_time

while True:
    now = datetime.now()
    time_str = str(now.time())[:5]

    if time_str == target_time:
        print("time up")
        import generate_graph_all
        print()
        import send_report_email
        print()
        print("Everything's done!")
        time.sleep(60)
    else:
        print(time_str)
        time.sleep(59)
