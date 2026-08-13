git add .import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, accuracy_score, mean_absolute_error, confusion_matrix, classification_report, roc_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
file_path = BASE_DIR / "data" / "data1.CSV"
df = pd.read_csv(file_path, encoding='latin1')

# 处理真实评分
true_ratings = pd.to_numeric(df['review_rate'], errors='coerce')
valid_indices = true_ratings.dropna().index
df = df.loc[valid_indices].copy()
true_ratings = df['review_rate'].values

# 提取预测评分，直接使用星级作为评分
predicted_ratings = df['answer'].str.extract(r'Etiqueta: (\d+) stars', expand=False).astype(float)
valid_predicted_indices = ~np.isnan(predicted_ratings)
df = df[valid_predicted_indices].reset_index(drop=True)
true_ratings = df['review_rate'].values
predicted_ratings = predicted_ratings[valid_predicted_indices].values

# 将评分转换为二分类标签
# 真实评分 0 - 5 为负类（0），6 - 10 为正类（1）
true_labels = np.where(true_ratings <= 5, 0, 1)

# 更新阈值调整函数
def adjust_threshold(threshold):
    adjusted_predictions = np.where(predicted_ratings >= threshold, 1, 0)
    precision = precision_score(true_labels, adjusted_predictions, zero_division=1)
    recall = recall_score(true_labels, adjusted_predictions, zero_division=1)
    accuracy = accuracy_score(true_labels, adjusted_predictions)
    print(f"Threshold = {threshold}")
    print(f"Precision: {precision:.4f}, Recall: {recall:.4f}, Accuracy: {accuracy:.4f}")
    return precision, recall, accuracy

# 阈值调整、最佳阈值选择
# 由于预测评分是 1 - 5 星级，调整阈值范围
thresholds = np.arange(2, 4, 0.5)
best_threshold = None
best_precision = 0
best_recall = 0
best_accuracy = 0

for threshold in thresholds:
    precision, recall, accuracy = adjust_threshold(threshold)
    if precision > best_precision:
        best_precision = precision
        best_recall = recall
        best_accuracy = accuracy
        best_threshold = threshold

print(f"最佳阈值: {best_threshold}")
print(f"最终 Precision: {best_precision:.4f}, Recall: {best_recall:.4f}, Accuracy: {best_accuracy:.4f}")

# 使用最佳阈值计算最终结果
adjusted_predictions = np.where(predicted_ratings >= best_threshold, 1, 0)

# 计算精准率
precision = precision_score(true_labels, adjusted_predictions, zero_division=1)
print(f"Precision 精准率: {precision:.4f}")

# 计算召回率
recall = recall_score(true_labels, adjusted_predictions, zero_division=1)
print(f"Recall 召回率: {recall:.4f}")

# 计算准确率
accuracy = accuracy_score(true_labels, adjusted_predictions)
print(f"Accuracy 准确率: {accuracy:.4f}")

# 计算平均绝对误差
mae = mean_absolute_error(true_ratings, predicted_ratings)
print(f"MAE 平均绝对误差: {mae:.4f}")

# 计算混淆矩阵
cm = confusion_matrix(true_labels, adjusted_predictions)
print("混淆矩阵(Confusion Matrix):")
print(cm)

# 可视化混淆矩阵
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')
plt.show()

# 分类报告
print("分类报告(Classification Report):")
print(classification_report(true_labels, adjusted_predictions, zero_division=1))

# 计算 ROC 曲线和 AUC
fpr, tpr, thresholds = roc_curve(true_labels, predicted_ratings)
roc_auc = auc(fpr, tpr)

# 绘制 ROC 曲线
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.show()

# 分析误分类样本
df['true_label'] = true_labels
df['final_prediction'] = adjusted_predictions
misclassified = df[df['true_label'] != df['final_prediction']]

# 输出误分类样本
print("误分类的样本:")
print(misclassified)
    