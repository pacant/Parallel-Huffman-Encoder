import subprocess
import re
import matplotlib.pyplot as plt
import sys
import statistics

file = ["fileone.txt", "filetwenty.txt", "filefifty.txt"]

num_threads_list = [1, 2, 4, 8, 16, 32, 64]

num_runs = 15

execution_times = ([], [], [])
execution_times_ff = ([], [], [])
io_execution_times = ([], [], [])
io_execution_times_ff = ([], [], [])
sequential_time = []
io_sequential_time = []

# when delivering change this and let insert it in the command line
if sys.argv > 1:
    remote_host = sys.argv[1]
    ssh = 1

##############################################
print("Executing sequential on file " + file[0])
# Sequenziale
step_times = {'Reading': [], 'Counting': [],
              'Building': [], 'Encoding': [], 'Translating': [], 'Writing': []}
run_times = []
io_run_times = []
for _ in range(num_runs):
    if ssh == 1:
        remote_command = f'ssh {remote_host} "cd Huffman-Encoder && make && LD_PRELOAD=libjemalloc.so ./sequential_encoder {file[0]}"'
    else:
        remote_command = f'./sequential_encoder {file[0]}'
    process = subprocess.run(
        remote_command, shell=True, capture_output=True, text=True)
    output = process.stdout
    times = re.findall(r'(\d+) usec', output)

    io_run_times.append(sum(int(time) for time in times))
    run_times.append(sum(int(time) for time in times[1:-1]))


# media e outliers
io_min_time = min(io_run_times)
io_max_time = max(io_run_times)
io_run_times.remove(io_min_time)
io_run_times.remove(io_max_time)
io_sequential_time.append(int(statistics.mean(io_run_times)))

min_time = min(run_times)
max_time = max(run_times)
run_times.remove(min_time)
run_times.remove(max_time)
sequential_time.append(int(statistics.mean(run_times)))

print("Sequential time with I/O (1 MB): " +
      str(io_sequential_time[0]) + " usec")
print("Sequential time (1 MB): " + str(sequential_time[0]) + " usec")

###########################################

print("Executing sequential on file " + file[1])
# Sequenziale
run_times = []
io_run_times = []
for _ in range(num_runs):
    if ssh == 1:
        remote_command = f'ssh {remote_host} "cd Huffman-Encoder && make && LD_PRELOAD=libjemalloc.so ./sequential_encoder {file[1]}"'
    else:
        remote_command = f'./sequential_encoder {file[1]}'
    process = subprocess.run(
        remote_command, shell=True, capture_output=True, text=True)
    output = process.stdout
    times = re.findall(r'(\d+) usec', output)

    io_run_times.append(sum(int(time) for time in times))
    run_times.append(sum(int(time) for time in times[1:-1]))


# media e outliers
io_min_time = min(io_run_times)
io_max_time = max(io_run_times)
io_run_times.remove(io_min_time)
io_run_times.remove(io_max_time)
io_sequential_time.append(int(statistics.mean(io_run_times)))

min_time = min(run_times)
max_time = max(run_times)
run_times.remove(min_time)
run_times.remove(max_time)
sequential_time.append(int(statistics.mean(run_times)))

print("Sequential time with I/O (20 MB): " +
      str(io_sequential_time[1]) + " usec")
print("Sequential time (20 MB): " + str(sequential_time[1]) + " usec")


##############################################

print("Executing sequential on file " + file[2])
# Sequenziale

run_times = []
io_run_times = []
for _ in range(num_runs):
    if ssh == 1:
        remote_command = f'ssh {remote_host} "cd Huffman-Encoder && make && LD_PRELOAD=libjemalloc.so ./sequential_encoder {file[2]}"'
    else:
        remote_command = f'./sequential_encoder {file[2]}'
    process = subprocess.run(
        remote_command, shell=True, capture_output=True, text=True)
    output = process.stdout
    times = re.findall(r'(\d+) usec', output)
    for i, step in enumerate(step_times.keys()):
        step_times[step].append(int(times[i]))
    io_run_times.append(sum(int(time) for time in times))
    run_times.append(sum(int(time) for time in times[1:-1]))

