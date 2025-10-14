### 基于内存的key-value数据库

### redis 命令参考： http://doc.redisfans.com

### redis.conf
daemonize yes  // 后台启动
protected-mode no // 关闭保护模式。允许外部主机客户端连接
bind 127.0.0.1 注释
requirepass  // 设置访问密码 

### redis-cli
启动server， redis-server .redis.conf
启动client， redis-cli -a $pwd -p 6379
关闭server， redis-cli -a $pwd shutdown -p xxx
中文支持 --raw

### commands
keys * 
type $key
exist $key
del $key
unlink $key  # 非阻塞删除
ttl $key  # 查看过期剩余时间
expire $key # 设置过期时间
select dbindex
dbsize # 查看当前库的key数量
flushdb # 清空当前库
flushall # 清空所有库

#### 字符串
最大512MB
set key value [NX 不存在才创建|XX 覆盖原值] [GET 先获取原值] [EX 过期时间秒| PX过期时间毫秒] [exat unix时间戳] [KEEPTTL 不修改之前的过期时间]

mset k1 v1 k2 v2...
mget k1 k2
getrange k1 $start $end  # 截取字符串
setrange k1 $start $end   # 替换字符串
incr k1 # 数值加一
decr k1。# 数值减一
decrby k1 $value  # 减去指定数值
append k1 xxxx  # 追加字符串

#### list
底层是一个双端链表结构， 2^32 - 1个元素
lpush k1 1 2 3 4 5..
rpush k1 5 3 5 6 7..
lrange $start $end 
lpop  rpop
lindex k1 $index  # 获取指定下标的元素
llen #获取长度
lrem k1 $value $number # 删除指定个数的某数
ltrim k1 $start $end #删除
rpoplpush k1 k2 # 
lset k1 $index $value 
linsert k1 before $value #value1 # 插入

#### hash
hset key  k1 v1 k2 v2 .
hset
hdel
hmset
hmget
hgetall 
hkeys / hvalue  k1
hincrby # 字段增加值
hincrbyfloat

#### set
sadd k1 $value
smembers k1  获取全部
sismember k1 $value 是否存在
srem 删除某个元素
scard  获取总个数
spop。随机弹出元素
srandmember 随机取一个
smove  k1  k2  $value 从一个set移动到另一个set
-- 集合运算
sdiff k1 k2  # k1 - k2
sunion k1 k2  # 并集
sinter k1 k2   # 交集
sintercard 

#### zset
zset k1 score1 v1 score2 v2 ...
zrange k1 0 -1  [withscores]

#### bitmap
基于string类型实现，支持最大位数2^32位
setbit key offset 0/1
getbit key offset
strlen key  返回字节数
bitcount key 0
bitop and k1 k2 

#### heyperlog

#### stream
消息队列
xadd streamName * k1 v1 k2 v2 k3 v3. # 自动生成消息id，时间戳+自增id，保证唯一且比之前的大
xrange streamName - +
xtrim streamName maxlen 2
xtrim streamName minid xxx
xread 
xgroup create streamName groupName  $/0 # 从尾部/头部开始消费
xreadgroup group groupName consumerName 
xack 读取后发送确认消息
xpending # 查询还未确认的记录

#### bitfield
set fieldkey k1
bitfield k1 get i8 0
bitfield kq set i8 8 120
bitfield kq incrby u4 2 1.   

### 持久化
#### rdb
redis的默认持久化方式
redis.conf   set seconds changes. # 时间间隔、修改次数
save(阻塞主任务) / bgsave 手动触发
lastsave 获取上次快照时间
shutdown、flushdb、flushall 会自动生成快照，flush类操作生成的空rdb文件
利于备份和快速恢复大规模数据，但是数据量太大时rdb备份会比较消耗性能
redis.conf:
    save "" # 禁用rdb, 或执行命令 config set save ""
    stop-writes-on-bgsave-error yes # 快照写入失败时，不接受写入请求
    rdbcompression yes # rdb 采用LZF算法压缩存储
    rdbchecksum yes # 存储快照后，使用crc64进行数据校验，会增加性能消耗
    rdb-del-sync-files no  # 没有配置持久化，是否删除主从复制的rdb文件

