import asyncio
import time
import threading


print("1. threading ---------------")
print("多线程并行： ")
def worker(index):
    for i in range(10):
        print("worker %s do %s time" % (index, i))
        time.sleep(0.1)


threads = []
for i in range(4):
    threads.append(threading.Thread(target=worker, args=(i,)))

for t in threads:
    t.start()    
for t in threads:
    t.join()


print("2. lock -------------")
print("GIL 能保证多个线程同步执行，但是无法保证共享资源的原子性访问")
print("累加、append()、字典更新，都是多条字节码的操作，执行过程中GIL可能切换线程")
counter = 0
thread_count = 4
increase_count = 10000
lock = threading.Lock()

def increase(with_lock):
    global counter
    for i in range(increase_count):
        if with_lock:
            with lock:
                counter += 1
        else:
            counter += 1   


def concurrency_increase(with_lock=False):
    start = time.time()
    threads = []
    for i in range(thread_count):
        thread = threading.Thread(target=increase, args=(with_lock,))
        threads.append(thread)
        thread.start()

    for i in threads:
        i.join()

    use_time = time.time() - start
    print("counter: %s, expect value: %s, use time: %s" % (counter, thread_count * increase_count, use_time))

print("无锁的情况累加：")
concurrency_increase(with_lock=False)
counter = 0
print("有锁的情况累加： ")
concurrency_increase(with_lock=True)

print("3. 线程池 -------------")
import requests
from concurrent.futures import ThreadPoolExecutor
num = 20 
urls = ["http://www.baidu.com"] * num
def fetch(url):
    return requests.get(url)
start = time.time()
with ThreadPoolExecutor(max_workers=5) as pool:
    result = list(pool.map(fetch, urls))
print("thread pool fetches %s urls, use %s sec." % (num, time.time() - start))

start = time.time()
for i in urls:
    resp = fetch(i)
print("synchronously fetch %s urls, use %s sec." % (num, time.time() - start))
print("多线程适合io密集场景")

print("4. 多进程 ---------- ")
# import multiprocessing
# counter = 0
# start = time.time()
# with multiprocessing.Pool(processes=4) as pool:
#     results = pool.map(increase, [True] * 4)
# print("use time: %s sec." % (time.time() - start))
# counter = 0
# start = time.time()
# with multiprocessing.Pool(processes=4) as pool:
#     results = pool.map(increase, [False] * 4)
# print("use time: %s sec." % (time.time() - start))

# 进程间通信，使用Queue， Pipe, Array


# I/O 密集型（少量任务）	线程（Threading）	      threading, requests
# I/O 密集型（大量任务）	异步（Asyncio）	          asyncio, aiohttp
# CPU 密集型	          进程（Multiprocessing）	multiprocessing

print("5. 异步io")
import aiohttp


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()
    

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        await asyncio.gather(*tasks)

start = time.time()
asyncio.run(main())
print('asyncio fetch %s urls, use time %s sec.' % (len(urls), time.time() - start))

start = time.time()
for i in urls:
    resp = requests.get(i)
print('requests fetch %s urls, use time %s sec.' % (len(urls), time.time() - start))