import time
import os

PROC_DIR = os.environ.get("PROC_DIR", "/proc")

def get_mem (file_path=os.path.join(PROC_DIR, "meminfo")):
    with open(file_path,'r',encoding='utf-8') as f:
        mem = {}
        target_key = ['MemTotal','MemFree','MemAvailable']
        for line in f:
            key = line.split(':',1)[0]

            if key in target_key:
                value = int(line.split()[1])
                mem[key] = value
            if len(mem) == 3:
                break
    return mem

def calculate_mem ():
    mem = get_mem()
    mem_usage = (1 - (mem['MemAvailable'] / mem['MemTotal'])) * 100
    return round(mem_usage,2)
if __name__ == "__main__":
    while True:
        mem_usage = calculate_mem()
        print(f'{mem_usage}%')
        time.sleep(1)