for step in step_times:
    min_time = min(step_times[step])
    max_time = max(step_times[step])
    step_times[step].remove(min_time)
    step_times[step].remove(max_time)
    avg_times = {step: int(statistics.mean(times))
                 for step, times in step_times.items()}
# media e outliers
io_min_time = min(io_run_times)
io_max_time = max(io_run_times)
io_run_times.remove(io_min_time)
io_run_times.remove(io_max_time)
io_sequential_time.append(int(statistics.mean(io_run_times)))

min_time = min(run_times)
max_time = max(run_times)
run_times.remove(min_time)
run_times.remove(max_time)
sequential_time.append(int(statistics.mean(run_times)))

print("Sequential time with I/O (50 MB): " +
      str(io_sequential_time[2]) + " usec")
print("Sequential time (50 MB): " + str(sequential_time[2]) + " usec")

##############################################

plt.bar(step_times.keys(), avg_times.values())
plt.xlabel('Step')
plt.ylabel('Execution times (usec)')
plt.grid(True)
plt.title('Sequential execution times')
plt.savefig('plot/sequential_times.png')
plt.close()
##############################################

print("Executing with native threads on file " + file[0])
# Parallelo nativo
for num_threads in num_threads_list:
    run_times = []
    io_run_times = []
    for _ in range(num_runs):
        if ssh == 1:
            remote_command = f'ssh {remote_host} "cd Huffman-Encoder && make && LD_PRELOAD=libjemalloc.so ./encoder {file[0]} {num_threads} 0"'
        else:
            remote_command = f'./encoder {file[0]} {num_threads} 0'
        process = subprocess.run(
            remote_command, shell=True, capture_output=True, text=True)
        output = process.stdout
        times = re.findall(r'(\d+) usec', output)
        io_run_times.append(sum(int(time) for time in times))
        run_times.append(sum(int(time) for time in times[1:-1]))
    # media e outliers
    io_min_time = min(io_run_times)
    io_max_time = max(io_run_times)
    io_run_times.remove(io_min_time)
    io_run_times.remove(io_max_time)
    io_avg_time = int(statistics.mean(io_run_times))
    io_execution_times[0].append(io_avg_time)
    print("Parallel native threads time with " + str(num_threads) +
          " threads with I/O (1 MB): " + str(io_avg_time) + " usec")

    min_time = min(run_times)
    max_time = max(run_times)
    run_times.remove(min_time)
    run_times.remove(max_time)
    avg_time = int(statistics.mean(run_times))
    execution_times[0].append(avg_time)
    print("Parallel native threads time with " + str(num_threads) +
          " threads (1 MB): " + str(avg_time) + " usec")

##############################################

print("Executing with native threads on file " + file[1])
# Parallelo nativo
for num_threads in num_threads_list:
    run_times = []
    io_run_times = []
    for _ in range(num_runs):
        if ssh == 1:
            remote_command = f'ssh {remote_host} "cd Huffman-Encoder && make && LD_PRELOAD=libjemalloc.so ./encoder {file[1]} {num_threads} 0"'
        else:
            remote_command = f'./encoder {file[1]} {num_threads} 0'
        process = subprocess.run(
            remote_command, shell=True, capture_output=True, text=True)
        output = process.stdout
        times = re.findall(r'(\d+) usec', output)
        io_run_times.append(sum(int(time) for time in times))
        run_times.append(sum(int(time) for time in times[1:-1]))
    # media e outliers
    io_min_time = min(io_run_times)
    io_max_time = max(io_run_times)
    io_run_times.remove(io_min_time)
    io_run_times.remove(io_max_time)
    io_avg_time = int(statistics.mean(io_run_times))
    io_execution_times[1].append(io_avg_time)
    print("Parallel native threads time with " + str(num_threads) +
          " threads with I/O (20 MB): " + str(io_avg_time) + " usec")

    min_time = min(run_times)
    max_time = max(run_times)
    run_times.remove(min_time)
    run_times.remove(max_time)
    avg_time = int(statistics.mean(run_times))
    execution_times[1].append(avg_time)
    print("Parallel native threads time with " + str(num_threads) +
          " threads (20 MB): " + str(avg_time) + " usec")

##############################################

