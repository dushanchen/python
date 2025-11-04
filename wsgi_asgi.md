## WSGI/ASGI 应用服务器
    承载web应用代码，提供并发服务

### WSGI

    定位：Python Web 同步规范。它定义了同步 Python Web 应用与服务器之间的简单调用接口。
    支持框架：Django (主要), Flask, Bottle 等。
    局限：它是为同步世界设计的，无法原生支持 WebSockets 或 HTTP/2 等长连接。

#### Gunicorn
    定位：一个用 Python 编写的 WSGI 服务器。简单、轻量、高效，是部署 WSGI 应用（如 Django, Flask）的事实标准。
    工作模式：它使用一种 “主-从”模型。一个主进程管理多个工作进程。工作进程可以是同步的，也可以是异步的。
    特点：配置简单，与各种 Web 框架兼容性极好。

#### uWSGI
    定位：一个功能极其丰富的 WSGI 服务器，用 C 语言编写。为部署高性能的 Python Web 应用提供一个完整的解决方案。
    特点：
        高性能：由于用 C 编写，通常比 Gunicorn 性能更高。
        高复杂度：配置项非常多，学习曲线陡峭。
        协议支持：除了 HTTP，它还支持自己的 uwsgi 二进制协议，常与 Nginx 紧密配合。
    
#### Waitress
    定位：一个纯 Python 编写的、与平台无关的 WSGI 服务器。在 Windows 平台上表现良好。
    特点：非常稳定、兼容性好，以“只需工作”为设计目标。 
    使用场景：适合中小型应用，或者在 Windows 上进行开发和测试。

#### mod_wsgi
    Apache HTTP Server的一个模块。将Python应用嵌入Apache进程。

#### Bjoern
    C语言编写，极其快速、轻量。一个非常专注于性能的WSGI服务器。
    

### ASGI

    定位：Python Web 异步规范。它是 WSGI 的精神继承者，支持异步、长连接和更复杂的协议。
    支持框架：FastAPI, Starlette, Quart（支持ASGI的Flask）, Django (3.0+ 异步视图)。

#### Uvicorn
    闪电般的速度，基于uvloop和httptools。是FastAPI的推荐服务器。

#### Hypercorn
    受Gunicorn启发，功能丰富。支持HTTP/2、ASGI/WSGI。与Quart框架同源。

#### Daphne
    最初为Django Channels开发，是官方推荐的ASGI服务器。主要用于需要WebSocket或后台任务的Django项目。

#### uvicorn-workers
    它不是独立服务器，而是让Gunicorn管理Uvicorn Worker的插件。
    生产环境部署ASGI应用的黄金组合：利用Gunicorn的进程管理 + Uvicorn的异步性能。

## gevent & eventlet
    都是基于协程的并发库，通过“猴子补丁”来实现异步I/O。
    1）在python的同步代码块中打开猴子补丁，改动少量代码，变同步为异步
    monkey.patch_all() 是魔法的源泉。
    gevent.spawn() 用于创建一个协程（绿色线程）。
    gevent.joinall() 用于等待所有协程完成。

    2）在 Gunicorn 中作为 Worker 使用
    不需要修改 Django/Flask 代码，只需要在启动命令中指定 worker 类型。
    
    ···bash···
    # 使用 gevent worker，并发处理请求
    gunicorn -k gevent -w 4 myapp:app
    # 或者，如果你想处理更多并发连接，可以指定worker连接数
    gunicorn -k gevent -w 4 --worker-connections 1000 myapp:app

## 总结与经典部署方案

## 部署同步应用（Django, Flask）

    经典组合：Nginx + Gunicorn

        Nginx：作为反向代理和静态文件服务器。

        Gunicorn：作为应用服务器，使用 gevent worker 来处理高并发。

    高性能组合：Nginx + uWSGI

### 部署纯异步应用（FastAPI, Starlette）

    简单组合：Nginx + Uvicorn

    生产环境组合：Nginx + Gunicorn + Uvicorn Worker

        Gunicorn 作为进程管理器，提供更完善的重启、日志、配置管理。

        Uvicorn Worker 作为实际运行异步代码的工人。