# Copyright 2023 Cadence Design Systems, Inc. All rights reserved worldwide.
#
# This source code ("Software") is part of the Verisium Debug API package, the proprietary
# and confidential information of Cadence or its licensors, and supplied
# subject to, and may be used only by Cadence's customer in accordance with a
# previously executed agreement between Cadence and that customer ("Customer").
#
# Permission is hereby granted to such Customer to use and make copies of this
# Software to connect and interact with a Cadence Verisium Debug product from
# Customer's Python program, subject to the following conditions:
#
# - Customer may not distribute, sell, or otherwise modify the Verisium Debug API package.
#
# - All copyright notices in this Software must be maintained on all included
#   Python libraries and packages used by Customer.

from verisium import *

# This script registers a callback to fire whenever signals are added to the waveform
# when this occurs, the script will modify the color of the added
# signal according to what type of port it is.

# set the color of a signal based on port type
def signal_color(i:Signal):
    if i.port is None:
        text_color = guicolor.GREEN
    elif i.port.direction == Direction.INPUT:
        text_color = GUIcolor(255, 165, 0)
    elif i.port.direction == Direction.OUTPUT:
        text_color = guicolor.YELLOW
    elif i.port.direction == Direction.INOUT:
        text_color = guicolor.MAGENTA
    else:
        text_color = guicolor.RED

    return text_color

# go through added waveform signals, find their rows and color them
def wv_add_callback(ev:ServerEvent):
    items = ev.objects
    for item in items:
        if isinstance(item, Signal):
            rows = wave.rows(ct.full_path==item.full_path)
            if rows is not None:
                try:
                    for r in rows:
                        r.text_color = signal_color(item)
                except Exception as e:
                    print ("error setting color for "+item.full_path)


# For Debug use only. allow this script to be run from an IDE or external Python (outside of embedded console)
if 'self' not in globals():
   server = VerisiumDebugServer(VerisiumDebugArgs(
            is_gui=True,
            is_launch_needed=True,
            db='<path to a db for testing>'
        ))
   server.add_callback(EventType.WAVEFORM_ADD, wv_add_callback)
   self=server
   wave = self.gui_components(ct.type == ComponentType.WAVEFORM)[0]
   while True:
        time.sleep(1)

# running via embedded console. Only code for main thread is to register the CB
self.add_callback(EventType.WAVEFORM_ADD, wv_add_callback)
wave = self.gui_components(ct.type == ComponentType.WAVEFORM)[0]

