import pandas as pd
from tkinter import filedialog as fd
from tkinter import simpledialog
import tkinter as tk
import os

# Parameters
MAX_TIME_BETWEEN_EVENTS = 2000  # ms
MIN_BURST_DURATION = 10000  # ms
MIN_BURST_FREQUENCY = 2  # Hz

# Function to calculate burst frequency (events/second)
def burst_frequency(num_events, burst_duration):
    return (num_events / burst_duration) * 1000

def open_file_selection():
    file_path = fd.askopenfilename()
    if file_path:  # Check if a file was selected
        file_extension = os.path.splitext(file_path)[1]  # Get the file extension
        return file_path, file_extension  # Return both the file path and its extension
    
    return None, None  # Return None if no file was selected

# Load the data
file_path, file_extension = open_file_selection()
if file_path is None:
    print("No file selected")
    exit()
if file_extension != '.atf':
    print("Invalid file format, you must choose a .atf file")
    exit()

# Read the file, and strip extra spaces from column names
#data = pd.read_csv(file_path, sep='\s+', engine='python', header=0, usecols=[0, 1, 2], names=['Event Start Time (ms)', 'Event End Time (ms)', 'Peak Amp (mV)'])#!change to see original excell
#4 5 7
df = pd.read_csv(file_path, sep='\t', skiprows=2, encoding='ISO-8859-1')
data = df.iloc[:, [4, 5, 7]]


print(data)
bursts = []
current_burst = []
current_burst_start = None

# Process events
for index, row in data.iterrows():
    start_time = row['Event Start Time (ms)']
    end_time = row['Event End Time (ms)']

    # If it's the first event of the burst
    if not current_burst:
        current_burst.append(row)
        current_burst_start = start_time
        continue

    # Check the time gap between current event and previous one
    prev_end_time = current_burst[-1]['Event End Time (ms)']
    time_gap = start_time - prev_end_time

    if time_gap <= MAX_TIME_BETWEEN_EVENTS:
        current_burst.append(row)
    else:
        # End the current burst and evaluate it
        burst_duration = current_burst[-1]['Event End Time (ms)'] - current_burst_start
        num_events = len(current_burst)
        if burst_duration >= MIN_BURST_DURATION and burst_frequency(num_events, burst_duration) >= MIN_BURST_FREQUENCY:
            bursts.append(current_burst)
        
        # Start a new burst
        current_burst = [row]
        current_burst_start = start_time

# Check the last burst
if current_burst:
    burst_duration = current_burst[-1]['Event End Time (ms)'] - current_burst_start
    num_events = len(current_burst)
    if burst_duration >= MIN_BURST_DURATION and burst_frequency(num_events, burst_duration) >= MIN_BURST_FREQUENCY:
        bursts.append(current_burst)

#print(bursts[0])
# Output results
print('-------------------------------------------------------')
print("Burst Detection Results:")
print(f"Number of valid bursts: {len(bursts)}")
if len(bursts) == 0:
    exit()
print(f"Average Number of Events: {sum(len(burst) for burst in bursts) / len(bursts)}") #! maybe meter int
print(f"Average Burst Duration: {sum(burst[-1]['Event End Time (ms)'] - burst[0]['Event Start Time (ms)'] for burst in bursts) / len(bursts)} ms") #!float com 3 casas e segundos
print(f"Average Burst Frequency: {sum(burst_frequency(len(burst), burst[-1]['Event End Time (ms)'] - burst[0]['Event Start Time (ms)']) for burst in bursts) / len(bursts)} Hz")    #!float com 3 casas     
print(f"Average Peak Amplitude: {sum(sum(event['Peak Amp (mV)'] for event in burst) for burst in bursts) / (sum(len(burst)for burst in bursts))} mV") #!esta diferente dela..., float com 4 casas

print('-------------------------------------------------------')
print("Detailed Resuslts:")
for i, burst in enumerate(bursts):
    print(f"Burst {i+1}: {len(burst)} events, duration = {burst[-1]['Event End Time (ms)'] - burst[0]['Event Start Time (ms)']} ms, frequency = {burst_frequency(len(burst), burst[-1]['Event End Time (ms)'] - burst[0]['Event Start Time (ms)'])} Hz, average peak amplitude = {sum(event['Peak Amp (mV)'] for event in burst)/len(burst)} mV")
#!ok, flaot com 3 casas e segundoos, flao com3 casas, 4 casas


#todo:
#mudar unidades
#fazer UI para selecionar paramentros ou selecionar bulk
#fazer bulk
#compilar + imagem fixe
#graseful death na leitura e nos calculos