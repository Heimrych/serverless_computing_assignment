import streamlit as st
import pandas as pd
import redis
import json
from time import sleep

st.title('Monitoring Dashboard')
holder = st.empty()
holder2 = st.empty()
holder3 = st.empty()

past_metrics_60sec = {'cpu0': [], 'cpu1': [], 'cpu2': [], 'cpu3': [], 'cpu4': [], 'cpu5': [], 'cpu6': [], 'cpu7': [], 'cpu8': [], 'cpu9': [], 'cpu10': [], 'cpu11': [], 'cpu12': [], 'cpu13': [], 'cpu14': [], 'cpu15': [], 'n_pids': []}
past_metrics_60min = {'cpu0': [], 'cpu1': [], 'cpu2': [], 'cpu3': [], 'cpu4': [], 'cpu5': [], 'cpu6': [], 'cpu7': [], 'cpu8': [], 'cpu9': [], 'cpu10': [], 'cpu11': [], 'cpu12': [], 'cpu13': [], 'cpu14': [], 'cpu15': [], 'n_pids': []}

while True:
    # Fetch Redis data
    redis_data = redis.Redis(host='192.168.121.189', port='6379').get('augustolessa-proj3-output')
    json_data = json.loads(redis_data)

    # Setup cpu df data
    data = {}
    filtered_data_60sec = {k: v for k, v in json_data.items() if k.startswith('avg-util-cpu') and k.endswith('60sec')}
    filtered_data_60sec = {k.split("-")[2]:v for k,v in filtered_data_60sec.items()}
    for k,v in filtered_data_60sec.items():
        data[k] = [*past_metrics_60sec[k]]
        data[k].append(v)
        past_metrics_60sec[k].append(v)
        if len(past_metrics_60sec[k]) > 10:
            past_metrics_60sec[k].pop(0)

    df = pd.DataFrame.from_dict(data)
    holder.line_chart(df)
    
    # Setup cpu df data
    data = {}
    filtered_data_60min = {k: v for k, v in json_data.items() if k.startswith('avg-util-cpu') and k.endswith('60min')}
    filtered_data_60min = {k.split("-")[2]:v for k,v in filtered_data_60min.items()}
    for k,v in filtered_data_60min.items():
        data[k] = [*past_metrics_60min[k]]
        data[k].append(v)
        past_metrics_60min[k].append(v)
        if len(past_metrics_60min[k]) > 10:
            past_metrics_60min[k].pop(0)

    df = pd.DataFrame.from_dict(data)
    holder2.line_chart(df)

    # Setup pid df data
    data = {}
    filtered_data_pids = {k: v for k, v in json_data.items() if k.startswith('avg-util-n_pids')}
    filtered_data_pids = {k.split("-")[2]:v for k,v in filtered_data_pids.items()}
    data["n_pids_60sec"] = [*past_metrics_60sec["n_pids"]]
    data["n_pids_60sec"].append(filtered_data_pids["n_pids"])
    past_metrics_60sec["n_pids"].append(filtered_data_pids["n_pids"])
    if len(past_metrics_60sec["n_pids"]) > 10:
        past_metrics_60sec["n_pids"].pop(0)

    df = pd.DataFrame.from_dict(data)
    holder3.line_chart(df)

    sleep(10)
