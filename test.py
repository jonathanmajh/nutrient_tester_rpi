from misc import QueueMessage
import sys
import time

def test_main(queue):
    try:
        queue.put(QueueMessage('Starting Tests'))
        queue.put(QueueMessage('Sleeping 5 seconds'))
        time.sleep(5)
        queue.put(QueueMessage('Raising Exception'))
        raise Exception()
        queue.put(QueueMessage('', 0))
    except:
        queue.put(QueueMessage('Unexpected Exception', 4, sys.exc_info()))