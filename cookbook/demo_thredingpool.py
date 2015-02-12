# -*- coding: UTF-8 -*-

'''
Last modified time: 2015-02-05 19:09:51
Edit time: 2015-02-05 19:10:37
File name: demo_thredingpool.py
Edit by caimaoy
'''

__author__ = 'caimaoy'

import threading
import Queue
import time
import sys

Qin = Queue.Queue()
Qout = Queue.Queue()
Qerr = Queue.Queue()
Pool = []
threading_local = threading.local()


def report_error():
    Qerr.put(sys.exc_info()[:2])


def get_all_from_queue(Q):
    try:
        while True:
            yield Q.get_nowait()
    except Queue.Empty:
        raise StopIteration

'''
def do_work_from_queue():
    threading_local.busy = False
    def is_done():
        ret = False
        if Qin.empty():
            for i in Pool:

    while True:
        if threading_local.busy is True:
            pass
        else:
            threading_local.busy == True
            command, item = Qin.get()
            if command == 'stop':
                break
            try:
                # time.sleep(0.1)
                if command == 'process':
                    result = 'new' + item
                    request_work(result)
                else:
                    raise ValueError, 'Unknown command %r' % command
            except Exception, e:
                report_error()
            else:
                Qout.put(result)
            threading_local.busy == False
'''

def make_and_start_thread_pool(number_of_thrads_in_pool=5, daemons=False):
    for i in range(number_of_thrads_in_pool):
        '''
        new_thread = threading.Thread(target=do_work_from_queue)
        print 'active_count is', threading.active_count()
        print 'current_thread is', threading.current_thread()
        print 'enumerate is', threading.enumerate()
        new_thread.setDaemon(daemons)
        Pool.append(new_thread)
        new_thread.start()
        '''
        print i
        new_thread = myTread(i)
        Pool.append(new_thread)
        new_thread.start()


lock = threading.Lock()
print_lock = threading.Lock()

class myTread(threading.Thread):
    def __init__(self, name):
        super(myTread, self).__init__()
        self.isbusy = False
        self.a = 3
        self.setName(name)

    def run(self):
        while True:
            if self.isbusy is True:
                'I am busy'
                pass
            else:
                lock.acquire()
                finished = False
                if Qin.empty() is True:
                    # print 'Qin.empty() is ', Qin.empty()
                    set_isbusy = set([i.isbusy for i in Pool])
                    if True in set_isbusy:
                        '''
                        for i in Pool:
                            print 'someone is busy'
                            print 'i am ', self.getName()
                            print i.getName(), 'isbusy', i.isbusy
                            # time.sleep(10)
                        '''
                        lock.release()
                        continue
                    else:
                        finished = True
                if finished is True:
                    lock.release()
                    break
                self.isbusy = True
                command, item = Qin.get_nowait()
                lock.release()
                time.sleep(1)
                if command == 'stop':
                    break
                try:
                    time.sleep(1)
                    if command == 'process':
                        result = 'new' + item
                        print_lock.acquire()
                        print result
                        print_lock.release()
                        if self.a:
                            request_work(result)
                            self.a -= 1
                    else:
                        raise ValueError, 'Unknown command %r' % command
                except Exception, e:
                    report_error()
                else:
                    Qout.put(result)
                self.isbusy = False


def request_work(data, command='process'):
    Qin.put((command, data))

def get_result():
    return Qout.get()

def show_all_results():
    for result in get_all_from_queue(Qout):
        print 'Result:', result

def show_all_errors():
    for etyp, err in get_all_from_queue(Qerr):
        print 'Error:', etyp, err

def stop_and_free_thread_pool():
    for i in range(len(Pool)):
        request_work(None, 'stop')

    for existring_thread in Pool:
        existring_thread.join()

    del Pool[:]

def is_any_thread_alive():
    for i in Pool:
        print 'alive_count is ', i.alive_count()
        if i.is_alive():
            print 'alive_count is ', i.alive_count()
            return True
    return False

def main():
    for i in range(3):
        request_work(str(i))

    make_and_start_thread_pool()
    # stop_and_free_thread_pool()
    show_all_results()
    show_all_errors()

    # import pdb; pdb.set_trace()

    '''
    while not Qin.empty(): # and not is_any_thread_alive():
        # import pdb; pdb.set_trace()
        print 'Qin is not empty'
        make_and_start_thread_pool()
        stop_and_free_thread_pool()
    '''


if __name__ == '__main__':
    main()