优点：生成文件是二进制压缩格式，体积小，便于传输和备份、数据恢复速度快、适合全量备份
缺点：可能丢失两次快照之间的数据，由于bgsave是fork的子进程做快照，如果数据量特别大，可能影响主进程

#### aof
记录写操作，默认不开启aof
redis.conf:
    appendonly yes  # 输出appendonly.aof 文件
    # 写回策略 
    appendfsync always/everysec/no
        # always 同步写回，可靠性高、数据基本不丢失、但性能消耗较大
        # everysec 先放缓冲区，每秒写回，性能适中，宕机时丢失1秒内的数据
        # no 放缓冲区，由操作系统控制写回，宕机时丢失数据较多
    # aof重写机制：
    auto-aof-rewrite-percentage 100%
    auto-aof-rewrite-min-size 100MB

redis 7功能 -> multi-part aof , base, incr,manifest
 
重写aof: 
    重写命令：bgrewriteaof
    原理：遍历数据库中所有key，并生成全量命令写入一个临时aof文件，最后替换旧的aof文件，再将缓冲区的增量命令追加到新文件后面

aof、rdb同时开启，aof优先级高于rdb

优点：数据可靠性高，最多丢失一秒的数据，always策略可以不丢失数据；文件内容是文本格式，便于排查问题，可以修改错误命令。
缺点：生产的日志文件较大，但是可以通过重写机制缩小文件；数据恢复速度较慢，10GB可能要几分钟

#### RDB 和 AOF 混合持久化
redis 4.0 引入混合持久化模式，是主流的生产环境选择
redis.conf:
    appendonly yes
    aof-use-rdb-preamble yes

原理：在重写aof流程上作修改，先将当前数据集以rdb格式写入文件头部，再将缓冲区的增量命令以aof的格式追加到尾部，
    形成一个两段式的结构.文件内容以REDIS打头，表示rdb的部分。
恢复过程：对于混合持久化文件，Redis会先加载RDB部分快速恢复基础数据，然后重放AOF尾部的增量命令，将数据恢复到最新状态

优点：兼得了rdb和aof的优势，文件体积小、数据安全性高、恢复速度快

阿里 tair，rdb 优化，企业版功能 tair-binlog，支持恢复到指定秒级时间点
百度 混合持久化，aof中内置时间戳，可恢复到指定秒级 

### 错误恢复
./redis-check-aof --fix xxx.aof   # 修复aof
./redis-check-rdb

### redis事务
指定的多个操作连续独占的执行
不保证原子性，没法回滚
multi 开启事务，命令存入队列
exec / discard  执行事务、放弃事务
watch 乐观锁实现，如果监控的key在其他事务被修改，当前事务会被放弃
unwatch

### redis管道
多条命令逐一执行，会多次网络io（RTT），数据从用户态转移到内核态的时间也是多次，所以性能消耗较大
管道支持将多条不同数据类型操作的命令进行批量处理，一次RTT
cat cmd.txt | redis-cli -a 111111 --pipe
没有原子性，

### redis发布订阅

redis事务、redis aof机制、redis发布订阅
不推荐用

### redis复制 replica
#### 主从:  
slave -> master <- slave
主节点的数据复制到从节点，主节点负责写操作，从节点负责读操作，实现数据冗余和负载均衡。

##### 配置文件指定
从机上配置，redis.conf
    masterauth $password
    replicaof xxx.xxx.xxx.xxx 6379
主机配置    
    deamonize yes 
    # bind 127.0.0.1
    protected-mode no
    port 6379
    logfile /xxx/xxx
    requirepass $password
    dbfile dump6379.rdb
先启动主，再启动从
主机redis-cli， info replication
从机只能读不能写
主机宕机，从机依然是从，不会变化
主机恢复后，主从复制功能恢复
从机宕机后恢复，主从复制功能恢复

##### 手动指定
不需配置，在cli执行 slaveof xxx.xxx.xxx.xxx 6379
重启server后失效

