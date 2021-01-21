
def getwatt(node, from_ts, to_ts):
    """Get power values from Grid'5000 Lyon Wattmetre (requires Execo)

    :param node: Node name

    :param from_ts: Time from which metric is collected, as an integer Unix timestamp

    :param from_ts: Time until which metric is collected, as an integer Unix timestamp

    :return: A list of (timestamp, value) tuples.
    """

    import datetime
    import requests
    import gzip
    import time
    from execo_g5k import get_host_attributes

    watt = []
    node_wattmetre = get_host_attributes(node)['sensors']['power']['via']['pdu'][0]
    for ts in range(int(from_ts), int(to_ts)+3600, 3600):
        suffix = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H')
        if suffix != datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%dT%H'):
            suffix += ".gz"
        data=requests.get("http://wattmetre.lyon.grid5000.fr/data/"+node_wattmetre['uid']+"-log/power.csv."+suffix).content
        if suffix.endswith(".gz"):
            data = gzip.decompress(data)
        for l in str(data).split('\\n')[1:-1]:
            l = l.split(',')
            if l[3] == 'OK' and l[4+node_wattmetre['port']] != '':
                ts, value = (float(l[2]), float(l[4+node_wattmetre['port']]))
                if from_ts <= ts and ts <= to_ts:
                    watt.append((ts, value))
        if not suffix.endswith(".gz"):
            break
    return watt
