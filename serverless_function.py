import json
import redis

from datetime import datetime, timedelta

RELEVANT_KEYS = ['cpu_percent-0', 'cpu_percent-1', 'cpu_percent-2', 'cpu_percent-3', 'cpu_percent-4', 'cpu_percent-5', 'cpu_percent-6', 'cpu_percent-7', 'cpu_percent-8', 'cpu_percent-9', 'cpu_percent-10', 'cpu_percent-11', 'cpu_percent-12', 'cpu_percent-13', 'cpu_percent-14', 'cpu_percent-15', 'n_pids']

def to_datetime(timestamp):
  return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

def setup_env(env, input, current_timestamp):
  if 'previous_executions' not in env:
    env['previous_executions'] = {}
  env['previous_executions'][current_timestamp] = {}

  for relevant_key in RELEVANT_KEYS:
    env['previous_executions'][current_timestamp][relevant_key] = input[relevant_key]

def lazy_fix_env(env, datetime_lower_bound):
  for timestamp in env['previous_executions']:
      date = to_datetime(timestamp)
      if (date < datetime_lower_bound):
        del env['previous_executions'][timestamp]

def handler(input, context):
	env = context.env
	# env = {'cpu_percent-0': {'2022-07-16 21:54:54.869218': {'60sec': 85.7, '60min': 33.9}}}
	'''
	{'timestamp': '2022-07-16 19:08:54.869218', 'cpu_percent-0': 1.0, 'cpu_percent-1': 2.2, 'cpu_percent-2': 1.0, 'cpu_percent-3': 4.0, 'cpu_percent-4': 1.4, 'cpu_percent-5': 1.4, 'cpu_percent-6': 1.8, 'cpu_percent-7': 2.6, 'cpu_percent-8': 0.6, 'cpu_percent-9': 2.6, 'cpu_percent-10': 1.8, 'cpu_percent-11': 1.8, 'cpu_percent-12': 0.8, 'cpu_percent-13': 2.6, 'cpu_percent-14': 4.0, 'cpu_percent-15': 1.0, 'cpu_freq_current': 2666.760000000001, 'cpu_stats-ctx_switches': 15545135406, 'cpu_stats-interrupts': 8515418247, 'cpu_stats-soft_interrupts': 2801393181, 'cpu_stats-syscalls': 0, 'virtual_memory-total': 20986593280, 'virtual_memory-available': 13110468608, 'virtual_memory-percent': 37.5, 'virtual_memory-used': 7479259136, 'virtual_memory-free': 323936256, 'virtual_memory-active': 9059991552, 'virtual_memory-inactive': 7857815552, 'virtual_memory-buffers': 1236148224, 'virtual_memory-cached': 11947249664, 'virtual_memory-shared': 11337728, 'virtual_memory-slab': 3410583552, 'n_pids': 863, 'net_io_counters_eth0-bytes_sent': 3126008909, 'net_io_counters_eth0-bytes_recv': 10043666039, 'net_io_counters_eth0-packets_sent': 4524828, 'net_io_counters_eth0-packets_recv': 6864541, 'net_io_counters_eth0-errin': 0, 'net_io_counters_eth0-errout': 0, 'net_io_counters_eth0-dropin': 58, 'net_io_counters_eth0-dropout': 0}
	'''
	response = {}

	read_timestamp = to_datetime(input['timestamp'])
	read_timestamp_60sec_diff = read_timestamp - timedelta(seconds = 60)
	read_timestamp_60min_diff = read_timestamp - timedelta(seconds = 3600)

	setup_env(env, input, read_timestamp)
	lazy_fix_env(env, read_timestamp_60min_diff)

	target_entries_sec = []
	target_entries_min = []

	for timestamp in env['previous_executions']:
		date = to_datetime(timestamp)

		# We'll always consider this timestamp entry for the hourly moving average
		# because we know for sure we only have entries within the last hour (see `lazy_fix_env`)
		target_entries_min.append(env['previous_executions'][timestamp])

		if (date >= read_timestamp_60sec_diff):
			target_entries_sec.append(env['previous_executions'][timestamp])

	response = {}

	for relevant_key in RELEVANT_KEYS:
		num_cpus = 0
		key_metric_sum = 0
		for entry in target_entries_sec:
			num_cpus += 1
			key_metric_sum += entry[relevant_key]
		
		mov_avg_60sec = key_metric_sum / num_cpus if num_cpus else 0

		num_cpus = 0
		key_metric_sum = 0
		for entry in target_entries_min:
			num_cpus += 1
			key_metric_sum += entry[relevant_key]

		mov_avg_60min = key_metric_sum / num_cpus if num_cpus else 0

		response['avg-util-{}-60sec'.format(relevant_key.replace('_percent-', ''))] = mov_avg_60sec
		response['avg-util-{}-60min'.format(relevant_key.replace('_percent-', ''))] = mov_avg_60min
			
	

			
			# previous_moving_average = 0.0
			# averages_measured = 1
			# if relevant_key not in env:
			# 		env[relevant_key] = {}

			# read_timestamp_list = env[relevant_key].keys()
			# read_datetimes_list = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f"), read_timestamp_list))
			# if len(read_datetimes_list) > 0:
			# 		read_datetimes_list_60sec_diff = list(filter(lambda x: x > read_timestamp_60sec_diff, read_datetimes_list))
			# 		read_datetimes_list_60sec_diff.sort(reverse = True)
			# 		if len(read_datetimes_list_60sec_diff) > 0:
			# 				previous_moving_average_timestamp = read_datetimes_list_60sec_diff[0]
			# 				previous_moving_average = env[relevant_key][previous_moving_average_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")]['60sec']
			# 				averages_measured = len(read_datetimes_list_60sec_diff) + 1

			# env[relevant_key][input['timestamp']] = {}
			# if averages_measured > 1:
			# 		current_moving_average_60sec = (previous_moving_average * (averages_measured - 1) + input[relevant_key]) / averages_measured
			# else:
			# 		current_moving_average_60sec = input[relevant_key]
			# response['avg-util-{}-60sec'.format(relevant_key.replace('_percent-', ''))] = env[relevant_key][input['timestamp']]['60sec'] = current_moving_average_60sec

			# if len(read_datetimes_list) > 0:
			# 		read_datetimes_list_60min_diff = list(filter(lambda x: x > read_timestamp_60min_diff, read_datetimes_list))
			# 		read_datetimes_list_60min_diff.sort(reverse = True)
			# 		if len(read_datetimes_list_60min_diff) > 0:
			# 				previous_moving_average_timestamp = read_datetimes_list_60min_diff[0]
			# 				previous_moving_average = env[relevant_key][previous_moving_average_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")]['60min']
			# 				averages_measured = len(read_datetimes_list_60min_diff) + 1

			# if averages_measured > 1:
			# 		current_moving_average_60min = (previous_moving_average * (averages_measured - 1) + input[relevant_key]) / averages_measured
			# else:
			# 		current_moving_average_60min = input[relevant_key] 
			# response['avg-util-{}-60min'.format(relevant_key.replace('_percent-', ''))] = env[relevant_key][input['timestamp']]['60min'] = current_moving_average_60min

	return response

# r = redis.Redis(host='192.168.121.189', port=6379, db=0)
# metrics = r.get('metrics')
# print(handler(metrics,{"env": {}}))
