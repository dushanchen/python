import multiprocessing
import multiprocessing.pool
import os 
import time


# from concurrent.futures import processPoolExecutor


def worker(name, delay):
    print(f"Process {name} (PID: {os.getpid()}) started")
    time.sleep(delay)
    print(f"Process {name} completed") 

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=worker, args=("Alpha", 2))
    p2 = multiprocessing.Process(target=worker, args=("Beta", 1))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print("All processes completed") 


print("1. 通过 Queue 传值")

def worker(num, queue):
    result = num * num  # 计算平方
    queue.put(result)   # 将结果放入队列
 
if __name__ == "__main__":
    numbers = [1, 2, 3, 4, 5]
    queue = multiprocessing.Queue()  # 创建队列
    processes = []
 
    for num in numbers:
        p = multiprocessing.Process(target=worker, args=(num, queue))
        processes.append(p)
        p.start()
 
    # 获取所有进程的返回值
    results = []
    for _ in range(len(numbers)):
        results.append(queue.get())  # 从队列中取出结果
 
    for p in processes:
        p.join()  # 等待所有进程结束
 
    print("Results:", results)  # 输出: [1, 4, 9, 16, 25]



print("2. Pipe 适合两个进程间直接通信")
def sender(conn, messages):
    for msg in messages:
        conn.send(msg)
        print(f"Sent: {msg}")
    conn.close()
 
def receiver(conn):
    while True:
        msg = conn.recv()
        if msg is None:  # 结束信号
            break
        print(f"Received: {msg}")
 
if __name__ == "__main__":
    parent_conn, child_conn = multiprocessing.Pipe()
    messages = ["Hello", "World", "Python", "Multiprocessing", None]
    sender_process = multiprocessing.Process(target=sender, args=(parent_conn, messages))
    receiver_process = multiprocessing.Process(target=receiver, args=(child_conn,))
    sender_process.start()
    receiver_process.start()
    sender_process.join()
    receiver_process.join()


print("3. 共享内存  Value 单个变量")
def worker1(n):
    n.value += 1
    print(f"worker1: {n.value}")

def worker2(n):
    n.value += 1
    print(f"worker2: {n.value}")

if __name__ == "__main__":
    n = multiprocessing.Value('i', 0)  # 整型共享变量
    p1 = multiprocessing.Process(target=worker1, args=(n,))
    p2 = multiprocessing.Process(target=worker2, args=(n,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


print("共享变量。Array 数组")
def worker1(n):
    n.value += 1
    print(f"worker1: {n.value}")

def worker2(n):
    n.value += 1
    print(f"worker2: {n.value}")

if __name__ == "__main__":
    n = multiprocessing.Value('i', 0)  # 整型共享变量
    p1 = multiprocessing.Process(target=worker1, args=(n,))
    p2 = multiprocessing.Process(target=worker2, args=(n,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


print("4. 多进程也可以通过 Lock，Semaphore，Event， Condition， Barrier 实现同步")


print("5. 进程池")
# multiprocessing.Pool 
# 同步调用
# pool.map(func, iterable)：批量提交任务，阻塞直到所有任务完成并返回结果列表。
# pool.apply(func, args)：提交单个任务，阻塞直到任务完成并返回结果

# 异步调用 
# pool.apply_async(func, args)：提交单个任务，立即返回 AsyncResult 对象（类似 Future）。
# pool.map_async(func, iterable)：批量提交任务，立即返回 AsyncResult 对象。
# pool.starmap_async() / pool.imap_async()：类似 map_async，但支持更灵活的参数传递。

print("异步调用，通过 Future 对象或回调函数获取结果，适合需要并行处理多个任务的场景")
# ProcessPoolExecutor内部使用multiprocessing.Process创建工作者进程
import concurrent.futures

def square(num):
    return num * num

if __name__ == "__main__":
    numbers = [1, 2, 3, 4, 5]
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # 提交所有任务，立即返回 Future 列表
        futures = [executor.submit(square, num) for num in numbers]
        
        # 手动获取结果（阻塞）
        results = [future.result() for future in futures]
        print("Future 结果:", results)  # 输出: [1, 4, 9, 16, 25]

        # 或者使用 as_completed 动态获取结果
        for future in concurrent.futures.as_completed(futures):
            print("动态获取结果:", future.result())