##### 主从同步逻辑
第一次同步：
    slave -> master 发送sync请求，
    master 执行rdb持久化
    master -> slaves 将rdb快照同步到slave
    slave 清空数据，加载rdb
    master 发送repl——baklog中的增量命令到slave
    slave 执行增量命令
    心跳通信
    slave下线
增量同步，或网络中断后：
    slave 恢复上线后，master检查backlog里的offset，将offset后面的数据同步复制给slave

##### 缺点
master 宕机后，slaves无法自动选主，需要手动切换
从节点复制会比较消耗主节点性能，单主机主节点，写能力和存储能力比较受限

##### 一主多从模式

##### 薪火相传模式
master <- slave <- slave

##### 独立门户模式
slaveof no one 

### 哨兵 sentinel
结合主从复制模式
    1.监控redis运行状态，检测master是否故障
    2.消息通知
    3.故障转移
    4.配置

sentinel.conf
    sentinel monitor $master-name $ip $port $quorum.   // quorum 确认客观下线的最少哨兵数量
    sentinel auth-pass $master-name $password
    sentinel down-after-milliseconds $master-name $milliseconds  
    sentinel parallel-syncs $master-name $nums 

启动 
    redis-sentinel  ./sentinel.conf

模拟故障，一主二从，主故障
    master shutdown
    sentinel 使用raft算法，选出leader
    sentinel leader 选举新的 master，其中一个从变成主
    sentinel leader 对新 master 执行 slaveof no one
    原主恢复，降级为slave. conf配置会被修改，增加 slaveof 等参数
    整个过程可能需要10秒或者更多
    客户端通过哨兵获取当前主节点的地址

sdown 主观下线，哨兵与master心跳超时 
odown 客观下线，达到指定数量的哨兵认为master sdown
重新选主的规则：
    比较 priority -> replication offset -> run id(选小者)  （redis.conf slave-priority)

### redis 集群
通过数据分区和故障转移实现高可用和分布式存储，突破单机内存限制，节点间通过Gossip协议通信。可以有多个master，比如三主三从。
使用哈希槽，有16384个哈希槽，通过哈希值取余来决定放到哪个节点哪个槽位
分片 crc16算法

1. 哈希取余
    不利于扩容
2. 一致性哈希算法
    容易造成数据倾斜
3. 哈希槽
    crc算法计算出key的哈希值，再对15384取余，再分配到指定的redis节点
    扩容，从已有节点匀一部分槽和对应数据给新节点

故障:
    主节点故障时，对应的从节点自动升主，原主节点恢复后，降级为从节点，执行cluster nodes 可以恢复为主。
    如果一对主从都挂了，默认不再提供服务，通过参数配置 cluster-require-all-corverage 默认配置为yes

扩容：
    新增节点  redis-cli --cluster add-node
    槽位分配  redis-cli --cluster reshard
    检查集群  redis-cli --cluster check
    添加从节点 redis-cli --cluster add-node xxx cluster-slave master-id xxxx

缩容：
    找到从节点id redis-cli --cluster check
    删除从机  redis-cli --cluster del-node xxxx:xxx xxxxx
    检查集群  redis-cli --cluster check
    槽位分配  redis-cli --cluster reshard 输入全部slots数量，输入接受槽位的节点id
    删除主机  redis-cli --cluster del-node xxxx:xxx xxxxx
    检查集群  redis-cli --cluster check

不在同一个槽位的key，无法使用mget，可以使用通识占位符，让多个key定位到同一个槽位
检查槽位的key数量： cluster countkeysinslot $slotid
查看key该分配到哪个槽位： cluster keyslot $keyname

### springboot redis
jedis -> 优化 -> lettuce
sprintboot RedisTemplate

### 高级
6.0.x 及 7.0 之后使用多线程处理网络io 和 后台删除数据业务、aof重新、快照生成等，数据读写命令执行还是单线程
redis.conf
    io-threads 4
    io-threads-do-reads no
之前为啥使用单线程：
    redis的性能瓶颈不在cpu，而在内存

为啥要使用多线程删除数据：
    如果key的值比较大，删除时阻塞主线程，降低服务性能（删除大key用unlink）
    flushdb也有可能阻塞主线程

