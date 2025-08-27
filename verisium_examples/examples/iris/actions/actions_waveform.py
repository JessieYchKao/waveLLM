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

'''Action Waveform'''

from actionslib.base_actions import *
from actionslib.lib import print_progress

class ActionWaveform(BaseAction):
	##### Perform Actions (this is specific for each all actions.py)
    def current_action(self):
        # Our example action is to add signals to waveform
        # Get full paths to be added

        full_paths = self.get_keys_from_objects_dict('signal', 'sendToWave')
        # Send to wave
        wf = self.indago_server.gui_components(ct.type == ComponentType.WAVEFORM)[0]
        wf.maximize()
        for i, f in enumerate(full_paths):
            signal = self.indago_server.signal_by_full_path(f)
            if signal is None:
                print(f"Signal not found: {f}")
                continue
            wf.add(signal)
            print_progress('Processed add', i)

        args_list = []
        for _ in range(self.test_count // 3):
            args_list.append(ZoomDirection.IN)
            args_list.append(ZoomDirection.OUT)
            args_list.append(ZoomDirection.FULL)

        for i, args in enumerate(args_list):
            wf.zoom(args)
            print_progress('Processed zoom', i)

        time_points = [TimePoint(i * wf.end_time.time / (self.test_count - 1), wf.end_time.units) for i in range(self.test_count)]
        wf.zoom(ZoomDirection.IN)
        wf.zoom(ZoomDirection.IN)
        for i, time_point in enumerate(time_points):
            wf.scroll_to(time_point)
            print_progress('Processed scroll', i)


action = ActionWaveform('This file is focused on measuring performance of different waveform operations.')
action.add_required_object('sendToWave', 'signal', action.test_count, action.no_constraint)
action.execute_action()
