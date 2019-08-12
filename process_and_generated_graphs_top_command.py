import re
import pygal

def plot_cpu_load_graph(cpu_time, cpu_load):
    graph = pygal.Line(x_label_rotation=-90)
    graph.title = '% CPU Load over time.'
    graph.x_labels = cpu_time
    graph.add('CPU load',  cpu_load)
    graph.render_to_file('cpu_load.svg')


def plot_cpu_load(cpu_time, top_lines):
    cpu_load = []
    for line in top_lines:
        cpu_load.append(get_cpu_load(line))
    plot_cpu_load_graph(cpu_time, cpu_load)
   

def plot_cpu_stats_graph(cpu_time, cpu_us, cpu_sy, cpu_id,cpu_io_wait):
    graph = pygal.Line(x_label_rotation=-90)
    graph.title = '% CPU stats over time.'
    graph.x_labels = cpu_time
    graph.add('cpu_user',  cpu_us)
    graph.add('cpu_system', cpu_sy)
    graph.add('cpu_idle', cpu_id)
    graph.add('cpu_IO_wait', cpu_io_wait)
    graph.render_to_file('cpu_stats.svg')    
    
def plot_cpu_stats(cpu_time, cpu_stats):
    cpu_us = []
    cpu_sy = []
    cpu_id = []
    cpu_io_wait = []
    for line in cpu_stats:
        cpu_us_value, cpu_sy_value, cpu_id_value, cpu_io_wait_value = get_cpu_statistics(line)
        cpu_us.append(cpu_us_value)
        cpu_sy.append(cpu_sy_value)
        cpu_id.append(cpu_id_value)
        cpu_io_wait.append(cpu_io_wait_value)        
    plot_cpu_stats_graph(cpu_time, cpu_us, cpu_sy, cpu_id,cpu_io_wait)

def get_matching_lines(file, pattern):
    matched_lines = []
    lines = file.readlines()
    for line in lines:
        if(pattern in line):
            matched_lines.append(line)
    return matched_lines
    
def get_cpu_load(line):
    top_row = line.split("  ")
    load_averages_string = top_row[2]
    p = re.compile('\d+.\d+')
    load_averages = p.findall(load_averages_string)
    return float(load_averages[0])

def get_cpu_time(line):
    p = re.compile('\d+:\d+:\d+')
    cpu_time = p.findall(line)
    return cpu_time[0]

def get_cpu_statistics(line):    
    p = re.compile('\d+.\d+')
    cpu_usage_stats = p.findall(line)
    cpu_us = float(cpu_usage_stats[0])
    cpu_sy = float(cpu_usage_stats[1])
    cpu_id = float(cpu_usage_stats[3])
    cpu_io_wait = float(cpu_usage_stats[4])
    return cpu_us,cpu_sy,cpu_id,cpu_io_wait


    
cpu_time = []
    
with open("top_op.txt","r") as file:
    top_lines = get_matching_lines(file, 'top -')

    for line in top_lines:
        cpu_time.append(get_cpu_time(line))
    plot_cpu_load(cpu_time, top_lines)
    
with open("top_op.txt","r") as file:
    cpu_stats = get_matching_lines(file, '%Cpu(s)')
    plot_cpu_stats(cpu_time, cpu_stats)