1. 大批量写入
    先把命令写入到一个文本，再使用redis管道批量写入
2. 生产上禁止 keys *、 flushdb 等操作, 通过配置文件禁用
    在百万级、千万级key的情况，可能阻塞几秒到几十秒不等，对业务产生较大影响
    redis.conf 
        rename-command keys ""
        rename-command flushdb ""
        rename-command flushall ""
    使用scan查询 ？
3. 大key
    认定标准：
        string > 10kB
        hash、list、set、zset > 5000 个 或10MB
    造成影响：
        造成内存不均、集群迁移困难； 删除超时； 网络流量阻塞
        执行get、hgetall、lrange 等操作时，比较耗时，可能长时间阻塞后续的命令执行，会一次性返回全部数据，容易内存溢出，或者占用大量网络带宽，影响其他业务请求
        在集群模式下，扩容缩容可能会迁移大key超时而失败，或者使用bgrewriteaof、bgsave 时超时
        过期删除时，也可能阻塞主线程
    发现大key： 
        redis-cli --bigkeys  -i 0.1 //找出每种数据类型最大的key， -i 每扫描100个key就休眠0.1秒 ，可以在从节点或者业务低峰执行  
        memoray usage $key // 计算指定key占用的内存
        使用scan命令遍历所有的key， 再用strlen、hlen、llen、scard、zcard等命令判断大小，可以用python脚本完成：
        使用redis-rdb-tools，可以离线分析rdb文件，生产内存报告，精确列出每个key的大小
    删除大key，渐进删除：
        string  用unlink 删除
        hash 使用 hscan 每次获取少量字段，渐进删除
        list 使用 ltrim 渐进删除
        set 使用sscan 扫描部分元素，在用srem删除
        zset 使用zscan 获取部分元素，再使用zremrangebyrank删除
    调优：
        redis.conf 
            lazyfree-layzy-server-del yes
            replica-lazy-flush yes
            lazyfree-lazy-user-del yes
    预防：
        1.增加监控，对redis实例的内存、key数量、慢查询等进行监控噶举
        2.指定规范， 在开发层面制定 Redis 使用规范，明确禁止存储 Bigkey，规定 Value 的大小和元素数量的上限。
        3.代码审查： 在代码提交阶段，对 Redis 的操作进行审查，提前避免产生 Bigkey 的逻辑。
        4.使用替代方案： 对于真的需要存储非常大 value 的场景（如文章内容、图片二进制），考虑是否可以使用其他数据库（如 MongoDB、S3）与 Redis 配合，Redis 中只存储其元数据或地址。
    
### 双写一致

数据更新：
    延时双删： 更新操作，先删缓存，再更新数据库，在延时异步删除缓存
    先更新数据库，在删除缓存

mysql - canel - redis

my.ini 
    [mysqld]
    log-bin=mysql-bin  # 开启binlog
    binlog-format=ROW  # 选择row模式
    server_id=1   # 配置mysql replication需要定义
mysql中新建canel用户并授权

canel 配置mysql链接参数、监听指定数据库表

自己实现写入redis逻辑，自定义canel监听哪些数据库表


### bitmap/hyperloglog/GEO

UV unique viewer
PV page viewer
DAU daily active user
MAU monthly active user

#### hyperloglog ip去重统计。12KB 统计 2^64个数据（亿级），误差在0.81%以内， 不记录数据本身。
适用场景：
    网站 UV 统计
    大规模日志分析中的独立事件计数
    数据库查询中不同值的近似计数
    任何需要海量数据去重计数且对精度要求不极致的场景

#### GEO
记录地理坐标，做范围查询
采用GEOHash算法，采用zset的逻辑存储查询坐标
GEOHash算法，讲经纬度二维坐标转化为一维数字，作为score存入zset，将地球表面按照先经度后维度的顺序递归划分，左边为0，右边为1
高纬度为0，低纬度为1，总共使用52位数将地球表面划分为无数个小方块（非严格矩形），左边可以解析到这些格子里，误差在亚米级
    范围查询逻辑：
    1. 根据输入的坐标和范围半径，计算出精度位数，Geohash前缀，即多大的格子能覆盖这个范围半径
    2. 计算九宫格。上一步找到的前缀，计算出地理位置上的经纬度范围，即一个四边形，再找出这个四边形周围的八个同精度的四边形
    3. 将上一步获取到的九个Geohash前缀，转化成9个分数区间，拿到zset里面去找出候选集
    4. 把所有候选集，逐一与用户输入的中心点计算球面距离，保留半径以内的点，得到精确结果集
