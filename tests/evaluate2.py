import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, accuracy_score, mean_absolute_error, confusion_matrix, classification_report, roc_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
file_path = BASE_DIR / "data" / "data2.CSV"
df = pd.read_csv(file_path, encoding='latin1')
true_ratings = pd.to_numeric(df['rating'], errors='coerce')
valid_indices = true_ratings.dropna().index  # 第一次过滤的有效索引
true_ratings = true_ratings[valid_indices]

# 提取预测评分并应用第一次过滤
predicted_ratings = (
    df['answer']
    .str.extract(r'Etiqueta: (\d+) stars')
    .astype(float)
    .values.flatten()
)
predicted_ratings = predicted_ratings[valid_indices]  # 应用第一次过滤

# 第二次过滤：去除预测评分中的 NaN
valid_predicted_indices = ~np.isnan(predicted_ratings)
true_ratings = true_ratings[valid_predicted_indices]
predicted_ratings = predicted_ratings[valid_predicted_indices]

# 合并两次过滤的索引
combined_indices = valid_indices[valid_predicted_indices]  # 关键修改点
valid_df = df.loc[combined_indices]  # 确保 valid_df 行数与标签数组一致

# 将评分转换为二分类标签，但去除评分为 3 的样本
# 评分为 1、2 为负类（0），评分为 4、5 为正类（1），评分为 3 的样本去除
valid_ratings = true_ratings[(true_ratings != 3) & (predicted_ratings != 3)]
valid_predicted_ratings = predicted_ratings[(true_ratings != 3) & (predicted_ratings != 3)]

# 重新计算 true_labels 和 predicted_labels
true_labels = np.where(valid_ratings <= 3, 0, 1)
predicted_labels = np.where(valid_predicted_ratings <= 3, 0, 1)

# 更新阈值调整函数，确保在处理评分为 3 的样本时，已去除它们
def adjust_threshold(threshold):
    adjusted_predictions = np.where(valid_predicted_ratings >= threshold, 1, 0)
    precision = precision_score(true_labels, adjusted_predictions, zero_division=1)
    recall = recall_score(true_labels, adjusted_predictions, zero_division=1)
    accuracy = accuracy_score(true_labels, adjusted_predictions)
    print(f"Threshold = {threshold}")
    print(f"Precision: {precision:.4f}, Recall: {recall:.4f}, Accuracy: {accuracy:.4f}")
    return precision, recall, accuracy

# 继续原来的步骤：阈值调整、最佳阈值选择、评价指标计算等...
thresholds = [3, 3.5, 4]
best_threshold = None
best_precision = 0
best_recall = 0
best_accuracy = 0

for threshold in thresholds:
    precision, recall, accuracy = adjust_threshold(threshold)
    # 选择最优阈值，这里优先选择精度，如果精度相同，则选择召回率
    if precision > best_precision:
        best_precision = precision
        best_recall = recall
        best_accuracy = accuracy
        best_threshold = threshold

print(f"最佳阈值: {best_threshold}")
print(f"最终 Precision: {best_precision:.4f}, Recall: {best_recall:.4f}, Accuracy: {best_accuracy:.4f}")

# 使用最佳阈值计算最终结果
adjusted_predictions = np.where(valid_predicted_ratings >= best_threshold, 1, 0)

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
mae = mean_absolute_error(valid_ratings, valid_predicted_ratings)
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
fpr, tpr, thresholds = roc_curve(true_labels, valid_predicted_ratings)
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
valid_df = df.iloc[combined_indices]  # 通过 valid_indices 来过滤数据
misclassified = valid_df[(true_labels != adjusted_predictions)]  # 获取误分类的样本

# 输出误分类样本
print("误分类的样本:")
print(misclassified)
