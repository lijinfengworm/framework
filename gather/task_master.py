#!/usr/bin/env python
# -*- coding:'utf8' -*-

from baseQueue import QueueManagerServer
from multiprocessing import Queue

task_queue = Queue()
result_queue = Queue()

Server = QueueManagerServer(task_queue, result_queue)

manager = Server(address=('', 5000), authkey=b'secret')

manager.start()
manager.join()