import spacy

# 假设数据库列的定义长度为 50
MAX_KEYWORD_LENGTH = 50

class KeywordExtractor:
    def __init__(self):
        self.nlp = spacy.load(r"C:\Users\shenyingxi\AppData\Local\Programs\Python\Python311\Lib\site-packages\es_core_news_sm\es_core_news_sm-3.8.0")

    def extract_keywords(self, content):
        doc = self.nlp(content)
        keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
        # 将关键词列表转换为字符串
        keyword_str = ", ".join(keywords)
        # 处理 keywords 长度，确保不超过数据库列的定义长度
        if len(keyword_str) > MAX_KEYWORD_LENGTH:
            keyword_str = keyword_str[:MAX_KEYWORD_LENGTH]
        return keyword_str