print("Executing with native threads on file " + file[2])
# Parallelo nativo
for num_threads in num_threads_list:
    run_times = []
    io_run_times = []
    for _ in range(num_runs):
        if ssh == 1:
            remote_command = f'ssh {remote_host} "cd Huffman-Encoder && make && LD_PRELOAD=libjemalloc.so ./encoder {file[2]} {num_threads} 0"'
        else:
            remote_command = f'./encoder {file[2]} {num_threads} 0'
        process = subprocess.run(
            remote_command, shell=True, capture_output=True, text=True)
        output = process.stdout
        times = re.findall(r'(\d+) usec', output)
        io_run_times.append(sum(int(time) for time in times))
        run_times.append(sum(int(time) for time in times[1:-1]))

    # media e outliers
    io_min_time = min(io_run_times)
    io_max_time = max(io_run_times)
    io_run_times.remove(io_min_time)
    io_run_times.remove(io_max_time)
    io_avg_time = int(statistics.mean(io_run_times))
    io_execution_times[2].append(io_avg_time)
    print("Parallel native threads time with " + str(num_threads) +
          " threads with I/O (50 MB): " + str(io_avg_time) + " usec")

    min_time = min(run_times)
    max_time = max(run_times)
    run_times.remove(min_time)
    run_times.remove(max_time)
    avg_time = int(statistics.mean(run_times))
    execution_times[2].append(avg_time)
    print("Parallel native threads time with " + str(num_threads) +
          " threads (50 MB): " + str(avg_time) + " usec")

##############################################

# Parallelo ff
print("Executing with FastFlow on file " + file[0])
for num_threads in num_threads_list:
    run_times = []
    io_run_times = []
    for _ in range(num_runs):
        if ssh == 1:
            remote_command = f'ssh {remote_host} "cd Huffman-Encoder && make && LD_PRELOAD=libjemalloc.so ./encoder {file[0]} {num_threads} 1"'
        else:
            remote_command = f'./encoder {file[0]} {num_threads} 1'
        process = subprocess.run(
            remote_command, shell=True, capture_output=True, text=True)
        output = process.stdout
        times = re.findall(r'(\d+) usec', output)
        io_run_times.append(sum(int(time) for time in times))
        run_times.append(sum(int(time) for time in times[1:-1]))

    # media e outliers
    io_min_time = min(io_run_times)
    io_max_time = max(io_run_times)
    io_run_times.remove(io_min_time)
    io_run_times.remove(io_max_time)
    io_avg_time = int(statistics.mean(io_run_times))
    io_execution_times_ff[0].append(io_avg_time)
    print("Parallel FF time with " + str(num_threads) +
          " threads with I/O (1 MB): " + str(io_avg_time) + " usec")

    min_time = min(run_times)
    max_time = max(run_times)
    run_times.remove(min_time)
    run_times.remove(max_time)
    avg_time = int(statistics.mean(run_times))
    execution_times_ff[0].append(avg_time)
    print("Parallel FF time with " + str(num_threads) +
          " threads (1 MB): " + str(avg_time) + " usec")

##############################################

# Parallelo ff
print("Executing with FastFlow on file " + file[1])
for num_threads in num_threads_list:
    run_times = []
    io_run_times = []
    for _ in range(num_runs):
        if ssh == 1:
            remote_command = f'ssh {remote_host} "cd Huffman-Encoder && make && LD_PRELOAD=libjemalloc.so ./encoder {file[1]} {num_threads} 1"'
        else:
            remote_command = f'./encoder {file[1]} {num_threads} 1'
        process = subprocess.run(
            remote_command, shell=True, capture_output=True, text=True)
        output = process.stdout
        times = re.findall(r'(\d+) usec', output)
        io_run_times.append(sum(int(time) for time in times))
        run_times.append(sum(int(time) for time in times[1:-1]))

    # media e outliers
    io_min_time = min(io_run_times)
    io_max_time = max(io_run_times)
    io_run_times.remove(io_min_time)
    io_run_times.remove(io_max_time)
    io_avg_time = int(statistics.mean(io_run_times))
    io_execution_times_ff[1].append(io_avg_time)
    print("Parallel FF time with " + str(num_threads) +
          " threads with I/O (20 MB): " + str(io_avg_time) + " usec")

    min_time = min(run_times)
    max_time = max(run_times)
    run_times.remove(min_time)
    run_times.remove(max_time)
    avg_time = int(statistics.mean(run_times))
    execution_times_ff[1].append(avg_time)
    print("Parallel FF time with " + str(num_threads) +
          " threads (20 MB): " + str(avg_time) + " usec")

