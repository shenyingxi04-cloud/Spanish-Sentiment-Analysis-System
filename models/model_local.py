from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 模型名称
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
# 定义保存路径
save_directory = r"D:\Program Files (x86)\model sentiment"

# 加载分词器并指定缓存目录为保存路径
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=save_directory)
# 加载模型并指定缓存目录为保存路径
model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=save_directory)

# 保存分词器和模型到指定路径（这里由于指定了 cache_dir，其实已经保存到该路径了，但为了保险可以再显式保存一次）
tokenizer.save_pretrained(save_directory)
model.save_pretrained(save_directory)

print(f"模型和分词器已成功保存到 {save_directory}")