边界点问题：是用九宫格方式可以解决
高纬度问题：获取到的九宫格是多个格子组成，可能不止九个，这就避免了高纬度时格子变窄导致无法覆盖要求的半径范围

#### bitmap
适合存储二值型数据， 比如签到记录


### 布隆过滤器
由一个很长的bit数组和多个无偏hash函数组成， 可以通过公式计算出初始位数（通过总的元素个数和误判率），如果实际元素数量超过了初始计划值，则需要重建布隆过滤器，重启把元素加入
添加元素时，通过多个hash计算，将结果投射到某个比特位，置为1
高效的查询一个元素是否在一个集合中，存在不一定存在，不存在则肯定不存在。

场景：
    1. 解决缓存穿透
    2. 黑名单、白名单

高效插入和查询，内存占用少
不存储数据本身

#### 布谷鸟过滤器

### 缓存预热、缓存雪崩、缓存击穿、缓存穿透
#### 缓存预热

#### 缓存雪崩
redis服务器宕机
redis中大量的key同时过期

主从+哨兵
集群模式
key的过期时间错开
加本地缓存 ehcache
服务降级，返回服务异常页面
其他云redis数据库 

#### 缓存穿透
多次访问一个缓存和库里都没有记录的数据，导致数据库压力增大，如果遇到恶意攻击，容易对服务造成巨大风险。
解决方法：
    1. 缓存空值，只能避免相同值的缓存穿透，恶意攻击可以变化不同的空对象来访问，因此都会打入到数据库，不能完全阻挡恶意攻击
    2. 布隆过滤器 （guava）

#### 缓存击穿
热点key失效瞬间，大量并发请求接入，导致数据库压力突增（比如天猫首页的聚划算商品）
可能是自然过期

解决方法：
    1. 用户过期+逻辑过期。不设置过期时间或者过期时间长一点，增加一个过期字段，再查询数据时判断是否过期，如果过期则异步地更新数据。性能较好，但有数据不一致的窗口期。
    2. 互斥锁，当发现缓存失效时，先去获得一个分布式锁，第一个拿到锁的请求去更新数据。 数据强一致性，略微影响用户体验。
    3. 不过期 + 后台定时刷新
    4. 用redis计数，来对热点参数限流，当热key过期时，只允许部分请求穿过数据库，其余请求做服务降级处理

### redis 分布式锁
独占性、高可用、防死锁、不乱抢、重入性、身份验证、可重试

1. 使用redlock创建锁，同时设置过期时间
2. 每个线程只能删除自己创建的锁，记录uuid和线程id，删除时做判断是否是自己的锁
3. 判断锁存在并是自己的锁和删除锁，这是两个步骤，如果判断成功，这是当前线程恰好阻塞且锁自动过期删除，此时很有可能其他线程创建了锁，当前线程再去删除，就会删掉别人的锁，使用lua脚本保证删除锁操作的原子性
4. 可重入, 使用hash类型，以uuid+线程id 为key，加锁次数为value，来实现可重入性
5. 超时自动释放问题，如果锁超时了，但是业务还没有结束。 自动续期。确保业务结束前，锁不要自动过期。
 

java -> redisson -> lua
lua 上锁逻辑：
    判断当前是否有锁，如果没有锁，则创建当前线程的锁，计数器为1，设置过期时间，返回null； 
    如果有锁，则判断此锁是否是当前线程持有的，如果是，则计数器加一，更新过期时间，返回null；
    如果不是当前线程的锁，则返回锁的ttl
lua 解锁逻辑：
    判断锁是否存在，不存在则返回null；
    如果存在，则判断是否是当前线程持有；
    如果是，则计数器减一，减一后如果计数为0则删除锁，并发布公告，返回1； 如果计数大于0，则刷新过期时间，返回0；
    如果不是当前线程持有，则返回null。
