TCP_STATES = {
    "01": "ESTABLISHED",
    "02": "SYN_SENT",
    "03": "SYN_RECV",
    "04": "FIN_WAIT1",
    "05": "FIN_WAIT2",
    "06": "TIME_WAIT",
    "07": "CLOSE",
    "08": "CLOSE_WAIT",
    "09": "LAST_ACK",
    "0A": "LISTEN",
    "0B": "CLOSING",
    "0C": "NEW_SYN_RECV",
}

def parse_tcp(file_path = '/proc/net/tcp'):

    metrics = {state: 0 for state in TCP_STATES.values()}

    with open(file_path,'r',encoding='utf-8') as f:
        next(f)
        for line in f:
            st_hex = line[34:36]
            if st_hex in TCP_STATES:
                metrics[TCP_STATES[st_hex]] += 1

    return metrics

if __name__ == '__main__':
    matrics = parse_tcp()
    for state,count in matrics.items():
        print(f'{state}: {count}')