##############################################

# Parallelo ff
print("Executing with FastFlow on file " + file[2])
for num_threads in num_threads_list:
    run_times = []
    io_run_times = []
    for _ in range(num_runs):
        if ssh == 1:
            remote_command = f'ssh {remote_host} "cd Huffman-Encoder && make && LD_PRELOAD=libjemalloc.so ./encoder {file[2]} {num_threads} 1"'
        else:
            remote_command = f'./encoder {file[2]} {num_threads} 1'
        process = subprocess.run(
            remote_command, shell=True, capture_output=True, text=True)
        output = process.stdout
        times = re.findall(r'(\d+) usec', output)
        io_run_times.append(sum(int(time) for time in times))
        run_times.append(sum(int(time) for time in times[1:-1]))

    # media e outliers
    io_min_time = min(io_run_times)
    io_max_time = max(io_run_times)
    io_run_times.remove(io_min_time)
    io_run_times.remove(io_max_time)
    io_avg_time = int(statistics.mean(io_run_times))
    io_execution_times_ff[2].append(io_avg_time)
    print("Parallel FF time with " + str(num_threads) +
          " threads with I/O (50 MB): " + str(io_avg_time) + " usec")

    min_time = min(run_times)
    max_time = max(run_times)
    run_times.remove(min_time)
    run_times.remove(max_time)
    avg_time = int(statistics.mean(run_times))
    execution_times_ff[2].append(avg_time)
    print("Parallel FF time with " + str(num_threads) +
          " threads (50 MB): " + str(avg_time) + " usec")

##############################################

#### 1 MB ####
speedup_1 = [sequential_time[0] / time for time in execution_times[0]]
speedup_ff_1 = [sequential_time[0] / time for time in execution_times_ff[0]]

scalability_1 = [execution_times[0][0] / time for time in execution_times[0]]
scalability_ff_1 = [execution_times_ff[0][0] /
                    time for time in execution_times_ff[0]]

io_scalability_1 = [io_execution_times[0][0] /
                    time for time in io_execution_times[0]]
io_speedup_1 = [io_sequential_time[0] / time for time in io_execution_times[0]]

io_speedup_ff_1 = [sequential_time[0] / time for time in execution_times_ff[0]]
io_scalability_ff_1 = [execution_times_ff[0][0] /
                       time for time in execution_times_ff[0]]

#### 10 MB ####
speedup_10 = [sequential_time[1] / time for time in execution_times[1]]
speedup_ff_10 = [sequential_time[1] / time for time in execution_times_ff[1]]

scalability_10 = [execution_times[1][0] / time for time in execution_times[1]]
scalability_ff_10 = [execution_times_ff[1][0] /
                     time for time in execution_times_ff[1]]

io_scalability_10 = [io_execution_times[1][0] /
                     time for time in io_execution_times[1]]
io_speedup_10 = [io_sequential_time[1] /
                 time for time in io_execution_times[1]]

io_speedup_ff_10 = [sequential_time[1] /
                    time for time in execution_times_ff[1]]
io_scalability_ff_10 = [execution_times_ff[1][0] /
                        time for time in execution_times_ff[1]]

#### 50 MB ####
speedup_50 = [sequential_time[2] / time for time in execution_times[2]]
speedup_ff_50 = [sequential_time[2] / time for time in execution_times_ff[2]]

scalability_50 = [execution_times[2][0] / time for time in execution_times[2]]
scalability_ff_50 = [execution_times_ff[2][0] /
                     time for time in execution_times_ff[2]]

io_scalability_50 = [io_execution_times[2][0] /
                     time for time in io_execution_times[2]]
io_speedup_50 = [io_sequential_time[2] /
                 time for time in io_execution_times[2]]

io_speedup_ff_50 = [sequential_time[2] /
                    time for time in execution_times_ff[2]]
io_scalability_ff_50 = [execution_times_ff[2][0] /
                        time for time in execution_times_ff[2]]

# Crea il grafico dei tempi di esecuzione con I/O
plt.plot(num_threads_list,
         io_execution_times[0], 'o-', label='1 MB Native threads')
