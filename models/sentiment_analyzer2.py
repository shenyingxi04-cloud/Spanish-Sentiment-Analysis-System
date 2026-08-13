import pandas as pd
import nltk
import numpy as np
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, accuracy_score, recall_score, confusion_matrix
import csv

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download("stopwords")
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

# 1. 读取数据
df = pd.read_csv(DATA_DIR / "cleaned_file.csv", encoding='latin-1')
# 选择有用列
df = df[["review_text", "review_rate"]].copy()

# 删除缺失值
df.dropna(inplace=True)

# 2. 标签清洗和过滤
# 重新定义标签转换函数
def transform_label(label):
    try:
        label = int(label)
        return 0 if label <= 5 else 1
    except (ValueError, TypeError):
        return None

# 应用标签转换函数
df['review_rate'] = df['review_rate'].apply(transform_label)

# 删除无效行
df = df.dropna(subset=['review_rate', 'review_text'])

# 3. 文本编码修正
def fix_encoding(text):
    try:
        return text.encode('latin-1').decode('utf-8')
    except:
        return text

df['review_text'] = df['review_text'].apply(fix_encoding)

# 4. 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(df["review_text"], df["review_rate"], test_size=0.3, random_state=42)

# 5. 文本向量化
# 调整特征维度
vectorizer = TfidfVectorizer(max_features=2000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# 6. 训练模型
# 调整随机森林参数
rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_split=5, random_state=42)
rf_model.fit(X_train_tfidf, y_train)
rf_preds = rf_model.predict(X_test_tfidf)

# 7. 评估模型
print("Random Forest:")
print(classification_report(y_test, rf_preds))
print(f"Precision 精准率: {accuracy_score(y_test, rf_preds):.4f}")
print(f"Recall 召回率: {recall_score(y_test, rf_preds):.4f}")
print(f"Accuracy 准确率: {accuracy_score(y_test, rf_preds):.4f}")
print("混淆矩阵(Confusion Matrix):")
print(confusion_matrix(y_test, rf_preds))

# 8. 生成新数据集文件
# 这里需要你将路径修改为实际的保存路径
output_path = r'E:\Desktop\学习工作\计算机\毕业设计\cleaned_dataset.csv'
df[['review_rate', 'review_text']].to_csv(
    output_path,
    index=False,
    encoding='latin1',
    quoting=csv.QUOTE_ALL,
    errors='ignore'
)

# 9. 验证结果
print(f"清洗后数据量：{len(df)}")
print("最终标签分布：")
print(df['review_rate'].value_counts())

# 示例输出查看
print("\n前3条有效数据：")
print(df[['review_rate', 'review_text']].head(3).to_string(index=False))