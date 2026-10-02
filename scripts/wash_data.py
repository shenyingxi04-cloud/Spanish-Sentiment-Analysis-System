import pandas as pd

# 定义原始文件路径和转换后文件的保存路径
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

input_file_path = DATA_DIR / "film_reviews_result.csv"
output_file_path = DATA_DIR / "cleaned_file.csv"

# 读取以 | 为分隔符的 CSV 文件
df = pd.read_csv(input_file_path, sep='|')

# 将 DataFrame 保存为以逗号为分隔符的 CSV 文件
df.to_csv(output_file_path, sep=',', na_rep='nan', index=False)

print(f"文件已成功转换并保存到 {output_file_path}")
