### 1. 原理
基于erlang语言开发、实现AMQP协议

producer -> broker(exchange -> queue) -> consumer

broker:
  - virtual host
    - queue
    - exchange 

exchange -(routing key)> queue

virtual host：
    用户资源隔离
channel：
    每个客户端连接可以有多个channel，以节省服务器资源，避免建立太多的tcp连接而造成资源浪费
exhange：
    name 名称
    type 类型
    
queue：
    存储消息，可以设置长度、消息超时时间
    Durability： Durable/ Transient (持久化、临时性)

业务端口5672，UI端口15672

#### 四种主要的交换机
Direct 精确匹配
    定向，由routing key 匹配队列
Fanout 广播
    广播，发送给绑定的所有队列
topic 
    通配符，发送给符合routing pattern的队列，路由模式
headers

交换机只具备转发能力，不能存储消息。如果没有绑定队列，那么消息会丢失。

#### 七种用法
helloworld：

working queue：
    默认交换机，一个队列，多个消费者竞争队列中的消息
pub/sub：
    fanout 交换机，广播到多个队列，监听同一个队列的消费者也是竞争关系
routing：
    direct 交换机， 交换机绑定队列，并指定routing key
topics：
    topic 交换机， routing key 使用通配符，#匹配零个或多个词、*匹配一个词
RPC：
    同步调用
Publisher Confirms：
    发送端消息确认

#### 其他功能
死信队列
    1）拒绝消费，消息被消费端拒绝消费，并不放入原队列
    2）队列溢出。队首溢出的消息进入死信队列
    3）消息超时
    处理方式：
    丢弃、入库、监听（消费端监听死信队列做处理）
    需要创建死信交换机并指定给正常的交换机，创建死信路由键、死信队列绑定死信交换机

事务消息：
    在客户端批量提交消息，具有原子性，可回滚。这是客户端的功能，并不是rabbitmq本身的功能
    在spring框架下用Transaction注解

惰性队列：
    允许存储大量的消息，在消息堆积时持久化到硬盘，需要被消费时再从硬盘加载。

优先队列：
    消息设置优先级。在消息发送后置处理器，指定消息优先级，数字越大越优先，优先级高的消息先进入队列

集群：
    haproxy 实现负载均衡

    仲裁队列：
        type: Quorum 
    
    流式队列：
        stream

### 2. 应用场景
应用解藕、流量削峰、异步任务

延迟队列：
    比如订单限时1个小时完成支付
    1）消息过期 + 死信队列
    2）安装插件 rabbitmq-delayed-message-exchange 最多延迟两天 
        交换机参数： type: x-delayed-message  arguments: x-delayed-type: direct





### 3. 有哪些坑
消息丢失
    1）消息没有发送到队列上
        生产端进行确认
            spring 配置：
                publisher-confirm-type: CORRELATED 交换机确认
                publisher-returns: true 队列确认
            创建配置类实现故障回调接口
        使用备份交换机
    2）消息队列宕机，消息没有持久化
        消息持久化到硬盘
    3）消费端出现问题，导致消息没有消费成功
        消费端消费成功返回ack信息，失败返回nack信息（可决定是否将消息重新放回队列，可判断是否uk j是重复投递的又消费失败，可以不再放回队列）
        deliveryTag：64位整数，交付标签机制，消息的唯一标识 

消息超时
    给消息设定过期时间，过期后删除，进入死信队列



### 4. 大厂主流方案

主流消息队列： 
kafka：分布式日志采集、大数据采集， 吞吐量非常大、性能非常好、技术生态完整； 功能单一
Rabbitmq：企业内部调用； 消息可靠性高、功能全面； 吞吐量较低、消息积压时会影响性能
rocketmq： 应用场景较多、比如金融； 高吞吐、高性能、高可用，高级功能非常全； 技术生态相对没那么完整

