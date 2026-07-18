# Smart Energy Billing and Consumption Prediction System

This is a Smart Energy Billing and Consumption Prediction System, a complete application that tracks household electricity usage, calculates monthly bills with different rates for peak/off-peak hours, predicts next month's consumption using machine learning (linear regression) & generates visual charts for analysis. This system simulates how electricity companies manage billing. 

---

## Contents
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run](#run)
- [Default Admin Credentials](#default-admin-credentials)
- [Usage Guide](#usage-guide)
- [Billing Model](#billing-model)
- [Forecasting Model](#forecasting-model)
- [Data Persistence (CSV Files)](#data-persistence-csv-files)
- [Exports and Outputs](#exports-and-outputs)
- [Configuration](#configuration)
- [Limitations](#limitations)
- [Author](#author)

---

## Overview
This project is a Python command-line application that simulates appliance-level household electricity consumption, calculates monthly bills using peak and off-peak tariffs, and provides reporting, visualization, and forecasting capabilities. Users define appliances with power ratings (W) and record daily or monthly usage based on operating hours. The system stores detailed usage logs, aggregates consumption by peak/off-peak categories, and computes billing totals using configurable tariff rates. It also exports usage and billing reports to CSV, generates analysis plots, and estimates next-month consumption using a linear regression trend model. All data is persisted through CSV files to ensure continuity across program runs.

---

## Features
- Role-based access control (Admin and Customer)
- Appliance management per customer (add, remove, list)
- Daily/monthly usage simulation:
  - Auto mode (randomized hours and peak/off-peak tagging)
  - Manual mode (user-entered hours and peak/off-peak selection)
- Peak/off-peak billing with configurable tariff rates
- Overload alert when daily usage exceeds a defined kWh threshold
- CSV persistence for users, appliances, usage logs, and bill history
- CSV exports for usage reports and bill summaries
- Visualization outputs (PNG):
  - Daily, weekly, appliance-wise, peak/off-peak, monthly trend, prediction
- Next-month consumption and bill estimation using linear regression trend + historical peak ratio

---

## Requirements
- Python 3.x
- Python packages:
  - `matplotlib`
  - `seaborn` (theme styling)

---

## Installation
```bash
pip install matplotlib seaborn
```

---

## Run

Clone the repository, move into the project directory, install dependencies, and execute the entry script:

```bash
git clone <REPO_URL>
cd <REPO_FOLDER>
python -m pip install matplotlib seaborn
python main.py
```
---

## Default Admin Credentials
```text
User ID: admin
Password: ouchhh
```

> Security note: Passwords are stored in plaintext in CSV files. This implementation is intended for local demonstration only.

---

## Usage Guide

### Main Menu
```text
Smart Energy Billing & Consumption Prediction System
1. Login
2. Register
3. Exit
```

### Admin Menu (YYYY-MM)
```text
Admin Menu(YYYY-MM)

1. Add User
2. Remove User
3. View Users
4. Set Tariff
5. View Logs
6. Monthly Report
7. Sample Appliances
8. Change Month
9. Logout
```

Admin capabilities:
- Add/remove customer accounts (the `admin` account cannot be removed)
- View all users and appliance counts
- Update tariff rates (normal and peak)
- View usage logs with filtering (by user, month, or both) and pagination
- Generate consolidated monthly report across all customers
- Change the active month context used for simulations and billing

### Customer Menu (YYYY-MM)
```text
MENU - <CustomerName> (YYYY-MM)

1.  View Appliances      2.  Add Appliance     3.  Remove Appliance
4.  Simulate (30 days)   5.  View Bill         6.  Export Usage CSV
7.  Export Bill CSV      8.  Daily Chart       9.  Weekly Chart
10. Peak/Off-Peak Chart  11. Appliances Chart  12. Day Breakdown
13. Predict Next         14. Prediction Chart  15. Trend Chart
16. View Months          17. Change Month      18. Logout
```

Customer workflow (typical):
1. Add appliances with power ratings (W).
2. Simulate monthly usage (auto or manual).
3. View the monthly bill.
4. Export CSV reports and generate plots as needed.
5. Run next-month prediction and generate prediction plot.

---

## Billing Model
Energy consumption per appliance entry:
- `kWh = (power_watts × hours) / 1000`

Monthly totals (for a given user and month):
- Peak kWh: sum of entries where `is_peak = True`
- Normal (off-peak) kWh: sum of entries where `is_peak = False`

Cost computation:
- `peak_cost = peak_kwh × tariff["peak"]`
- `normal_cost = normal_kwh × tariff["normal"]`
- `total_bill = peak_cost + normal_cost`

Bills can be displayed in the CLI, exported as a per-user CSV file, and appended to bill history.

---

## Forecasting Model
The forecasting module predicts next-month usage using linear regression over daily totals:
- Input: daily total kWh values for the selected month
- Fit: slope and intercept from least-squares regression
- Output: predicted next 30 daily values (negative values clipped to 0)

Predicted bill estimation:
- Uses historical peak ratio from the selected month:
  - `peak_ratio = peak_kwh / total_kwh` (fallback to 0.5 if undefined)
- Applies peak/off-peak tariffs to the predicted total using this ratio.

---

## Data Persistence (CSV Files)
The application reads/writes CSV files in the working directory.

### `users_data.csv`
```text
user_id, name, type, password
```

### `appliances_data.csv`
```text
user_id, appliance_name, power_watts
```

### `usage_logs.csv`
```text
user_id, month, day, appliance, hours, kwh, is_peak
```

### `monthly_bills.csv`
```text
user_id, month, date, total_kwh, normal_kwh, peak_kwh, total_bill
```

---

## Exports and Outputs

### CSV Exports
Usage report:
```text
usage_report_<user_id>_<YYYY-MM>.csv
```

Bill export:
```text
bill_<user_id>_<YYYY-MM>.csv
```

Bill history(auto-append):
```text
monthly_bills.csv
```

### Plot Outputs (PNG)
```text
daily_<user_id>.png
weekly_<user_id>.png
peak_<user_id>.png
appliances_<user_id>.png
day<day>_<user_id>.png
trend_<user_id>.png
prediction_<user_id>.png
```

---

## Configuration
Key parameters are defined in the source code:
- `tariff["normal"]` (default: 15.0)
- `tariff["peak"]` (default: 25.0)
- `overload_limit` (default: 50.0 kWh/day)
- `current_month` format: `YYYY-MM`

The active month can be changed from the Admin or Customer menu.

---

## Limitations
- Passwords are stored in plaintext in CSV files (not secure for production).
- Forecasting is trend-only and does not model seasonality or external drivers.
- Auto-simulation is randomized and may produce noisy data that affects prediction stability.

---
## Author
Minahil Ahsan
