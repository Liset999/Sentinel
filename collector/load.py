import time

LOADAVG_KEYS = (
        'load1',
        'load5',
        'load15'
    )

def get_loadavg(file_path = '/proc/loadavg'):
    with open(file_path,'r',encoding='utf-8') as f:
        return f.readline().strip()

def parse_loadavg():
    lines = get_loadavg().split()
    load_value = list(map(float,lines[0:3]))
    load_dict = dict(zip(LOADAVG_KEYS,load_value))
    return load_dict

if __name__ == '__main__':
    while True:
        load_dict = parse_loadavg()
        print(load_dict['load1'],load_dict['load5'],load_dict['load15'])
        time.sleep(1)


