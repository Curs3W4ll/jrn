#!/usr/bin/env python3

from itertools import islice, chain
from datetime import date, datetime
from argparse import ArgumentParser
from sys import argv, exit
import os
import sys

settings_filepath = os.getenv("HOME") + "/.jrn.settings"
settings_separator = ";"
default_stock_path = os.getenv("HOME") + "/Documents/my_journey.txt"
stock_separator = "|"
stock_path_key = "stock-path"

class colors:
    TITLE = "\033[32m"
    ADD = "\033[92m"
    REMOVE = "\033[91m"
    TIME = "\033[94m"
    CYAN = "\033[96m"
    WARNING = "\033[93m"
    UNDERLINE = "\033[4m"
    BOLD = "\033[1m"
    END = "\033[0m"

def str2bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in ("yes", "true", "enable", "y", "t", "e", "1"):
        return True
    elif value.lower() in ("no", "false", "disable", "n", "f", "d", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")

def get_args():
    parse = ArgumentParser(description="A simple tool to keep up what you've done in your day")
    parse.add_argument("-cp", "--change-path", type=str, help="Change the path where the program stock your daily journal", metavar="new_path")
    parse.add_argument("-r", "--reset", action="store_true", help="Reset settings to default")
    parse.add_argument("-c", "--clear", action="store_true", help="Clear the journal stock")
    parse.add_argument("-s", "--summary", action="store_true", help="Make a summary of your journey")
    parse.add_argument("-rs", "--readable-summary", action="store_true", help="Make a readable summary of your journey with total times")
    parse.add_argument("-p", "--previous", action="store_true", help="Take the activity you was doing before")
    parse.add_argument("Activity", type=str, nargs="?", help="A litle description of the activity you started")
    return parse

def read_settings_file():
    data = []
    try:
        file = open(settings_filepath, 'r')
        data = file.readlines()
        file.close()
    except IOError:
        return data
    return data

def get_stock_path():
    data = read_settings_file()
    for line in data:
        splitted = line.split(settings_separator)
        splitted[1] = splitted[1].rstrip("\n")
        if splitted[0] == stock_path_key:
            return splitted[1]
    return default_stock_path

def write_stock_path(path):
    if path == None:
        return
    old_path = get_stock_path()
    f = open(settings_filepath, "a")
    f.close()
    with open(settings_filepath, "r+") as f:
        d = f.readlines()
        f.seek(0)
        for i in d:
            if (i.split(settings_separator))[0] != stock_path_key:
                f.write(i)
        f.truncate()
    with open(settings_filepath, "a") as f:
        f.writelines(stock_path_key + settings_separator + path + "\n")
    f = open(old_path, "a")
    f.close()
    with open(old_path, "r") as fold:
        d = fold.readlines()
    with open(path, "w") as fnew:
        for i in d:
            fnew.write(i)
    os.remove(old_path)

def reset_settings_if_needed(boolean):
    if boolean:
        f = open(settings_filepath, "w")
        f.close()

def clear_stock_if_needed(boolean):
    if boolean:
        f = open(get_stock_path(), "w")
        f.close()

def actualize_date():
    cur_date = date.today().strftime("%d %b %Y")
    try:
        f = open(get_stock_path(), "r")
        lines = f.readlines()
        f.close()
        for line in reversed(lines):
            line = line.rstrip("\n")
            splitted = line.split(stock_separator)
            if len(splitted) == 1:
                if splitted[0] != cur_date:
                    with open(get_stock_path(), "a") as f:
                        f.write("-----------\n%s\n" %cur_date)
                return
        with open(get_stock_path(), "a") as f:
            f.write("-----------\n%s\n" %cur_date)
    except IOError:
        with open(get_stock_path(), "a") as file:
            file.write("-----------\n%s\n" %cur_date)

def write_new_activity(activity):
    print(colors.ADD + "Starting new activity..." + colors.END)
    cur_time = datetime.now().strftime("%H:%M")
    with open(get_stock_path(), "a") as f:
        f.write(activity)
        f.write(stock_separator)
        f.write(cur_time)
    print(colors.ADD + "Activity '" + colors.UNDERLINE + activity + colors.END + colors.ADD + "' started at " + colors.TIME + colors.BOLD + cur_time + colors.END)

def close_activity():
    print(colors.REMOVE + "Closing previous activity..." + colors.END)
    cur_time = datetime.now().strftime("%H:%M")
    with open(get_stock_path(), "a") as f:
        f.write(stock_separator)
        f.write(cur_time)
        f.write(stock_separator)
    with open(get_stock_path(), "r") as f:
        last_line = f.readlines()[-1]
    splitted = last_line.split(stock_separator)
    now = datetime.now()
    previous_datetime = datetime(now.year, now.month, now.day, int(splitted[1].split(":")[0]), int(splitted[1].split(":")[1]), 0)
    duration = (now - previous_datetime).total_seconds()
    hours = int(duration / 3600)
    duration %= 3600
    minutes = int(duration / 60)
    duration_string = "{}h{}m".format(hours, minutes)
    if hours == 0:
        duration_string = duration_string.split("h")[1]
    with open(get_stock_path(), "a") as f:
        f.write(duration_string)
        f.write("\n")
    print(colors.REMOVE + "Activity '" + colors.UNDERLINE + splitted[0] + colors.END + colors.REMOVE +"' closed, duration: " + colors.TIME + colors.BOLD + duration_string + colors.END)

def change_if_youtrack(activity):
    if "RDA" in activity:
        activity = activity.replace("RDA", "https://youtracknew.doyoudreamup.com/issue/RDA")
    if "rda" in activity:
        activity = activity.replace("rda", "https://youtracknew.doyoudreamup.com/issue/RDA")
    if "RDS" in activity:
        activity = activity.replace("RDS", "https://youtracknew.doyoudreamup.com/issue/RDS")
    if "rds" in activity:
        activity = activity.replace("rds", "https://youtracknew.doyoudreamup.com/issue/RDS")
    if "INTERNE" in activity:
        activity = activity.replace("INTERNE", "https://youtracknew.doyoudreamup.com/issue/INTERNE")
    if "interne" in activity:
        activity = activity.replace("interne", "https://youtracknew.doyoudreamup.com/issue/INTERNE")
    return activity

def get_activity(activity, boolean):
    if boolean:
        if activity:
            print(colors.WARNING + colors.BOLD + "/!\\Warning/!\\" + colors.END + " Activities are not taken in count when " + colors.BOLD + "-p" + colors.END + ", " + colors.BOLD + "--previous option" + colors.END + " is specified")
        with open(get_stock_path(), "r") as f:
            lines = f.readlines()
        for line in reversed(lines):
            line = line.rstrip("\n")
            splitted = line.split(stock_separator)
            if len(splitted) == 4:
                activity = splitted[0]
                break;
    return change_if_youtrack(activity)

def write_activity(activity, prev_boolean):
    actualize_date()
    new_activity = get_activity(activity, prev_boolean)
    activity = new_activity
    with open(get_stock_path(), "r") as f:
        lines = f.readlines()
    for line in reversed(lines):
        line = line.rstrip("\n")
        splitted = line.split(stock_separator)
        if len(splitted) == 2:
            close_activity()
            break;
    if activity:
        write_new_activity(activity)

def get_activities_list():
    cur_date = date.today().strftime("%d %b %Y")
    try:
        f = open(get_stock_path(), "r")
        lines = f.readlines()
        f.close()
        i = len(lines)
        activities_list = []
        for line in reversed(lines):
            line = line.rstrip("\n")
            splitted = line.split(stock_separator)
            if len(splitted) == 1:
                if splitted[0] != cur_date:
                    return None
                else:
                    for l in islice(lines, i, None):
                        activities_list.append(l)
                    return activities_list
                    display_normal_summary(activities_list)
                break;
            i -= 1
    except IOError:
        return None
    return None

def display_normal_summary(activities_list):
    print(colors.BOLD + "\nSummary of your day:\n" + colors.END)
    for activity in activities_list:
        activity = activity.rstrip("\n")
        splitted = activity.split("|")
        if len(splitted) >= 4:
            print(splitted[1] + "-->" + splitted[2] + "\t" + colors.TIME + colors.BOLD + splitted[3] + colors.END + ":\t" + colors.TITLE + colors.BOLD + splitted[0] + colors.END)
        else:
            print(splitted[1] + "-->...\t...:\t" + colors.TITLE + colors.BOLD + splitted[0] + colors.END)

def check_normal_summary(activity):
    activities_list = get_activities_list()
    if activities_list:
        display_normal_summary(activities_list)
    else:
        print(colors.REMOVE + "No summary to display" + colors.END)
    if activity:
        print(colors.WARNING + colors.BOLD + "/!\\Warning/!\\" + colors.END + " Activities are not taken in count when -s, --summary option is specified")

def display_readable_summary(activities_list):
    activities_sum = []
    for activity in activities_list:
        activity = activity.rstrip("\n")
        splitted = activity.split("|")
        if len(splitted) >= 4:
            if "h" in splitted[3]:
                hours = int(splitted[3].split("h")[0])
                minutes = int(splitted[3].split("h")[1].rstrip("m"))
            else:
                hours = 0
                minutes = int(splitted[3].rstrip("m"))
            if splitted[0] not in chain(*activities_sum):
                activities_sum.append([splitted[0], hours, minutes])
            else:
                for elem in activities_sum:
                    if splitted[0] in elem[0]:
                        elem[1] += hours
                        elem[2] += minutes
                        break;
    print(colors.BOLD + "\nSummary of your day:\n" + colors.END)
    total_hours = 0
    total_minutes = 0
    for elem in activities_sum:
        elem[1] += int(elem[2] / 60)
        elem[2] %= 60
        total_hours += elem[1]
        total_minutes += elem[2]
        if elem[1] and elem[2]:
            time = "{}h{}m".format(elem[1], elem[2])
        elif not elem[2]:
            time = "{}h".format(elem[1])
        else:
            time = "{}m".format(elem[2])
        print(colors.TIME + colors.BOLD + time + colors.END + ":\t" + colors.BOLD + colors.TITLE + elem[0] + colors.END)
    total_hours += int(total_minutes / 60)
    total_minutes %= 60
    if total_hours and total_minutes:
        time = "{}h{}m".format(total_hours, total_minutes)
    elif not total_minutes:
        time = "{}h".format(total_hours)
    else:
        time = "{}m".format(total_minutes)
    print(colors.CYAN + colors.BOLD + colors.UNDERLINE + "\nTotal work time:\t" + colors.END + colors.CYAN + colors.BOLD + time + colors.END)

def check_readable_summary(activity):
    activities_list = get_activities_list()
    if activities_list:
        display_readable_summary(activities_list)
    else:
        print(colors.REMOVE + "No summary to display" + colors.END)
    if activity:
        print(colors.WARNING + colors.BOLD + "/!\\Warning/!\\" + colors.END + " Activities are not taken in count when -rs, --readable-summary option is specified")

def main():
    parse = get_args()
    try:
        args = parse.parse_args()
    except SystemExit:
        return 1

    reset_settings_if_needed(args.reset)
    write_stock_path(args.change_path)
    clear_stock_if_needed(args.clear)
    if args.summary:
        check_normal_summary(args.Activity)
    elif args.readable_summary:
        check_readable_summary(args.Activity)
    else:
        write_activity(args.Activity, args.previous)
    return 0

if __name__ == "__main__":
    exit(main())
