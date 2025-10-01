import asyncio


'''
    协程, 轻量级线程，特别适合处理I/O密集型任务
    内存占用小，单线程可以运行数万个协程
'''


'''Python中协程的实现经历了三个阶段，现代代码推荐使用async/await语法'''

'''
    1.生成器实现（Python 2.5+） 
    通过yield暂停执行，send()恢复执行
'''

def coroutine_example():
    while True:
        x = yield  # 接收外部发送的值
        print("Received:", x)
 
co = coroutine_example()
next(co)  # 启动协程
co.send("Hello")  # 输出: Received: Hello

'''
    2. asyncio装饰器（Python 3.4）
        使用@asyncio.coroutine和yield from
'''

 
@asyncio.coroutine
def func1():
    print(1)
    yield from asyncio.sleep(3)  # 模拟I/O操作
    print(2)
 
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(func1()))
 

'''
    3. async/await语法（Python 3.5+，推荐）
    使用async def定义协程，await暂停执行：
'''

import asyncio
 
async def hello():
    print("Hello")
    await asyncio.sleep(1)  # 模拟I/O操作
    print("World")
 
asyncio.run(hello())  # Python 3.7+简化写法

'''
    await 后跟 Awaitable对象， 包括协程、Task、Future
'''


print("1. 创建任务 ===========")
async def some_task():
    await asyncio.sleep(0.1)


async def main():
    tasks = [asyncio.create_task(some_task) for i in range(4)]
    asyncio.gather(*tasks)   


asyncio.run(main())

print('2. 取消任务 ===========')
async def long_running_task():
    try:
        print("Task started")
        await asyncio.sleep(3600)  # 模拟长时间运行
    except asyncio.CancelledError:
        print("Task cancelled")
        raise

async def main():
    task = asyncio.create_task(long_running_task())
    await asyncio.sleep(1)
    
    # 取消任务
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        print("Main caught cancellation")

asyncio.run(main())


print("3. 协程队列")
async def worker(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Processing {item}")
        await asyncio.sleep(0.5)
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    
    # 启动worker
    worker_task = asyncio.create_task(worker(queue))
    
    # 添加工作项
    for i in range(10):
        await queue.put(i)
    
    # 等待队列处理完成
    await queue.join()
    
    # 停止worker
    await queue.put(None)
    await worker_task

asyncio.run(main())


print("4. 超时控制")
async def worker(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Processing {item}")
        await asyncio.sleep(0.5)
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    asyncio.shield()
    # 启动worker
    worker_task = asyncio.create_task(worker(queue))
    
    # 添加工作项
    for i in range(10):
        await queue.put(i)
    
    # 等待队列处理完成
    await queue.join()
    
    # 停止worker
    await queue.put(None)
    await worker_task

asyncio.run(main())


print("5. 完成回调")
async def background_task():
    await asyncio.sleep(1)
    return "Result"

def callback(future):
    print(f"Task completed with result: {future.result()}")

async def main():
    task = asyncio.create_task(background_task())
    task.add_done_callback(callback)
    await task

asyncio.run(main())


# 协程同步
# asyncio.Semaphore()
# asyncio.Lock()
# asyncio.Event()
# asyncio.Condition()
# asyncio.Barrier()
import numpy