## 索引

###  前缀索引
    建立语法：alter... add index $column($lenth)；
    使用场景：比如varchar、text，如果要建立索引，必须指定前缀长度
    怎么确定前缀长度？
    查看前缀区分度：select count(distinct left($column, 10))/count(*) from $table; 
    查看前10个字符的区分度，依次增加前缀长度，直到区分度接近1，前缀也不能太长，否则太占用空间。

    缺陷：无法进行排序（因为索引里只有前缀，没有完整字段值，没法排序）

### 大表追加索引
    场景：已有大量记录行，追加创建索引。可能造成读写阻塞进而影响业务
    方案：Online DDL 算法 或者 Percona Toolkit 的 pt-online-schema-change
        1. 分析表结构和数据分布
        确定是否适合创建索引
        SELECT COUNT(DISTINCT your_column) / COUNT(*) FROM your_large_table;
        2. 检查磁盘空间是否充足
        3. 执行方案
            使用 Online DDL：
            ALTER TABLE your_large_table ADD INDEX idx_your_column (your_column), ALGORITHM=INPLACE, LOCK=NONE;
            ALGORITHM=INPLACE：使用在线算法。
            LOCK=NONE：允许并发读写。这是最不阻塞的模式。COPY模式会阻塞读写 
            优点：安全，速度快

            备选方案：使用 Percona Toolkit 的 pt-online-schema-change
            bash：pt-online-schema-change --alter "ADD INDEX idx_email (email)" D=database_name,t=your_large_table --execute
            原理：创建影子表，以触发器形式将增量数据复制一份到影子表，然后以原子操作替换表名，过程透明。
            优点：最平稳安全、业务影响最小

        4. 先在从库进行测试，在业务低峰期操作
        5. 监控数据库状态
            HOW PROCESSLIST; -- 查看当前连接和状态
            SHOW ENGINE INNODB STATUS; -- 查看InnoDB详细信息，包括锁
    
## 慢查询

### 定位方法论
    确定是数据库层面慢
    开启慢查询，指定超时阈值：  
        set global slow_query_log = on;  show variables like '%slow_query_log'; 可以看到日志文件目录
        set [global|session] slow_query_time = 3; show variables like '%slow_query_time';
    用Explain、Show profiles 等语句
    1.sql 等待时间长 -> 服务器参数调优
    2.sql 执行时间长 -> 索引优化、表设计优化等

    查看系统参数： show [Global|Session] status like 'xx';
        慢查询数：show status like '%slow_query';
    
    查看慢查询：mysqldumpslow -s -t 5 /var/lib/mysql/$log_dir

    关闭慢查询日志

    Profile：查sql性能
        开启： show variables like 'prifiling'; set prifiling = 'ON';
        执行一次慢 sql
        找到慢查询的id： show prifiles; 
        查看慢查询耗时： show profile cpu,block io for query $id;  -- all/cpu/block io/memory...
    
    Explain 查看执行计划
        输出：id| select_type| table| partitions| type| possible_keys| key| key_len| ref| rows| filtered| Extra
        id：一个select一个id，id越大优先级越高越先执行
        select_type：查询类型，SIMPLE、PRIMARY、
        type：
            System、const、eq_ref、ref、full_text、ref_or_null、index_merge、unique_subquery、range、index、all 
            性能依次下降，ref及之前的较佳，最差也要尽量达到range，all最差
        possible_keys： 可能用到的索引
        key：实际用到的索引
        key_len: 用到的索引字符长度
        rows：预估扫描出来的行数

        如果是in查询，explain的结果可能有两条，但是id一致，因为in查询会优化为join
        如果是union，可能有三条结果，一条是临时表


            

        
