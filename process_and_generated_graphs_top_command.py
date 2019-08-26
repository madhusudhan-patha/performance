import re
import pygal


class GenerateReports(object):

    def __init__(self):
        self.cpu_time = []

    def plot_cpu_load_graph(self, time_interval, cpu_load):
        graph = pygal.Line(x_label_rotation=-90)
        graph.title = '% CPU Load over time.'
        graph.x_labels = time_interval
        graph.add('CPU load', cpu_load)
        graph.render_to_file('cpu_load.svg')

    def plot_cpu_load(self, time_interval, top_lines):
        cpu_load = []
        for row in top_lines:
            cpu_load.append(self.get_cpu_load(row))
        self.plot_cpu_load_graph(time_interval, cpu_load)

    def plot_cpu_stats_graph(self, cpu_time, cpu_us, cpu_sy, cpu_id, cpu_io_wait):
        graph = pygal.Line(x_label_rotation=-90)
        graph.title = '% CPU stats over time.'
        graph.x_labels = cpu_time
        graph.add('cpu_user', cpu_us)
        graph.add('cpu_system', cpu_sy)
        graph.add('cpu_idle', cpu_id)
        graph.add('cpu_IO_wait', cpu_io_wait)
        graph.render_to_file('cpu_usage_stats.svg')

    def plot_cpu_stats(self, cpu_time, cpu_stats):
        cpu_us = []
        cpu_sy = []
        cpu_id = []
        cpu_io_wait = []
        for line in cpu_stats:
            cpu_us_value, cpu_sy_value, cpu_id_value, cpu_io_wait_value = self.get_cpu_statistics(line)
            cpu_us.append(cpu_us_value)
            cpu_sy.append(cpu_sy_value)
            cpu_id.append(cpu_id_value)
            cpu_io_wait.append(cpu_io_wait_value)
        self.plot_cpu_stats_graph(cpu_time, cpu_us, cpu_sy, cpu_id, cpu_io_wait)

    def get_matching_lines(self, file, pattern):
        matched_lines = []
        lines = file.readlines()
        for line in lines:
            if pattern in line:
                matched_lines.append(line)
        return matched_lines

    def get_cpu_load(self, line):
        top_row = line.split("  ")
        load_averages_string = top_row[2]
        p = re.compile('\d+.\d+')
        load_averages = p.findall(load_averages_string)
        return float(load_averages[0])

    def get_cpu_time(self, line):
        p = re.compile('\d+:\d+:\d+')
        cpu_time = p.findall(line)
        return cpu_time[0]

    def get_cpu_statistics(self, line):
        p = re.compile('\d+.\d+')
        cpu_usage_stats = p.findall(line)
        cpu_us = float(cpu_usage_stats[0])
        cpu_sy = float(cpu_usage_stats[1])
        cpu_id = float(cpu_usage_stats[3])
        cpu_io_wait = float(cpu_usage_stats[4])
        return cpu_us, cpu_sy, cpu_id, cpu_io_wait

    def generate_cpu_load_and_usage_statistics(self):
        with open("../testdata/top_output.txt", "r") as top_output_file:
            top_lines = self.get_matching_lines(top_output_file, 'top -')
            for line in top_lines:
                self.cpu_time.append(self.get_cpu_time(line))
            self.plot_cpu_load(self.cpu_time, top_lines)

        with open("../testdata/top_output.txt", "r") as top_output_file:
            cpu_stats = self.get_matching_lines(top_output_file, '%Cpu(s)')
            self.plot_cpu_stats(self.cpu_time, cpu_stats)

    def generate_memory_usage_statistics(self):
        with open("../testdata/top_output.txt", "r") as top_output_file:
            mem_stats = self.get_matching_lines(top_output_file, 'KiB Mem')
            self.plot_mem_usage(self.cpu_time, mem_stats)

    def plot_mem_usage(self, cpu_time, mem_stats):
        mem_total = []
        mem_free = []
        mem_used = []
        mem_buff_cache = []
        for line in mem_stats:
            mem_total_value, mem_free_value, mem_used_value, mem_buff_cache_value = self.get_mem_statistics(line)
            mem_total.append(mem_total_value/1000)
            mem_free.append(mem_free_value/1000)
            mem_used.append(mem_used_value/1000)
            mem_buff_cache.append(mem_buff_cache_value/1000)
        self.plot_memory_stats_graph(self.cpu_time, mem_total, mem_free, mem_used, mem_buff_cache)

    def get_mem_statistics(self, line):
        p = re.compile('\d+')
        mem_usage_stats = p.findall(line)
        mem_total = int(mem_usage_stats[0])
        mem_free = int(mem_usage_stats[1])
        mem_used = int(mem_usage_stats[2])
        mem_buff_cache = int(mem_usage_stats[3])
        return mem_total, mem_free, mem_used, mem_buff_cache

    def plot_memory_stats_graph(self, cpu_time, mem_total, mem_free, mem_used, mem_buff_cache):
        from pygal.style import NeonStyle
        graph = pygal.Line(x_label_rotation=-90, width=2000, height=600, spacing=20,style=NeonStyle)
        graph.title = '% Memory stats over time in Mb'
        graph.x_labels = cpu_time
        graph.add('Memory Total', mem_total)
        graph.add('Memory Free', mem_free)
        graph.add('Memory Used', mem_used)
        graph.add('Memory Buffer cache', mem_buff_cache)
        graph.render_to_file('memory_usage_stats.svg')

    def get_process_memory_usage(self, process):
        process_usage = []
        average_process_usage = []
        iteration = 0
        with open("../testdata/top_output.txt", "r") as top_output_file:
            for line in top_output_file:
                if line.startswith('  PID '):
                    if iteration == 0:
                        print('in iteration 0')
                    else:
                        avg = self.get_average(process_usage)
                        print(avg)
                        average_process_usage.append(avg)
                        process_usage = []
                    iteration += 1
                if line not in ['\n', '\r\n'] and line.find(process) >= 0:
                    process_details = line.split()
                    # PID USER      PR  NI    VIRT    RES    SHR S %CPU %MEM     TIME+ COMMAND
                    mem = process_details[9]
                    process_usage.append(float(mem))

    def get_average(self, usage_list):
        try:
            avg = sum(usage_list)/len(usage_list)
            return round(avg, 5)
        except ZeroDivisionError as e:
            print(e.message)


if __name__ == "__main__":
    gr = GenerateReports()
    gr.generate_cpu_load_and_usage_statistics()
    gr.generate_memory_usage_statistics()
    gr.get_process_memory_usage('jmeter+')
