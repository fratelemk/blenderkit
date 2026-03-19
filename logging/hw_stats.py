import platform
import subprocess

def get_host_cpu_cores():
    args = ["/usr/sbin/sysctl", "-n", "hw.ncpu"]
    return subprocess.check_output(args, text=True).strip()

def get_host_total_mem():
    args = ["/usr/sbin/sysctl", "-n", "hw.memsize"]
    return f"{(int(subprocess.check_output(args, text=True).strip()) / (1024 ** 3)):.0f} GB"

def get_host_cpu_name():
    args = ["/usr/sbin/sysctl", "-n", "machdep.cpu.brand_string"] 
    return subprocess.check_output(args, text=True).strip()

def get_host_name():
    args = ["/usr/sbin/sysctl", "-n", "kern.hostname"] 
    return subprocess.check_output(args, text=True).strip()