redisson 看门狗 -》 定时三分之一过期时间去更新锁的过期时间，确保锁不会在业务还没完成时就过期删除了，锁删除后关闭看门狗。如果锁丢失或被其他线程占用，也会停止看门狗续期
重试机制： 如果加锁失败，线程会在等待时间内订阅锁的消息，一旦收到消息，再执行尝试加锁trylock方法，如果加锁失败，又继续等待，直到等待时间耗尽，返回加锁失败。
主从一致性问题：
    使用集群模式，加锁时，在每一个redis主节点都创建锁，即为联锁：redissonClient.getMultiLock()

#### redis 优化秒杀
业务步骤：查询判断库存 -》 判断是否重复下单 -〉创建订单
优化思路：同步下单变成异步下单
具体逻辑：将库存数据、用户订单数据放入redis，上面的判断步骤全部从redis取数据（用lua脚本实现逻辑判断），而不是去数据库，这样提高了速度，判断结束后返回给客户端结果，如果秒杀成功则返回一个订单凭证（可以使用redisIdWorker 分布式ID），同时创建一个订单对象放入一个阻塞队列， 开启一个异步定时任务不断从队列中获取订单，去数据库创建订单、扣减库存等操作。或者使用redis的stream 来实现消息队列。

安全问题：


#### redlock
redis 是 AP模型，不保证数据一致性，如果有主节点挂了，可能锁没有及时同步到从节点，就会丢失。由此引出redlock
N = 2X + 1 （N是最终部署机器数，X是容错机器数），从超过半数的主节点上获取到锁，才算加锁成功。
redission解锁时要判断是否是锁住状态且锁是当前线程持有，避免解锁失败或者解错锁
redlock 性能较低

### 缓存淘汰策略
默认内存不限制，一般配置为物理总内存的四分之三
超过配置的内存上限，会报内存溢出
查看内存情况： info memory

1. 立即删除     CPU压力大
2. 惰性删除     redis.conf => lazyfree-lazyeviction yes 
3. 定期删除     定期抽检一部分key判断是否过期

redis.conf  => [memory management] => 
1. noeviction  不淘汰、内存用满时，拒绝新的写入请求，返回错误
2. allkeys-lru 
3. volatile-lru
4. allkeys-random
5. volatile-random
6. volatile-ttl
7. allkeys-lfu
8. volatile-lfu

lru 最近最少使用
    原理：并非严格的lru算法，而是在所有key中随机抽取一定数量的key，淘汰最后访问时间最早的那个。
    因为lru算法需要维护一个有序链表来记录所有key的访问顺序，维护起来比较消耗性能
    适合场景：热点数据随时间变化的场景
lfu 最不经常使用
    原理：用lfu_count 记录最近访问次数，用lfu_timer记录时间戳，定时（默认一分钟，lfu-decay-time)按时间差降低lfu_count，并更新lfu_timer为当前时间,淘汰lfu_count最小的key，如果lfu_count 一致，则淘汰最久未被访问的key
    适合场景：热点数据长期稳定的场景

根据业务场景选择合适的淘汰策略

### 源码分析
redis 6
    string -》 SDS
    set -》 intset + hashtable  如果数据全为整数且长度有限，则使用intset，这样可以节省使用hashtable产生的指针等空间占用
    zset -》 skiplist + zipList  如果小于128个元素且大小都小于64字节，则使用ziplist
    list -》 quicklist + ziplist
    hash -》 hashtable + ziplist 默认采用ziplist存储以节省内存，ziplist里面连续两个entry存储field和value，entry数量超过512或由一个entry大小超过64字节，则转为hashtable存储
redis 7
    zset -》 skiplist + listpack
    list -》 quicklist
    hash -》 hashtable + listpack


