'''
    面向对象编程
'''

print("1. metaclass 元类，创建类的类， 在定义类的时候动态定义类的行为")

print("===== type 动态创建类 =====")
Sample = type("Sample", (), {"attr_x": 1})
print(Sample().attr_x)

'''继承type，实现元类'''
class Meta(type):
    def __new__(cls, name, bases, attrs):
        attrs['x'] = 1
        return super().__new__(cls, name, bases, attrs)
    

class MyClass(metaclass=Meta):
    pass


print(MyClass.x)

print("==== 使用元类实现单例模式 =====")

class SingletonMeta(type):
    __singletonDict = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls.__singletonDict:
            cls.__singletonDict[cls] = super().__call__(*args, **kwargs)
        return cls.__singletonDict[cls]
    

class MySingleton(metaclass=SingletonMeta):
    pass


single1 = MySingleton()
single2 = MySingleton()
print(single1 is single2)


print("2. 描述符 __get__, __set__, __delete__  属性校验 =========")

print("3. 抽象基类 ABC，用于规范接口设计 =========")
# 子类必须实现基类的方法，来达到规范的目的
# 模版方法模式

print("4. 魔术方法 __init__, __new__, __str__, __repr__, __len__, __getitem__, __setitem__, __contains__")

 