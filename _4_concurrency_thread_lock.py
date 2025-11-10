import time
import requests
from concurrent.futures import ThreadPoolExecutor
import threading

print("1. RLock ===========")


'''可重入锁， 允许一个线程多次获取锁而不阻塞， 所以rlock可以避免同一线程多次获取锁而产生死锁'''
# 递归函数：确保递归调用时锁的安全性。
# 锁嵌套：多层方法或函数调用中需要获取同一锁。
# 复杂同步逻辑：如与 Condition 结合使用的生产者 - 消费者模型。

from threading import Lock

lock = Lock()

def func1():
    with lock:
        print("In func1")
        func2()  # 调用 func2，需要再次获取锁

def func2():
    with lock:  # 使用 Lock 会导致死锁
        print("In func2")

# 以下调用会导致死锁， 使用RLock 不会死锁   
# func1()

print("2. threading.Semaphore 信号量, 限制同时访问资源的线程数量（计数锁）")


def worker(sem):
    with sem:
        time.sleep(0.2)


def test_semaphore(sem_num):
    semaphore1 = threading.Semaphore(sem_num)

    start = time.time()
    threads = [threading.Thread(target=worker, args=(semaphore1,)) for i in range(8)]
    for i in threads: i.start()
    for i in threads: i.join()
    print("semaphore %s, 8 threads, use time: %s sec." % (sem_num, time.time() - start))
 

test_semaphore(sem_num=2)
test_semaphore(sem_num=4)  # 4个信号量比两个信号量运行快一倍


print("3. condition 允许线程在某个条件不满足时等待，并在条件可能满足时被通知  =============")
from queue import Queue
from threading import Condition


class MessaageQueue:
    def __init__(self):
        self.msg_queue = Queue(maxsize=10)
        self.condition = Condition()
    
    def produce(self, item):
        with self.condition:
            while self.msg_queue.full():
                self.condition.wait()
            
            self.msg_queue.put(item)
            self.condition.notify_all()
    
    def consume(self, item):
        with self.condition:
            while self.msg_queue.empty():
                self.condition.wait()
          
            item = self.msg_queue.get()
            print("current thread: %s , item: %s" % (threading.current_thread().name, item))
            self.condition.notify_all()


message_queue = MessaageQueue()

def producer():
    for i in range(100):  
        message_queue.produce(i)


def consumer():
    for i in range(50): 
        time.sleep(0.1) 
        message_queue.consume(i)


produce_thread = threading.Thread(target=producer)
consume_thread = threading.Thread(target=consumer)
consume_thread2 = threading.Thread(target=consumer)
print(consume_thread.name)
print(consume_thread2.name)

produce_thread.start()
consume_thread.start()
consume_thread2.start()

produce_thread.join()
consume_thread.join()
consume_thread2.join()


print("4. Event 事件，通过标识位实现线程间通信，一个线程给另一个线程一个信号")
event = threading.Event()
def func1():
    print("func1, wait event from func2 ...")
    event.wait()
    print("func1, event got")


def func2():
    print("func2, wait to set event ...")
    time.sleep(1)
    print("func2, set event ...")
    event.set()


thread1 = threading.Thread(target=func1)
thread2 = threading.Thread(target=func2)
thread1.start()
thread2.start()
thread1.join()
thread2.join()


print("5. barrier 屏障， 设定多个线程都达到某一步才继续往下执行，并在此刻可以有回调函数")
# 多阶段并行计算
# 资源初始化同步
# 数据搜集与汇总

# 类似多个阶段的多线程计算

def worker(barrier, id):
    print(f"Thread {id} started phase 1")
    time.sleep(id)  # 模拟不同的计算时间
    barrier.wait()  # 等待所有线程完成阶段1
    
    print(f"Thread {id} started phase 2")
    time.sleep(id)  # 模拟不同的计算时间
    barrier.wait()  # 等待所有线程完成阶段2
    
    print(f"Thread {id} finished")

# 创建屏障，等待3个线程
barrier = threading.Barrier(3)

# 创建3个工作线程
threads = [threading.Thread(target=worker, args=(barrier, i)) for i in range(3)]

# 启动所有线程
for t in threads:
    t.start()

# 等待所有线程完成
for t in threads:
    t.join()
    
    
    
    
