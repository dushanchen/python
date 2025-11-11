def coroutine_example():
    while True:
        x = yield  # 接收外部发送的值
        print("Received:", x)
        return 'world'
    
    
co = coroutine_example()
next(co)  # 启动协程
next(co)  # 启动协程
# co.send("Hello")  # 输出: Received: Hello
# co.send()  # 输出: Received: Hello
