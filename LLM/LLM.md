### LLM
    基于transformer
    训练时，“吃”下了整个互联网级别的文本数据（书籍、网页、文章等）
    学会了给定前面所有的文字，预测下一个字是什么， 并且学会了语法、事实知识、逻辑推理、指令遵循

    所以问答过程，即是启动一个极其复杂的文本补全程序，问题相当于是给它的开头，它则以一种高度智能化的方式，专注地、一个字一个字地，将这个开头补完成一个完整、连贯且有用的回答。

    比喻：
        大语言模型，更像一个没有耳朵、眼睛、嘴巴的人，虽然不能说、听、看，无法直观的感受世界，但是通过海量的语料喂养，掌握了每个词与其他词的相关度，所以每当谈及到一个词时，他能联想到相关的东西，那么这个词就具像化了， 理论上跟人体记忆、联想的原理也是一样的。
        就像我从来没有去过火星，没有见过火星，当我阅读了大量关于火星的书籍、大量的描述后，这些知识让我在脑海中构建了对于火星有一个全方位的认知体系，在别人问到我关于火星各方面的知识时，我都可以回答出相关度非常高的描述。

#### 分词技术：
    子词分词 思想， BPE算法， Byte Pair Encoding 
    中文使用 Byte based BPE（GPT、通义千问、claude、深求）， WordPiece + 预分词（BERT, Google Gemini, T5）

    优点：
        应对词表爆炸，彻底较少内存占用
        赋予模型举一反三的泛化能力
        高效处理生僻词和拼写错误

#### transformer
    RNN -> Attention is all you need -> transformer
    RNN 和LSTM 对于顺序处理， 容易遗忘、速度慢无法并行

    编码器 + 解码器
    嵌入： 词（token）-> 数字向量 + 位置编码

    编码：整个句子 -> 深度理解 -> 上下文矩阵
    解码器：自回归模型，上下文 -> 预测下一个词

    多头自注意力机制：
        计算每个词语句子中其他词的关联程度
    优势：
        并行计算、解决了长程依赖问题、可扩展性

#### 算法
    方向导数
    梯度下降算法
    反向传播算法
    激活函数

### langchain
    提示词模版  
        PromptTemplate : 用于非对话式提示词， 比如文章撰写、摘要生成、问题问答
        chatPromptTemplate： 用于对话式提示词，适合持续多轮对话
        systemMessagePromptTemplate
        humanMessagePromptTemplate

        fewShotPromptTemplate: 根据少量案例（输入、输出、描述）进行学习，
    结果解析器
        csv, datetime, xml, json
    RAG
    model： 
        LLM、
        ChatModel、
        文本嵌入模型

    chain链
        invoke
        predict
        batch
    文档链

    数学链

    SQL查询链
        生成sql

### RAG
    文档加载、切割

    向量化

    向量存储：
        chroma， FAISS， Lance

    检索器
        VectorStore
ChatOpenAI()