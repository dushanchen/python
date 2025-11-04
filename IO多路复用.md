## IO多路复用
    用一个进程（或少量线程）来同时监视和管理大量的网络连接，只有当连接真正准备好进行I/O操作时，才去处理它，从而最大限度地利用CPU资源，实现高并发。

### 1. select
    io多路复用最初的实现，基于轮询机制。
    性能较差：每次都要在内核空间和用户空间拷贝和遍历
    数量有限：只支持1024个描述符

### 2. poll
    在select基础上，突破数量限制；还是轮询机制

### 3. epoll
    真正实现了事件驱动
    Linux 下性能最高、最主流的IO多路复用实现。

### 4. io_uring
    是 Linux 内核 5.1+ 引入的新一代异步 I/O 接口。性能潜力理论上超过 epoll/libuv
    在Python领域，io_uring 的应用目前主要处于探索和概念验证阶段（KLoop）


## python asyncio
    基于事件循环，在底层维护两个队列：就绪队列、等待队列
    在 用户态 进行高效的上下文切换，以 单线程 处理海量 I/O 并发

    系统层面：
        在 Linux 上，它默认使用 epoll，旧版本系统可能自动选择。
        在 macOS/BSD 上，它使用 kqueue（与 epoll 类似的高性能多路复用器）。
        在 Windows 上，它使用 select（或者效率更高的 IOCP）

### uvloop
    更高效的事件循环模块，可以替代asyncio默认的事件循环，性能提升2-3倍。
    不是纯python实现，用 Cython 编写，基于第三方的C库libuv。

    import asyncio
    import uvloop

    if __name__ == "__main__":
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        asyncio.run(main())  # 启动你的主异步函数

### trio