结构体：
    SDS： 简单动态字符串，可以动态扩容。因为C语言的字符串不适合使用（不可变、长度需要计算、非二进制安全），SDS 是一个结构体（字节数、申请总字节数、头类型、字符数组）
    IntSet： 保持整型元素、升序，结构体头部定义数字类型：分短整型、整型、长整型，如果数字超出范围，则动态升级数字类型，并把原先的数据拷贝到正确位置
    hash类型：又包含了两个哈希表，还有数组和链表结构，小哈希表存储哈希表的各种信息和函数指针，用于实现渐进式rehash；指针数组，用于存储实际数据的指针，实际数据存储在dictEntry对象中，此对象中可能有一个指针指向下一个对象，此链表结构，用于解决hash冲突

debug object $key 查看编码方式、lru、内存地址、引用计数等

编码方式：
    string： int(长整型 64位有符号，长度小于20) ,embstr（小于44字节的字符串，浮点数也是用此编码）, raw（大于44字节） 

数据结构：
    skiplist: 跳表 有序链表，元素两两取首作为上层索引，形成多层索引，查询复杂度O(logN)，空间复杂的O(N) 空间换时间，相当于二分查找的有序链表. 查询快，维护麻烦，新增和删除需要更新索引，时间复杂度O（log N）
    ziplist: 压缩列表，具备双端链表的主要特性，连续内存，所以不需要指针，访问效率高。如果数据量增大，申请内存较多，申请内存的效率就很低，所以存储上限较低
    quicklist：双端链表结构，每个节点是一个ziplist，限制每一个ziplist的大小，保证内存申请效率
    listpack：ziplist 因为存在级联更新问题（prevlen可能有1字节变成5字节，导致后面的数据全部都变动），在新版本逐步被listpack替代优化，listpack去掉prenlen，增加element-len，性能几乎不变，消除了级联更新问题

连续内存存储，好处是对CPU、内存友好，可以节省内存空间，读取时非常快、可以一次性多加载相邻元素。缺点是如果有元素更新且长度变化，会对后面的元素进行搬迁，性能开销较大，如果超出了分配的内存，还要进行内存重新分配和数据拷贝，开销更大。
    
### IO多路复用
基于操作系统的函数（select、poll、epoll），实现用一个进程来处理多个IO连接
redis 基于Reactor模式开发的网络事件处理器

BIO 需要多开线程处理多个客户端连接，缺点并发处理能力有限
NIO 只需一个线程，将客户端连接放入容器，while循环遍历所有连接来收发数据，缺点比较耗费CPU资源
IO多路复用 基于操作系统的epoll函数，基于事件驱动，将就绪的IO事件主动推送给应用，减少应用层面的资源消耗，提高了应用的吞吐能力

### 渐进式rehash
redis内部所有的key存在一个大的哈希表，当哈希表里面key的数量太多时，哈希冲突增多，链表长度过长，会影响查询效率
所以当key的数据达到一定阈值，就要进行扩容，创建新的hash表，把key重新计算hash值，插入新的hash表，这个过程称为rehash。redis中的hash数据类型也会进行rehash
当负载因子 >= 1, 且没有执行BGSAVE或BGREWRITEWAOF时，会进行扩容
当负载因子 > 5， 会进行扩容
当负载因子 < 0.1，会进行缩容
hash表默认大小是4，每次扩容
为了保证性能，采用渐进式rehash，每次增删改查时，进行rehash，新增key直接写入新的hash表，更新key会rehash写入新表，并同一个桶中的key也会一起写入新表。
定时rehash，为了业务空闲，很多key可能不会被访问，所以redis后台会定时rehash，每次rehash指定数量key，比如100个




1. redis 快的原因
2. redis 五个基本数据类型，string、list、hash、set、zset，还有GEO、hyperloglog、bitmap
3. redis 底层数据结构： SDS（int、embstr、raw），quicklist、ziplist、listpack、skiplist、hashtable、linkedlist
4. redis 主从复制
5. redis 哨兵 sentinel集群，raft算法选举leader，选举新master的原则
6. redis 集群
7. redis 分布式锁
8. redis 缓存穿透、缓存雪崩、缓存击穿
9. redis 实现秒杀业务，判断能否下单和下单两个操作分离
10. redis 发布订阅
11. pipeline批处理、stream消息队列
12. IO多路复用实现高并发
13. redis持久化机制，rdb、aof， 混合持久化的优势特点