import asyncio
import time



async def say_after(sec:int, msg:str):
    await asyncio.sleep(sec)
    print(msg)
    
    
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(
            say_after(1, 'hello'))

        task2 = tg.create_task(
            say_after(2, 'world'))

        print(f"started at {time.strftime('%X')}")

    # 当存在上下文管理器时 await 是隐式执行的。

    print(f"finished at {time.strftime('%X')}")
    
asyncio.run(main())