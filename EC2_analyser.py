import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np
import subprocess

def check_folder(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)

def get_data():
    # Check if data directory is present, otherwise create it
    check_folder("Data")
    # Change these dates to retrieve data from other timeframes
    # Make sure the format is "YYYY-MM-DDTHH:MM:SS"
    start_time = "2017-09-17T00:00:00"
    end_time = "2017-10-17T00:00:00"
    # Add more machine to this list if you like
    instances = ["m4.large", "m4.xlarge", "m4.2xlarge", "m4.4xlarge", "m4.10xlarge", "m4.16xlarge", "c4.large",
                "c4.xlarge", "c4.2xlarge", "c4.4xlarge", "c4.8xlarge"]

    print "Started downloading historical EC2 data, this process could take a while"
    for instance in instances:
        print "Now downloading data for: " + str(instance)
        cmd = "aws ec2 describe-spot-price-history --instance-types " + str(instance) + " --start-time " + str(start_time) + \
              " --end-time " + str(end_time) + " --output text > Data/" + str(instance) + ".txt"
        get = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)
        if get == 0:
            print "Downloading of " + str(instance) + " data successful"

def get_day_name(row):
    if row['DayofWeek'] == 0:
        return "Monday"
    elif row['DayofWeek'] == 1:
        return "Tuesday"
    elif row['DayofWeek'] == 2:
        return "Wednesday"
    elif row['DayofWeek'] == 3:
        return "Thursday"
    elif row['DayofWeek'] == 4:
        return "Friday"
    elif row['DayofWeek'] == 5:
        return "Saturday"
    elif row['DayofWeek'] == 6:
        return "Sunday"

def load_data_txt(path):
    # Give column names
    colums_names = ["Info", "VPC", "InstanceType", "OS", "SpotPrice", "Time"]
    # Read in the txt file
    print "Read in the file at " + str(path)
    df = pd.read_csv(path, sep="\t", decimal='.', names = colums_names)
    print "Convert dates"
    # Convert time column to datetime
    df.Time = pd.to_datetime(df['Time'])
    # Set index to this timestamp
    df.set_index('Time')
    # Remove unnecessary columns
    df = df[df.columns[1:]]
    df = df[df.OS == "Linux/UNIX"]
    df = df.drop('OS', 1)

    print "Add weekday information to dataframe for day-by-day analysis"
    # Add weekday information to dataframe
    df['DayofWeek'] = df.apply(lambda row: row['Time'].weekday(), axis=1)
    df['DayNameofWeek'] = df.apply(lambda row: get_day_name(row), axis=1)
    return df

def visualize_data_per_week(df, machine, number):
    # Define the different VPCs
    vpcs = df.VPC.unique()
    # Make a new figure
    plt.figure()
    # Plot all VPCs in this figure
    for vpc in vpcs:
        subset = df[df.VPC == vpc]
        x = subset['Time']
        y = subset['SpotPrice']
        plt.plot(x, y, c=np.random.rand(3,))
    # Set labels
    plt.xlabel('Time')
    plt.ylabel('Spot price')
    # plt.show()
    text = machine + "_week_" + str(number)
    plt.savefig('Images/' + str('Plot_of_') + "%s.png" % (text))

def visualize_data_per_month(df, machine):
    # Define the different VPCs
    vpcs = df.VPC.unique()
    # Make a new figure
    plt.figure()
    # Plot all VPCs in this figure
    for vpc in vpcs:
        subset = df[df.VPC == vpc]
        x = subset['Time']
        y = subset['SpotPrice']
        plt.plot(x, y, c=np.random.rand(3,))
    # Set labels
    plt.xlabel('Time')
    plt.ylabel('Spot price')
    # plt.show()
    text = machine + "_month_" + str(df.iloc[0]["Time"].strftime("%B"))
    plt.savefig('Images/' + str('Plot_of_') + "%s.png" % (text))

def get_daily_averages(data):
    # Group by day of the week and calculate means, median, min and max
    mean = data.groupby(['DayNameofWeek']).mean().sort_values(['DayofWeek'])
    # Delete first column for nice output
    mean = mean.iloc[:,0:1]
    median = data.groupby(['DayNameofWeek']).median().sort_values(['DayofWeek'])
    median = median.iloc[:,0:1]
    min_val = data.groupby(['DayNameofWeek']).min(axis=1).sort_values(['DayofWeek'])
    min_val = min_val.iloc[:,2:3]
    max_val = data.groupby(['DayNameofWeek']).max(axis=1).sort_values(['DayofWeek'])
    max_val = max_val.iloc[:,2:3]
    return mean, median, min_val, max_val

def visualize_stats(df, type, machine):
    plt.figure()
    df.plot(kind='bar')
    plt.xticks(rotation=20)
    plt.title(str(type) + " price of " + str(machine))
    # plt.show()
    text = "stats_" + machine + "_" + type
    plt.savefig('Images/' + str('Plot of ') + "%s.png" % (text))

if __name__ == '__main__':
    print "Program started"

    ######## DATA GATHERING
    answer = raw_input("Is data already present? Typ Y/N ")
    if answer == "y" or answer == "Y":
        print "Perfect, let's use that data!"
    elif answer == "n" or answer == "N":
        get_data()
    else:
        print "Wrong answer, terminating"

    ######## DATA LOADING
    print "The following data is available in Data folder:"
    ls = os.listdir("Data")
    for i in range(len(ls)):
        print ls[i]
    path = raw_input("Please enter the name of the .txt file you want to analyse: ")
    print "Loading data file " + str(path)
    data = load_data_txt('Data/' + path)
    machine = data.iloc[0]["InstanceType"]
    print "Data loaded successfully for machine " + str(machine)

    ######## DATA DIVISION IN WEEKS
    q = int(round(len(data.index) * 0.25))
    first_quarter = data[0:q]
    second_quarter = data[q:2*q]
    third_quarter = data[2*q:3*q]
    fourth_quarter = data[3*q:]
    weeks = [first_quarter, second_quarter, third_quarter, fourth_quarter]

    ####### DATA VISUALIZATION
    check_folder("Images")
    print "Visualize data per week"
    i = 0
    for week in weeks:
        visualize_data_per_week(week, machine, i)
        i = i + 1

    print "Visualize data for the whole month"
    visualize_data_per_month(data, machine)
    print "Done visualizing"

    ###### DATA STATISTICS
    mean, median, min_val, max_val = get_daily_averages(data)
    print "Data statistical analyses"
    print "For machine " + machine + " the descriptive statistics are:"
    print "----------------------------------------------"
    print "-- MEAN -- "
    print mean
    print "-- MEDIAN -- "
    print median
    print "-- MINIMUM -- "
    print min_val
    print "-- MAXIMUM -- "
    print max_val
    print "----------------------------------------------"

    visualize_stats(mean, "Mean", machine)
    visualize_stats(median, "Median", machine)
    visualize_stats(min_val, "Minimum", machine)
    visualize_stats(max_val, "Maximum", machine)

    print "Program finished successfully"
