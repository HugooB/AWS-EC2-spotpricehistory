import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np
import subprocess

def get_data():
    start_time = "2017-09-17T00:00:00"
    end_time = "2017-10-17T00:00:00"
    machines = ["m4.large", "m4.xlarge", "m4.2xlarge", "m4.4xlarge", "m4.10xlarge", "m4.16xlarge", "c4.large",
                "c4.xlarge", "c4.2xlarge", "c4.4xlarge", "c4.8xlarge"]

    print "Started downloading historical EC2 data, this process could take a while"
    for machine in machines:
        print "Now downloading data for: " + str(machine)
        cmd = "aws ec2 describe-spot-price-history --instance-types " +str(machine)+ " --start-time " +str(start_time)+ \
              " --end-time " +str(end_time)+ " --output text > Data/" +str(machine)+ ".txt"
        get = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)
        if get == 0:
            print "Downloading of " + str(machine) + " data successful"

def load_data_txt(path):
    # Give column names
    colums_names = ["Info", "Region", "InstanceType", "OS", "SpotPrice", "Time"]
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

def get_daily_averages(data):
    mean = data.groupby(['DayNameofWeek']).mean()
    mean = mean.iloc[:,0:1]
    median = data.groupby(['DayNameofWeek']).median()
    median = median.iloc[:,0:1]
    min_val = data.groupby(['DayNameofWeek']).min(axis=1)
    min_val = min_val.iloc[:,2:3]
    max_val = data.groupby(['DayNameofWeek']).max(axis=1)
    max_val = max_val.iloc[:,2:3]
    return mean, median, min_val, max_val

def visualize_data_per_week(df, machine, number):
    # Define the different regions
    regions = ["us-east-2a", "us-east-2b", "us-east-2c"]
    # Make a new figure
    plt.figure()
    # Plot all regions in this figure
    for region in regions:
        subset = df[df.Region == region]
        x = subset['Time']
        y = subset['SpotPrice']
        plt.plot(x, y, c=np.random.rand(3,))
    # Set labels
    plt.xlabel('Time')
    plt.ylabel('Spot price')
    # plt.show()
    text = machine + "_week_" + str(number)
    plt.savefig('Images/' + str('Plot of ') + "%s.png" % (text))

def visualize_data_per_month(df, machine):
    # Define the different regions
    regions = ["us-east-2a", "us-east-2b", "us-east-2c"]
    # Make a new figure
    plt.figure()
    # Plot all regions in this figure
    for region in regions:
        subset = df[df.Region == region]
        x = subset['Time']
        y = subset['SpotPrice']
        plt.plot(x, y, c=np.random.rand(3,))
    # Set labels
    plt.xlabel('Time')
    plt.ylabel('Spot price')
    # plt.show()
    text = machine + "_month_" + str(df.iloc[0]["Time"].strftime("%B"))
    print text
    plt.savefig('Images/' + str('Plot of ') + "%s.png" % (text))

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

if __name__ == '__main__':
    print "Program started"

    ######## DATA GATHERING
    answer = raw_input("Is data already present? Typ Y/N ")
    if answer == "y" or answer == "Y":
        print "Perfect, let's use that data!"
    elif answer == "n" | answer == "N":
        get_data()
    else:
        print "Wrong answer, terminating"

	######## DATA LOADING
    path = raw_input("Please enter the path of the .txt file you want to analyse: ")
    print "Loading data"
    data = load_data_txt(path)
    machine = data.iloc[0]["InstanceType"]
    print "Data loaded succesfully for machine " + str(machine)

    ######## DATA DIVISION IN WEEKS
    q = int(round(len(data.index) * 0.25))
    first_quarter = data[0:q]
    second_quarter = data[q:2*q]
    third_quarter = data[2*q:3*q]
    fourth_quarter = data[3*q:]
    weeks = [first_quarter, second_quarter, third_quarter, fourth_quarter]

    ####### DATA VISUALIZATION
    print "Visualize data per week"
    i = 0
    for week in weeks:
        visualize_data_per_week(week, machine, i)
        i = i+1

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

    print "The End"