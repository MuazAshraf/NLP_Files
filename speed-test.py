import speedtest as st
def speedtest():
    test = st.Speedtest()
    down_speed = test.download()
    down_speed = round(down_speed /10**6,2)
    print("Downloading Speed in Mbps: ", down_speed)

    up_speed = test.upload()
    up_speed = round(up_speed /10**6,2)
    print("Uploading Speed in Mbps: ", up_speed)

    ping = test.results.ping
    print("Ping: ",ping)
speedtest()