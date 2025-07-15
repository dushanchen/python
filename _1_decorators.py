import time


print("# 1. 装饰器  计算方法执行时间")


def decorator(func):
    def _decorator():
        start = time.time()
        func()
        print("func used ", time.time() - start)
    return _decorator


@decorator
def some_func():
    time.sleep(1)
    pass


some_func()


print("# 2. 闭包 利用闭包缓存斐波那契")


def fib():
    cache = {}

    def _fib(n):
        if n in cache:
            print("visit cache: ", n)
            return cache[n]
        else:
            value = n if n < 2 else n + _fib(n - 1)
            cache[n] = value
            return value

    return _fib


compute_fib = fib()
print(compute_fib(5))
print(compute_fib(6))
print(compute_fib(10))

# 生成器核心优势总结
#
# 场景	    传统方法问题	生成器解决方案
# 大文件处理	内存不足	    逐行流式处理
# 无限序列	无法预先生	按需生成
# 数据管道	中间结果存储	链式惰性计算
# 状态管理	需类封装	    用yield保存状态
# 内存优化	列表占用高	生成器表达式

print("# 3. 生成器 yield。 惰性计算，借助yield可以自定义迭代逻辑，使代码更加简洁")


def generator(n):
    while True:
        if n < 0:
            break
        if n % 3 == 0:
            yield "haha"
        else:
            yield n
        n -= 1


for i in generator(10):
    print(i)


print("偏函数：functools.partial, 可以固定一个函数的参数，命名为一个新的函数。跟lambda差不多")

print("高阶函数： map, filter, reduce, sorted, zip, iter, lru_cache 缓存计算值, wraps 保留被装饰函数的元信息")

