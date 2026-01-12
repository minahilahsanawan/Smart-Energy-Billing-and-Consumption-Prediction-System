import csv
import os
import random
from datetime import datetime
import matplotlib.pyplot as plt                                            
import seaborn as sns
sns.set_theme(style="whitegrid")                
users = {}
usage_logs = []
tariff = {"normal": 15.0, "peak": 25.0}        
overload_limit = 50.0    
current_user = None
current_month = datetime.now().strftime("%Y-%m")
def save_users():
    try:
        with open("users_data.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["user_id", "name", "type", "password"])
            for uid, info in users.items():
                w.writerow([uid, info["name"], info["type"], info["password"]])
    except Exception as e:
        print(f"Error saving users: {e}")
def load_users():                                        
    global users
    if not os.path.exists("users_data.csv"):
        return
    try:
        with open("users_data.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                users[row["user_id"]] = {"name": row["name"], "type": row["type"], "password": row["password"], "appliances": set(),}
    except Exception as e:
        print(f" Sadly, Error loading users: {e} :(( ))")
def save_appliances():
    try:
        with open("appliances_data.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["user_id", "appliance_name", "power_watts"])
            for uid, info in users.items():
                for app in info["appliances"]:
                    w.writerow([uid, app[0], app[1]])
    except Exception as e:
        print(f"Sadly, Error saving appliances: {e} :(( ))")
def load_appliances():
    if not os.path.exists("appliances_data.csv"):
        return
    try:
        with open("appliances_data.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["user_id"] in users:
                    users[row["user_id"]]["appliances"].add((row["appliance_name"], int(row["power_watts"])))
    except Exception as e:
        print(f"Sadly, Error loading appliances: {e} :(( ))")
def save_logs():
    try:
        with open("usage_logs.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["user_id", "month", "day", "appliance", "hours", "kwh", "is_peak"])
            for log in usage_logs:
                w.writerow(log)
    except Exception as e:
        print(f"Sadly, Error saving logs: {e} :(( ))")
def load_logs():
    global usage_logs
    if not os.path.exists("usage_logs.csv"):
        return
    try:
        with open("usage_logs.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    month = row.get("month", current_month)
                    usage_logs.append([row["user_id"], month, int(row["day"]), row["appliance"], float(row["hours"]), float(row["kwh"]), row["is_peak"] == "True",])
                except Exception:
                    continue
    except Exception as e:
        print(f"Sadly, Error loading logs: {e} :(( ))")
def save_bill(uid, bill):
    exists = os.path.exists("monthly_bills.csv")
    try:
        with open("monthly_bills.csv", "a", newline="") as f:
            w = csv.writer(f)
            if not exists:
                w.writerow(["user_id", "month", "date", "total_kwh", "normal_kwh", "peak_kwh", "total_bill"])
            w.writerow([uid, bill.get("month", current_month), datetime.now().strftime("%Y-%m-%d"), bill["total_kwh"], bill["normal_kwh"], bill["peak_kwh"], bill["total_bill"],])
    except Exception as e:
        print(f"Sadly, Error saving bill: {e} :(( ))")
def export_report(uid, month=None):
    if month is None:
        month = current_month
    user_logs = [l for l in usage_logs if l[0] == uid and l[1] == month]
    if not user_logs:
        print(f"No data for {month} :(( ")
        return
    try:
        with open(f"usage_report_{uid}_{month}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Month", "Day", "Appliance", "Hours", "kWh", "Type"])
            for log in user_logs:
                w.writerow([log[1], log[2], log[3], log[4], round(log[5], 2), "Peak" if log[6] else "Normal"])
        print(f"Yayyy, Report saved to usage_report_{uid}_{month}.csv")
    except Exception as e:
        print(f"Error: {e} :(( ))")
def export_bill(uid, bill, month=None):
    if month is None:
        month = current_month
    try:
        with open(f"bill_{uid}_{month}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["User ID", "Name", "Month", "Normal kWh", "Peak kWh", "Total kWh","Normal Cost", "Peak Cost", "Total Bill"])
            w.writerow([uid, users[uid]["name"], month, bill["normal_kwh"], bill["peak_kwh"], bill["total_kwh"], bill["normal_cost"], bill["peak_cost"], bill["total_bill"]])
        print(f"Yayy, Bill exported to bill_{uid}_{month}.csv")
    except Exception as e:
        print(f"Sadly, Error: {e}")
def add_user(uid, name, utype, password):
    if uid in users:
        print(f"Error: User '{uid}' already exists!!")
        return False
    if utype not in ["admin", "customer"]:
        print("Error: Only enter 'admin' or 'customer' !!")
        return False
    users[uid] = {"name": name, "type": utype, "password": password, "appliances": set()}
    print(f"User '{name}' added!!")
    save_users()
    return True
def remove_user(uid):
    if uid not in users:
        print("User not found!!")
        return False
    if uid == "admin":
        print("Cannot remove admin :)")
        return False
    global usage_logs
    usage_logs[:] = [l for l in usage_logs if l[0] != uid]
    del users[uid]
    print(f"User '{uid}' removed!!")
    save_users()
    save_appliances()
    save_logs()
    return True
def login(uid, pwd):
    global current_user
    if uid not in users:
        print("User not found!!")
        return None
    if users[uid]["password"] != pwd:
        print("Wrong password!!")
        return None
    current_user = uid
    print(f"Welcome, {users[uid]['name']}!!")
    return users[uid]
def add_appliance(uid, name, watts):
    if uid not in users:
        print("User not found!!")
        return False
    try:
        watts = int(watts)
        if watts <= 0:
            print("Power must be positive!!")
            return False
    except:
        print("Invalid power rating!!")
        return False
    for app in users[uid]["appliances"]:
        if app[0].lower() == name.lower():
            print(f"'{name}' already exists!!")
            return False
    users[uid]["appliances"].add((name, watts))
    print(f"Added {name} ({watts}W)")
    save_appliances()
    return True
def remove_appliance(uid, name):
    if uid not in users:
        print("User not found!!")
        return False
    for app in users[uid]["appliances"]:
        if app[0].lower() == name.lower():
            users[uid]["appliances"].remove(app)
            print(f"Removed {name}")
            save_appliances()
            return True
    print(f"'{name}' not found!!")
    return False
def list_appliances(uid):
    if uid not in users:
        print("Ouch, User not found!!")
        return
    apps = users[uid]["appliances"]
    if not apps:
        print("Sadly, No appliances added yet.")
        return
    print(f"\n{'No.':<4} {'Appliance':<20} {'Power (W)':<10}")
    for i, app in enumerate(sorted(apps, key=lambda x: x[0].lower()), 1):
        print(f"{i:<4} {app[0]:<20} {app[1]:<10}")
def get_valid_hours(prompt):
    while True:
        try:
            val = input(prompt).strip()
            if val == "":
                return 0
            hours = float(val)
            if hours < 0 or hours > 24:
                print("Hours must be between 0 and 24!!")
                continue
            return hours
        except ValueError:
            print("Sadly, Invalid input!! Enter a number.")
def get_yes_no(prompt):
    while True:
        ans = input(prompt).strip().lower()
        if ans in ("y", "n"):
            return ans == "y"
        print("Enter y or n only pleej!!")
def simulate_day(uid, day, auto=True):
    if uid not in users or not users[uid]["appliances"]:
        return []
    day_logs = []
    day_total = 0
    for name, watts in users[uid]["appliances"]:
        if auto:
            hours = round(random.uniform(0, 8), 2)
            is_peak = random.choice([True, False])
        else:
            hours = get_valid_hours(f"{name} - hours used(0-24): ")
            is_peak = get_yes_no("Peak hours?(y/n): ")
        kwh = (watts * hours) / 1000
        day_total += kwh
        log = [uid, current_month, day, name, hours, kwh, is_peak]
        day_logs.append(log)
        usage_logs.append(log)
    if day_total > overload_limit:
        print(f"Alert: Day {day} usage ({day_total:.2f} kWh) exceeds {overload_limit} kWh!!")
    return day_logs
def clear_month_data(uid, month=None):
    global usage_logs
    if month is None:
        month = current_month
    old_count = len([l for l in usage_logs if l[0] == uid and l[1] == month])
    usage_logs[:] = [l for l in usage_logs if not (l[0] == uid and l[1] == month)]
    if old_count > 0:
        print(f"Cleared {old_count} old logs for {month} :) ")
    save_logs()
def simulate_month(uid, days=30, auto=True):
    if uid not in users:
        print("User not found!!")
        return
    if not users[uid]["appliances"]:
        print("Bro Add appliances first!!")
        return
    existing = len([l for l in usage_logs if l[0] == uid and l[1] == current_month])
    if existing > 0:
        if input(f"Found {existing} existing logs for {current_month}. Clear? (y/n): ").lower() == "y":
            clear_month_data(uid)
    print(f"\nSimulating {days} days for {current_month}... ")
    totals = []
    for day in range(1, days + 1):
        logs = simulate_day(uid, day, auto)
        total = sum(l[5] for l in logs)
        totals.append(total)
        if auto:
            print(f"Day {day:2}: {total:.2f} kWh")
    monthly = sum(totals)
    print(f"Monthly Total: {monthly:.2f} kWh")
    print(f"Daily Average: {monthly/days:.2f} kWh")
    save_logs()
    return totals
def get_daily_totals(uid, month=None):
    if month is None:
        month = current_month
    data = {}
    for log in usage_logs:
        if log[0] == uid and log[1] == month:
            day = log[2]
            data[day] = data.get(day, 0) + log[5]
    return data
def get_weekly_totals(uid, month=None):
    if month is None:
        month = current_month
    weekly = {}
    for log in usage_logs:
        if log[0] == uid and log[1] == month:     #log[1] == month, log[0] == uid
            day = int(log[2])
            week = (day - 1) // 7 + 1
            weekly[week] = weekly.get(week, 0) + log[5]
    return weekly
def get_appliance_totals(uid, month=None): 
    if month is None:
        month = current_month
    data = {}
    for log in usage_logs:
        if log[0] == uid and log[1] == month:
            app = log[3]                             #log[3] appliance name
            data[app] = data.get(app, 0) + log[5]
    return data
def get_peak_offpeak(uid, month=None):
    if month is None:
        month = current_month
    peak, offpeak = 0, 0
    for log in usage_logs:
        if log[0] == uid and log[1] == month:
            if log[6]:
                peak += log[5]
            else:
                offpeak += log[5]
    return peak, offpeak
def get_available_months(uid):
    months = set()
    for log in usage_logs:
        if log[0] == uid:
            months.add(log[1])
    return sorted(months)
def set_month(new_month):
    global current_month
    if new_month:
        current_month = new_month
    print(f"Month set to {current_month}")
def calculate_bill(uid, month=None):
    if month is None:                     
        month = current_month
    peak_kwh, normal_kwh = get_peak_offpeak(uid, month)
    total_kwh = peak_kwh + normal_kwh
    if total_kwh == 0:
        print(f"No usage data for {month}!! Bro Run simulation first.")
        return None
    peak_cost = peak_kwh * tariff["peak"]
    normal_cost = normal_kwh * tariff["normal"]
    total = peak_cost + normal_cost
    return {"month": month, "total_kwh": round(total_kwh, 2), "normal_kwh": round(normal_kwh, 2), "peak_kwh": round(peak_kwh, 2), "normal_cost": round(normal_cost, 2), "peak_cost": round(peak_cost, 2), "total_bill": round(total, 2)}
def show_bill(uid, month=None):
    if month is None:
        month = current_month
    bill = calculate_bill(uid, month)
    if not bill:
        return
    print(f"Monthly Bill: {users[uid]['name']}")
    print(f"Billing Month: {month}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Normal Usage: {bill['normal_kwh']} kWh")
    print(f"Peak Usage: {bill['peak_kwh']} kWh")
    print(f"Total Usage: {bill['total_kwh']} kWh")
    print(f"Normal Rate: Rs {tariff['normal']}/kWh")
    print(f"Peak Rate: Rs {tariff['peak']}/kWh")
    print(f"Normal Cost: Rs {bill['normal_cost']:.2f}")
    print(f"Peak Cost: Rs {bill['peak_cost']:.2f}")
    print(f"Total BILL: Rs {bill['total_bill']:.2f}")
    save_bill(uid, bill)
    return bill
def update_tariff(normal, peak):
    try:
        n, p = float(normal), float(peak)
        if n <= 0 or p <= 0:
            print("Rates must be positive!!")
            return False
        tariff["normal"], tariff["peak"] = n, p
        print(f"Tariff updated!! Normal: Rs {n}/kWh, Peak: Rs {p}/kWh")
        return True
    except:
        print("Sadly, Invalid rates!!")
        return False
def consolidated_report(month=None):
    if month is None:
        month = current_month
    print(f"Consolidated Report: {month}")
    total_kwh, total_rev = 0, 0
    print(f"{'User':<12} {'Name':<15} {'kWh':<10} {'Bill (Rs)':<10}")
    for uid in users:
        if users[uid]["type"] == "customer":
            bill = calculate_bill(uid, month)
            if bill:
                total_kwh += bill["total_kwh"]
                total_rev += bill["total_bill"]
                print(f"{uid:<12} {users[uid]['name']:<15} {bill['total_kwh']:<10.2f} {bill['total_bill']:<10.2f}")
    print(f"{'Total':<12} {'':<15} {total_kwh:<10.2f} {total_rev:<10.2f}")
    print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
def plot_daily(uid, month=None):
    if month is None:
        month = current_month
    data = get_daily_totals(uid, month)
    if not data:
        print(f"No data for {month}!!")
        return
    plt.figure(figsize=(12, 5))
    plt.bar(list(data.keys()),list(data.values()),color="pink", edgecolor="purple")
    plt.axhline(y=overload_limit, color="red", linestyle="--", label=f"Limit ({overload_limit} kWh)")
    plt.xlabel("Day")
    plt.ylabel("kWh")
    plt.title(f"Daily Consumption: {users[uid]['name']} ({month})")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"daily_{uid}.png")
    plt.show()
    print(f"Yay, Saved as daily_{uid}.png")
def plot_weekly(uid, month=None):
    if month is None:
        month = current_month
    data = get_weekly_totals(uid, month)
    if not data:
        print(f"No data for {month}!!")
        return
    weeks = sorted(data.keys())
    vals = [data[w] for w in weeks]
    plt.figure(figsize=(10, 5))
    plt.plot(weeks, vals, marker="o", linewidth=2, color="purple")
    plt.xlabel("Week")
    plt.ylabel("kWh")
    plt.title(f"Weekly Consumption: {users[uid]['name']} ({month})")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"weekly_{uid}.png")
    plt.show()
    print(f"Yay, Saved as weekly_{uid}.png")
def plot_monthly_trend(uid, month=None):
    if month is None:
        month = current_month
    data = get_daily_totals(uid, month)
    if not data:
        print(f"No data for {month}!")
        return
    days= sorted(data.keys())
    vals= [data[d] for d in days]
    cumulative= [sum(vals[: i + 1]) for i in range(len(vals))]
    plt.figure(figsize=(12, 5))
    plt.plot(days, vals, "b-o", label="Daily", linewidth=2, color="hotpink")
    plt.plot(days, cumulative, "g--", label="Cumulative", linewidth=2, color="plum")
    plt.xlabel("Day")
    plt.ylabel("kWh")
    plt.title(f"Monthly Trend: {users[uid]['name']} ({month})")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"trend_{uid}.png")
    plt.show()
    print(f"Yay, Saved as trend_{uid}.png")
def plot_peak_offpeak(uid, month=None):
    if month is None:
        month = current_month
    daily_peak, daily_offpeak = {}, {}
    for log in usage_logs:
        if log[0] == uid and log[1] == month:
            day = log[2]
            if log[6]:
                daily_peak[day] = daily_peak.get(day, 0) + log[5]
            else:
                daily_offpeak[day] = daily_offpeak.get(day, 0) + log[5]
    if not daily_peak and not daily_offpeak:
        print(f"Sadly, No data for {month}!!")
        return
    days = sorted(set(list(daily_peak.keys()) + list(daily_offpeak.keys())))
    peak_vals = [daily_peak.get(d, 0) for d in days]
    offpeak_vals = [daily_offpeak.get(d, 0) for d in days]
    plt.figure(figsize=(12, 5))
    plt.bar(days, offpeak_vals, label="Off-Peak", color="pink")
    plt.bar(days, peak_vals, bottom=offpeak_vals, label="Peak", color="purple")
    plt.xlabel("Day")
    plt.ylabel("kWh")
    plt.title(f"Peak vs Off-Peak: {users[uid]['name']} ({month})")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"peak_{uid}.png")
    plt.show()
    print(f"Yay, Saved as peak_{uid}.png")
def plot_appliances(uid, month=None):
    if month is None:
        month = current_month
    data = get_appliance_totals(uid, month)
    if not data:
        print(f"No data for {month}!")
        return
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    apps, vals = [x[0] for x in sorted_data], [x[1] for x in sorted_data]
    plt.figure(figsize=(10, 6))
    plt.barh(apps, vals, color="lavender")
    plt.xlabel("kWh")
    plt.ylabel("Appliance")
    plt.title(f"Top Appliances: {users[uid]['name']} ({month})")
    for i, v in enumerate(vals):
        plt.text(v + 0.5, i, f"{v:.1f}", va="center")
    plt.tight_layout()
    plt.savefig(f"appliances_{uid}.png")
    plt.show()
    print(f"Yay, Saved as appliances_{uid}.png")
def plot_day_appliances(uid, day, month=None):
    if month is None:
        month = current_month
    data = {}
    for log in usage_logs:
        if log[0] == uid and log[1] == month and log[2] == day:
            app = log[3]
            data[app] = data.get(app, 0) + log[5]
    if not data:
        print(f"Sadly, No data for Day {day}!")
        return
    apps, vals = list(data.keys()), list(data.values())
    plt.figure(figsize=(8, 6))
    colors = ["hotpink", "plum", "skyblue", "thistle", "deeppink", "yellow", "purple", "lavender"]
    plt.pie(vals, labels=apps, autopct="%1.1f%%", colors=colors, startangle=90)
    plt.title(f"Day {day} Consumption by Appliance: {users[uid]['name']} ({month})")
    plt.tight_layout()
    plt.savefig(f"day{day}_{uid}.png")
    plt.show()
    print(f"Yay, Saved as day{day}_{uid}.png")
def linear_regression(x, y):
    n = len(x)
    if n == 0:
        return 0, 0
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    num = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    den = sum((x[i] - x_mean) ** 2 for i in range(n))
    slope = num / den if den != 0 else 0
    intercept = y_mean - slope * x_mean
    return slope, intercept
def predict_next_month(uid, month=None):
    if month is None:
        month = current_month
    data = get_daily_totals(uid, month)
    if len(data) < 5:
        print("Need at least 5 days of data!!")
        return None
    days = sorted(data.keys())
    vals = [data[d] for d in days]
    x = list(range(1, len(days) + 1))
    y = vals
    slope, intercept = linear_regression(x, y)
    next_days = list(range(len(days) + 1, len(days) + 31))
    predicted = [max(0, slope * d + intercept) for d in next_days]
    pred_total = sum(predicted)
    curr_total = sum(vals)
    peak_kwh, normal_kwh = get_peak_offpeak(uid, month)
    total_kwh = peak_kwh + normal_kwh
    peak_ratio = peak_kwh / total_kwh if total_kwh > 0 else 0.5
    pred_bill = (pred_total*peak_ratio*tariff["peak"])+(pred_total*(1-peak_ratio)*tariff["normal"])
    print(f"Next Month Prediction (based on {month})")
    print(f"Based on {len(days)} days of data: ")
    print(f"Current Month: {curr_total:.2f} kWh")
    print(f"Predicted Next: {pred_total:.2f} kWh")
    print(f"Predicted Daily: {pred_total/30:.2f} kWh")
    print(f"Peak Ratio Used: {peak_ratio*100:.1f}%")
    print(f"Predicted Bill: Rs {pred_bill:.2f}")
    if slope > 0:
        print("Trend: ↑ INCREASING!!")
    elif slope < 0:
        print("Trend: ↓ DECREASING!!")
    else:
        print("Trend: → STABLE!!")
    return {"slope": slope, "intercept": intercept, "predicted": predicted, "pred_total": pred_total, "pred_bill": pred_bill, "curr_total": curr_total, "peak_ratio": peak_ratio}
def plot_prediction(uid):
    pred= predict_next_month(uid)
    if not pred:
        return
    data= get_daily_totals(uid)
    curr_days= sorted(data.keys())
    curr_vals= [data[d] for d in curr_days]
    last_day= max(curr_days)
    pred_days= list(range(last_day + 1, last_day + 31))
    all_days= list(range(1, last_day + 31))
    trend= [pred["slope"] * d + pred["intercept"] for d in all_days]
    plt.figure(figsize=(14, 5))
    plt.plot(curr_days, curr_vals, marker="o", linewidth=2.5, label="Actual", color="skyblue")
    plt.plot(pred_days, pred["predicted"], marker="s", linestyle="--", linewidth=2.5, label="Predicted", color="hotpink")
    plt.plot(all_days, trend, linestyle=":", linewidth=2, label="Trend", color="purple", alpha=0.8)
    plt.axvline(x=last_day + 0.5, color="plum", linestyle="--", alpha=0.7)
    plt.xlabel("Day")
    plt.ylabel("Consumption (kWh)")
    plt.title(f"Actual vs Predicted: {users[uid]['name']}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"prediction_{uid}.png")
    plt.show()
    print(f"Yay, saved as prediction_{uid}.png")
def view_logs_paginated(filter_uid=None, filter_month=None, page_size=20):
    filtered = usage_logs
    if filter_uid:
        filtered = [l for l in filtered if l[0] == filter_uid]
    if filter_month:
        filtered = [l for l in filtered if l[1] == filter_month]
    if not filtered:
        print("No logs found!!")
        return
    total = len(filtered)
    page = 0
    while True:
        start = page * page_size
        end = min(start + page_size, total)
        print(f"\nLogs {start+1}-{end} of {total}")
        print(f"{'User':<10} {'Month':<8} {'Day':<4} {'Appliance':<12} {'kWh':<8} {'Type'}")
        for log in filtered[start:end]:
            print(f"{log[0]:<10} {log[1]:<8} {log[2]:<4} {log[3]:<12} {log[5]:<8.2f} {'Peak' if log[6] else 'Normal'}")
        if end >= total:
            print("End of logs!!")
            break
        if input("More?(y/n): ").lower()!="y":
            break
        page += 1
def admin_menu():
    global current_month
    while True:
        print(f"\nAdmin Menu({current_month})\n")
        print("1. Add User\n2. Remove User\n3. View Users\n4. Set Tariff")
        print("5. View Logs\n6. Monthly Report\n7. Sample Appliances\n8. Change Month\n9. Logout")
        p = input("Choice: ").strip()
        if p == "1":
            uid, name = input("User ID: ").strip(), input("Name: ").strip()
            utype, pwd = input("Type (admin/customer): ").lower(), input("Password: ").strip()
            add_user(uid, name, utype, pwd) if uid and name and pwd else print("All fields required!!")
        elif p == "2":
            print("Users:", list(users.keys()))
            uid = input("User ID to remove: ").strip()
            remove_user(uid) if input(f"Remove '{uid}'? (y/n): ").lower() == "y" else None
        elif p == "3":
            print(f"\n{'ID':<12} {'Name':<15} {'Type':<10} {'Apps'}")
            for uid, info in users.items():
                print(f"{uid:<12} {info['name']:<15} {info['type']:<10} {len(info['appliances'])}")
        elif p== "4":
            print(f"Current: Normal=Rs {tariff['normal']}, Peak=Rs {tariff['peak']}")
            update_tariff(input("New normal: "), input("New peak: "))
        elif p == "5":
            print("Filter options: 1. All, 2. By User, 3. By Month, 4. By User+Month")
            fch = input("Filter: ").strip()
            fuid = input("User ID (or Enter for all): ").strip() if fch in ["2", "4"] else None
            fmon = input("Month (YYYY-MM or Enter for all): ").strip() if fch in ["3", "4"] else None
            view_logs_paginated(fuid or None, fmon or None)
        elif p== "6":
            m = input(f"Month (Enter for {current_month}): ").strip() or current_month
            consolidated_report(m)
        elif p== "7":
            uid = input("User ID: ").strip()
            if uid in users:
                for n, w in [("AC", 1500), ("Fridge", 150), ("TV", 100), ("Fan", 75), ("Washer", 500)]:
                    add_appliance(uid, n, w)
        elif p== "8":
            current_month = input("Enter month (YYYY-MM): ").strip() or current_month
            print(f"Month set to {current_month}")
        elif p== "9":
            print("Logged out, Remember: switch off lights, not common sense!")
            break
        input("\nPress enter pls if you don't mind!!")
def customer_menu():
    while True:
        print(f"\nMENU - {users[current_user]['name']} ({current_month})\n")
        print("1. View Appliances      2. Add Appliance     3. Remove Appliance")
        print("4. Simulate (30 days)   5. View Bill         6. Export Usage CSV")
        print("7. Export Bill CSV      8. Daily Chart       9. Weekly Chart")
        print("10. Peak/Off-Peak Chart 11. Appliances Chart 12. Day Breakdown")
        print("13. Predict Next        14. Prediction Chart 15. Trend Chart")
        print("16. View Months         17. Change Month     18. Logout")
        q= input("Choice: ").strip()
        if q== "1":
            list_appliances(current_user)
        elif q== "2":
            n, w = input("Appliance name: ").strip(), input("Power (Watts): ").strip()
            add_appliance(current_user, n, w) if n and w else None
        elif q== "3":
            list_appliances(current_user)
            n = input("Name to remove: ").strip()
            remove_appliance(current_user, n) if n else None
        elif q== "4":
            if not users[current_user]["appliances"]:
                print("Bro add appliances first!!")
            else:
                simulate_month(current_user, 30, input("Auto? (y/n): ").lower() != "n")
        elif q== "5":
            show_bill(current_user)
        elif q== "6":
            export_report(current_user)
        elif q== "7":
            bill = calculate_bill(current_user)
            if bill:
                export_bill(current_user, bill)
        elif q== "8":
            plot_daily(current_user)
        elif q== "9":
            plot_weekly(current_user)
        elif q== "10":
            plot_peak_offpeak(current_user)
        elif q== "11":
            plot_appliances(current_user)
        elif q== "12":
            try:
                day = int(input("Enter day number(1-30): "))
                plot_day_appliances(current_user, day)
            except ValueError:
                print("Invalid day!!")
        elif q== "13":
            predict_next_month(current_user)
        elif q== "14":
            plot_prediction(current_user)
        elif q== "15":
            plot_monthly_trend(current_user)
        elif q== "16":
            months = get_available_months(current_user)
            print(f"Available months: {months if months else 'None'}")
        elif q== "17":
            set_month(input("Enter month(YYYY-MM): ").strip())
        elif q== "18":
            print("Logged out, Thanks for visiting the kWh kingdom!!")
            break
        input("\nPress enter pls if you don't mind!!")
def main_menu():
    while True:
        print("Smart Energy Billing & Consumption Prediction System")
        print("1. Login\n2. Register\n3. Exit")
        k= input("Choice: ").strip()
        if k== "1":
            user = login(input("User ID: ").strip(), input("Password: ").strip())
            if user:
                admin_menu() if user["type"] == "admin" else customer_menu()
        elif k== "2":
            uid, name, pwd = input("User ID: ").strip(), input("Name: ").strip(), input("Password: ").strip()
            add_user(uid, name, "customer", pwd) if uid and name and pwd else print("All fields required!")
        elif k== "3":
            print("Saving, please wait, I'm being responsible.")
            save_users()
            save_appliances()
            save_logs()
            print("Goodbye, System shutting down unlike your appliances :)")
            break
        input("\nPress enter pls if you don't mind!!")
if __name__ == "__main__":
    print("Starting up, May your bill be low and your savings high!!")
    load_users()
    load_appliances()
    load_logs()
    if "admin" not in users:
        users["admin"] = {"name": "Admin", "type": "admin", "password": "ouchhh", "appliances": set()}
        print("Default admin created (admin/ouchhh)!!")
        save_users()
    else:
        users["admin"]["password"] = "ouchhh"
        save_users()
    print("Yayy, system is ready! Let's track those sneaky kWh.\n")
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nSaving and exiting(acha chalta ho duaon mei yad rakhna :)")
        save_users()
        save_appliances()
        save_logs()