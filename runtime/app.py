import os
import importlib
import redis
import json
import time
import pandas as pd
import numpy as np

REDIS_HOST = os.getenv('REDIS_HOST', "localhost")
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_INPUT_KEY = os.getenv('REDIS_INPUT_KEY', None)
REDIS_OUTPUT_KEY = os.getenv('REDIS_OUTPUT_KEY', None)

INTERVAL_TIME = int(os.getenv('INTERVAL', 15))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT,
                       charset="utf-8", decode_responses=True)

module_loader = importlib.util.find_spec('custom_module')

import custom_module
from context import Context
context = Context(host=REDIS_HOST, port=REDIS_PORT,
                  input_key=REDIS_INPUT_KEY, output_key=REDIS_OUTPUT_KEY)

while True:
    data = None
    output = None
    data = r.get(REDIS_INPUT_KEY)

    if data:
        data = json.loads(data)
        output = custom_module.handler(data, context)

        if output and REDIS_OUTPUT_KEY:
            r.set(REDIS_OUTPUT_KEY, json.dumps(output))
        context.set_last_execution()

    time.sleep(INTERVAL_TIME)
