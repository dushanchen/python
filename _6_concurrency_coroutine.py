import asyncio


'''
    协程, 轻量级线程，可以在函数间自由切换运行。
    跟线程的区别：线程切换是由系统调度，涉及到内核态到用户态的转换，开销大，MB级别，携程切换可以由程序员调度，由于共用一个线程，切换开销小，KB级别。
    特别适合处理I/O密集型任务
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


print("6. 调用阻塞io")
import requests

loop = asyncio.get_event_loop()
url = 'www.baidu.com'
async def run_blocking_io():
    # 使用 run_in_executor 默认线程池来运行一个阻塞操作
    resp = await loop.run_in_executor(None, requests.get, url)
    print(resp)

loop.close()

print("7. 异步迭代器")
# 实现__aiter__方法

print("8. 异步上下文管理器")
# 实现 __aenter__、__aexit__方法

print("9. uvloop")
# 使用uvloop 替用asyncio 默认的循环； uvicorn内部使用的就是uvloop
    
# 协程同步
# asyncio.Semaphore()
# asyncio.Lock()
# asyncio.Event()
# asyncio.Condition()
# asyncio.Barrier()

# 10. 使用numpy、pands等同步类库
# 1）绝不直接在 async def 视图中调用同步阻塞函数。
# 2）使用 asyncio.to_thread (Python 3.9+) 或 loop.run_in_executor（3.7、3.8） 将同步代码包装起来。
# 3）将所有相关的同步操作打包到一个函数中，然后一次性提交到线程池，以减少线程切换的开销。
# 4）对于重度使用场景，考虑创建自定义线程池以控制并发度和资源消耗。