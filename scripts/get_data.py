import pandas as pd

# 定义原始 CSV 文件路径和新 CSV 文件路径
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

original_file_path  = DATA_DIR / "Balanced_AHR.csv"
new_file_path = DATA_DIR / "getdata.csv"
# 读取原始 CSV 文件
try:
    df = pd.read_csv(original_file_path)
except FileNotFoundError:
    print(f"未找到文件: {original_file_path}")
    exit(1)

# 提取剩余数据的前 48 行
next_48_rows = df.head(118)

# 将这 48 行数据追加到新 CSV 文件的末尾
next_48_rows.to_csv(new_file_path, mode='a', header=False, index=False)

# 从原始文件中删除这 48 行数据（可选）
remaining_rows = df[118:]
remaining_rows.to_csv(original_file_path, index=False)

print(f"剩余数据的前 48 行数据已成功追加到 {new_file_path}")