plt.plot(num_threads_list,
         io_execution_times_ff[0], 'o-', label='1 MB FastFlow')
plt.plot(num_threads_list,
         io_execution_times[1], 'o-', label='20 MB Native threads')
plt.plot(num_threads_list,
         io_execution_times_ff[1], 'o-', label='20 MB FastFlow')
plt.plot(num_threads_list,
         io_execution_times[2], 'o-', label='50 MB Native threads')
plt.plot(num_threads_list,
         io_execution_times_ff[2], 'o-', label='50 MB FastFlow')
plt.legend()
plt.xlabel('Number of threads')
plt.ylabel('Execution times (usec)')
plt.grid(True)
plt.title('Execution times plot with I/O')
plt.savefig('plot/execution_times_IO.png')
plt.close()

# Crea il grafico della scalability con IO
plt.plot(num_threads_list, io_scalability_1, 'o-', label='1 MB Native threads')
plt.plot(num_threads_list, io_scalability_ff_1, 'o-', label='1 MB FastFlow')
plt.plot(num_threads_list, io_scalability_10,
         'o-', label='20 MB Native threads')
plt.plot(num_threads_list, io_scalability_ff_10, 'o-', label='20 MB FastFlow')
plt.plot(num_threads_list, io_scalability_50,
         'o-', label='50 MB Native threads')
plt.plot(num_threads_list, io_scalability_ff_50,
         'o-', label='50 MB FastFlow')
plt.legend()
plt.xlabel('Number of threads')
plt.ylabel('Scalability')
plt.grid(True)
plt.title('Scalability plot with I/O')
plt.savefig('plot/scalability_io.png')
plt.close()

# Crea il grafico della scalability senza I/0
plt.plot(num_threads_list, scalability_1, 'o-', label='1 MB Native threads')
plt.plot(num_threads_list, scalability_ff_1, 'o-', label='1 MB FastFlow')
plt.plot(num_threads_list, scalability_10,
         'o-', label='20 MB Native threads')
plt.plot(num_threads_list, scalability_ff_10, 'o-', label='20 MB FastFlow')
plt.plot(num_threads_list, scalability_50,
         'o-', label='50 MB Native threads')
plt.plot(num_threads_list, scalability_ff_50, 'o-', label='50 MB FastFlow')
plt.legend()
plt.xlabel('Number of threads')
plt.ylabel('Scalability')
plt.grid(True)
plt.title('Scalability plot')
plt.savefig('plot/scalability.png')
plt.close()

# Crea il grafico dello speedup CON I/O
plt.plot(num_threads_list, io_speedup_1, 'o-', label='1 MB Native threads')
plt.plot(num_threads_list, io_speedup_ff_1, 'o-', label='1 MB FastFlow')
plt.plot(num_threads_list, io_speedup_10, 'o-', label='20 MB Native threads')
plt.plot(num_threads_list, io_speedup_ff_10, 'o-', label='20 MB FastFlow')
plt.plot(num_threads_list, io_speedup_50, 'o-', label='50 MB Native threads')
plt.plot(num_threads_list, io_speedup_ff_50, 'o-', label='50 MBFastFlow')
plt.legend()
plt.xlabel('Number of threads')
plt.ylabel('Speedup')
plt.grid(True)
plt.title('Speedup plot with I/O')
plt.savefig('plot/speedup_io.png')
plt.close()

# Crea il grafico dello speedup SENZA I/O
plt.plot(num_threads_list, speedup_1, 'o-', label='1 MB Native threads')
plt.plot(num_threads_list, speedup_ff_1, 'o-', label='1 MB FastFlow')
plt.plot(num_threads_list, speedup_10, 'o-', label='20 MB Native threads')
plt.plot(num_threads_list, speedup_ff_10, 'o-', label='20 MB FastFlow')
plt.plot(num_threads_list, speedup_50, 'o-', label='50 MB Native threads')
plt.plot(num_threads_list, speedup_ff_50, 'o-', label='50 MBFastFlow')
plt.legend()
plt.xlabel('Number of threads')
plt.ylabel('Speedup')
plt.grid(True)
plt.title('Speedup plot without I/O')
plt.savefig('plot/speedup.png')
plt.close()
