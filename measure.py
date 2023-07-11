import subprocess
import re
import matplotlib.pyplot as plt
import sys
import statistics
import argparse


files = []
ssh = 1
parser = argparse.ArgumentParser()
parser.add_argument('-ssh', help='SSH remote host')
parser.add_argument('files', nargs='+', help='Input files')
args = parser.parse_args()

files = args.files
ssh = args.ssh

num_threads_list = [1, 2, 4, 8, 16, 32, 64]

num_runs = 3
execution_times = []
execution_times_ff = []
io_execution_times = []
io_execution_times_ff = []
sequential_time = []
io_sequential_time = []

##############################################

for file in files:
    print("Executing sequential on file " + file)
    # Sequenziale
    step_times = {'Reading': [], 'Counting': [],
                  'Building': [], 'Encoding': [], 'Translating': [], 'Writing': []}
    run_times = []
    io_run_times = []
    for _ in range(num_runs):
        if ssh == 1:
            remote_command = f'ssh {remote_host} "cd Huffman-Encoder && make && LD_PRELOAD=libjemalloc.so ./sequential_encoder {file}"'
        else:
            remote_command = f'make && LD_PRELOAD=libjemalloc.so ./sequential_encoder {file}'
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
          str(io_sequential_time[-1]) + " usec")
    print("Sequential time on: " + file + " " +
          str(sequential_time[-1]) + " usec")

    ###########################################

    print("Executing with native threads on file " + file)
    # Parallelo nativo
    execution_times.append([])
    io_execution_times.append([])
    for num_threads in num_threads_list:
        run_times = []
        io_run_times = []
        for _ in range(num_runs):
            if ssh == 1:
                remote_command = f'ssh {remote_host} "cd Huffman-Encoder && make && LD_PRELOAD=libjemalloc.so ./encoder {file} {num_threads} 0"'
            else:
                remote_command = f'make && LD_PRELOAD=libjemalloc.so ./encoder {file} {num_threads} 0'
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
        io_execution_times[-1].append(io_avg_time)
        print("Parallel native threads time with " + str(num_threads) +
              " threads with I/O on: " + file + " " + str(io_avg_time) + " usec")

        min_time = min(run_times)
        max_time = max(run_times)
        run_times.remove(min_time)
        run_times.remove(max_time)
        avg_time = int(statistics.mean(run_times))
        execution_times[-1].append(avg_time)
        print("Parallel native threads time with " + str(num_threads) +
              " threads on: " + file + " " + str(avg_time) + " usec")

    ##############################################

    # Parallelo ff
    execution_times_ff.append([])
    io_execution_times_ff.append([])
    print("Executing with FastFlow on file " + file)
    for num_threads in num_threads_list:
        run_times = []
        io_run_times = []
        for _ in range(num_runs):
            if ssh == 1:
                remote_command = f'ssh {remote_host} "cd Huffman-Encoder && make && LD_PRELOAD=libjemalloc.so ./encoder {file} {num_threads} 1"'
            else:
                remote_command = f'make && LD_PRELOAD=libjemalloc.so ./encoder {file} {num_threads} 1'
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
        io_execution_times_ff[-1].append(io_avg_time)
        print("Parallel FF time with " + str(num_threads) +
              " threads on: " + file + " " + str(io_avg_time) + " usec")

        min_time = min(run_times)
        max_time = max(run_times)
        run_times.remove(min_time)
        run_times.remove(max_time)
        avg_time = int(statistics.mean(run_times))
        execution_times_ff[-1].append(avg_time)
        print("Parallel FF time with " + str(num_threads) +
              " threads on: " + file + " " + str(avg_time) + " usec")

##############################################

# Crea il grafico dei tempi di esecuzione con I/O
for i, file in enumerate(files):
    plt.plot(num_threads_list,
             io_execution_times[i], 'o-', label=file + ' Native threads')
    plt.plot(num_threads_list,
             io_execution_times_ff[i], 'o-', label=file + ' FastFlow')

plt.legend()
plt.xlabel('Number of threads')
plt.ylabel('Execution times (usec)')
plt.grid(True)
plt.title('Execution times plot with I/O')
plt.savefig('plot/execution_times_IO.png')
plt.close()

# Crea il grafico della scalability con IO
for j, file in enumerate(files):
    plt.plot(num_threads_list, [io_execution_times[j][0] /
                                time for time in io_execution_times[j]], 'o-', label=file + ' Native threads')
    plt.plot(num_threads_list, [io_execution_times_ff[j][0] /
                                time for time in io_execution_times_ff[j]], 'o-', label=file + ' FastFlow')

plt.legend()
plt.xlabel('Number of threads')
plt.ylabel('Scalability')
plt.grid(True)
plt.title('Scalability plot with I/O')
plt.savefig('plot/scalability_io.png')
plt.close()

# Crea il grafico della scalability senza I/O
for i, file in enumerate(files):
    plt.plot(num_threads_list, [execution_times[j][0] /
                                time for time in execution_times[j]], 'o-', label=file + ' Native threads')
    plt.plot(num_threads_list, [execution_times_ff[j][0] /
                                time for time in execution_times_ff[j]], 'o-', label=file + ' FastFlow')

plt.legend()
plt.xlabel('Number of threads')
plt.ylabel('Scalability')
plt.grid(True)
plt.title('Scalability plot')
plt.savefig('plot/scalability.png')
plt.close()

# Crea il grafico dello speedup CON I/O
for i, file in enumerate(files):
    plt.plot(num_threads_list, [io_sequential_time[j] /
                                time for time in io_execution_times[j]], 'o-', label=file + ' Native threads')
    plt.plot(num_threads_list, [sequential_time[j] /
                                time for time in execution_times_ff[j]], 'o-', label=file + ' FastFlow')

plt.legend()
plt.xlabel('Number of threads')
plt.ylabel('Speedup')
plt.grid(True)
plt.title('Speedup plot with I/O')
plt.savefig('plot/speedup_io.png')
plt.close()

# Crea il grafico dello speedup SENZA I/O
for i, file in enumerate(files):
    plt.plot(num_threads_list, [sequential_time[j] /
                                time for time in execution_times[j]], 'o-', label=file + ' Native threads')
    plt.plot(num_threads_list, [sequential_time[j] /
                                time for time in execution_times_ff[j]], 'o-', label=file + ' FastFlow')

plt.legend()
plt.xlabel('Number of threads')
plt.ylabel('Speedup')
plt.grid(True)
plt.title('Speedup plot without I/O')
plt.savefig('plot/speedup.png')
plt.close()
