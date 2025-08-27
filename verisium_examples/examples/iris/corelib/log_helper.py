# Copyright 2022 Cadence Design Systems, Inc. All rights reserved worldwide.
#
# This source code ("Software") is part of the Indago API package, the proprietary
# and confidential information of Cadence or its licensors, and supplied
# subject to, and may be used only by Cadence's customer in accordance with a
# previously executed agreement between Cadence and that customer ("Customer").
#
# Permission is hereby granted to such Customer to use and make copies of this
# Software to connect and interact with a Cadence Indago product from
# Customer's Python program, subject to the following conditions:
#
# - Customer may not distribute, sell, or otherwise modify the Indago API package.
#
# - All copyright notices in this Software must be maintained on all included
#   Python libraries and packages used by Customer.
"""
Provides some log functions
"""

import logging
import os
import shutil
import glob
from datetime import datetime


log_file_name = ""


def set_logger(app_name: str):
    """Create an instance of the logger"""

    global log_file_name
    log_format = '[%(asctime)s] %(levelname)5s {%(filename)s:%(lineno)d} - %(message)s'
    time_stamp = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f'))
    log_file_name = f'{app_name}_logfile_{time_stamp}.log'

    # Set the ..iris/temp as default location when running inside Cadence
    if os.path.exists('/development/rels/users/dvcmida/iris/Temp'):
        log_file_name = os.path.join('/development/rels/users/dvcmida/iris/Temp', log_file_name)

    logging.basicConfig(filename=log_file_name,
                        filemode="w",
                        format=log_format,
                        level=logging.DEBUG)

def print_and_log(text_message, log_level=logging.INFO):
    """Print message into log file and print to the stdout """
    print(text_message)

    lines = text_message.split("\n")
    for text_line in lines:
        logging.log(log_level, text_line)

def copy_log_output_dir(destination_path: str):
    if destination_path is None or os.path.exists(destination_path) is False:
        logging.warning('Unable to copy logs, temporary folder does not exists or is unavailable')

    # if is running iris or out of cadence
    if os.path.exists(log_file_name):
        log_file_path_origin = log_file_name
        log_file_path_destination = os.path.join(destination_path, os.path.basename(log_file_name))
    else:
        log_file_path_origin = glob.glob(f'./{log_file_name}')[0]
        log_file_path_destination = destination_path + f'/{log_file_name}'

    if log_file_path_origin is not None and log_file_path_destination is not None:
        logging.info('Copying log to output folder: %s', log_file_path_destination)
        shutil.move(log_file_path_origin, log_file_path_destination)
    else:
        logging.error('Failed in copying ')
