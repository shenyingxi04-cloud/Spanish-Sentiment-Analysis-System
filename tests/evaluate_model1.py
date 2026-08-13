import pandas as pd
import re
import nltk
import numpy as np
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, accuracy_score, mean_absolute_error, recall_score, confusion_matrix
import csv,os
from pathlib import Path
nltk.download('punkt')
nltk.download('punkt_tab')  # 可能 `punkt` 就够了

# 1. 原始数据读取（容忍错误格式）
DATA_PATH = os.getenv("DATA_PATH")

raw_df = pd.read_csv(
    DATA_PATH,
    encoding='latin-1',
    header=None,
    names=['raw_data'],
    dtype=str,
    on_bad_lines='warn'
)

# 2. 列错位修正函数
def correct_columns(row):
    raw_data = row['raw_data']

    # 如果 raw_data 是 bytes，则解码为 UTF-8
    if isinstance(raw_data, bytes):
        raw_data = raw_data.decode('utf-8', errors='ignore')

    # 确保 raw_data 是字符串
    raw_data = str(raw_data)

    # 使用正则表达式匹配
    match = re.match(r'^(\d+)[,\s]+(.*)', raw_data)
    if match:
        label = match.group(1).strip()
        text = match.group(2).strip()
        # 清理文本中的残留字符
        text = re.sub(r'[\x00-\x1F\x80-\xFF]', ' ', text)
        return pd.Series({'label': label, 'review_text': text})

    return pd.Series({'label': None, 'review_text': None})

# 确保已下载 nltk 资源
nltk.download("stopwords")
nltk.download("punkt")

# 读取数据
file_path = os.getenv("DATA_PATH")
df = pd.read_csv(file_path, encoding="latin1")

# 选择有用列
df = df[["review_text", "label"]]

# 删除缺失值
df.dropna(inplace=True)

# 3. 标签清洗和过滤
# 去除评分为 3 的样本
valid_labels = {'0', '1'}  # 允许的标签值

# 标签格式统一处理
df['label'] = df['label'].apply(
    lambda x: x if str(x).strip() in valid_labels else None
)

# 删除无效行
df = df.dropna(subset=['label', 'review_text'])
df['label'] = df['label'].astype(int)  # 转换为整数

# 将评分转换为二分类标签
# 这里假设 0 为负类，1 为正类
# 由于已经去除了 3，所以无需额外判断
df['label'] = df['label'].apply(lambda x: 0 if x == 0 else 1)

# 4. 文本编码修正
def fix_encoding(text):
    try:
        return text.encode('latin-1').decode('utf-8')
    except:
        return text

df['review_text'] = df['review_text'].apply(fix_encoding)

# 5. 划分训练集和测试集
# 减少训练数据量
X_train, X_test, y_train, y_test = train_test_split(df["review_text"], df["label"], test_size=0.3, random_state=42)

# 6. 文本向量化
# 降低特征维度
vectorizer = TfidfVectorizer(max_features=1000)  # 降低词汇数
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# 7. 训练模型
# 训练随机森林
# 简化模型复杂度
rf_model = RandomForestClassifier(n_estimators=20, random_state=42)
rf_model.fit(X_train_tfidf, y_train)
rf_preds = rf_model.predict(X_test_tfidf)

# 训练SVM
svm_model = SVC(kernel="linear")
svm_model.fit(X_train_tfidf, y_train)
svm_preds = svm_model.predict(X_test_tfidf)

# 训练MLP神经网络
mlp_model = MLPClassifier(hidden_layer_sizes=(100,), max_iter=300, random_state=42)
mlp_model.fit(X_train_tfidf, y_train)
mlp_preds = mlp_model.predict(X_test_tfidf)

# 8. 评估模型
print("Random Forest:")
print(classification_report(y_test, rf_preds))
print(f"Precision 精准率: {accuracy_score(y_test, rf_preds):.4f}")
print(f"Recall 召回率: {recall_score(y_test, rf_preds):.4f}")
print(f"Accuracy 准确率: {accuracy_score(y_test, rf_preds):.4f}")
print("混淆矩阵(Confusion Matrix):")
print(confusion_matrix(y_test, rf_preds))
DATA_DIR = Path(os.getenv("PROJECT_DATA_DIR"))

# 9. 生成新数据集文件
output_path = DATA_DIR / "cleaned_dataset.csv"
# 9. 生成新数据集文件，加入 errors='ignore'
df[['label', 'review_text']].to_csv(
    output_path,
    index=False,
    encoding='latin1',
    quoting=csv.QUOTE_ALL,  # 直接使用 csv.QUOTE_ALL
    errors='ignore'  # 忽略不能编码的字符
)

# 10. 验证结果
print(f"清洗后数据量：{len(df)}")
print("最终标签分布：")
print(df['label'].value_counts())

# 示例输出查看
print("\n前3条有效数据：")
print(df[['label', 'review_text']].head(3).to_string(index=False))
