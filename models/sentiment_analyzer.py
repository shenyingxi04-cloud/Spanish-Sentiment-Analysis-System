import requests
import pandas as pd

class SentimentAnalyzer:
    def __init__(self, api_token):
        self.api_token = api_token
        self.sentiment_api_url = "https://api-inference.huggingface.co/models/nlptown/bert-base-multilingual-uncased-sentiment"
        self.sentiment_headers = {"Authorization": f"Bearer {self.api_token}"}

    def analyze_sentiment(self, content):
        response = requests.post(self.sentiment_api_url, headers=self.sentiment_headers, json={"inputs": content})
        if response.status_code == 200:
            json_response = response.json()[0]
            highest_probability_item = max(json_response, key=lambda x: x['score'])
            star_label = highest_probability_item['label']
            try:
                star_rating = int(star_label.split()[0])
            except (IndexError, ValueError):
                print(f"无法从标签 {star_label} 中提取星级数字。")
                return None
            if star_rating < 1:
                print(f"警告：提取的星级 {star_rating} 低于预期的 1，将使用 1 进行转换。")
                star_rating = 1
            elif star_rating > 5:
                print(f"警告：提取的星级 {star_rating} 高于预期的 5，将使用 5 进行转换。")
                star_rating = 5
            new_rating = (star_rating - 1) / 4 * 3
            print(f"Etiqueta: {star_label}, Puntuación: {new_rating:.2f}")
            return {'label': star_label, 'score': new_rating}
        else:
            print(f"Error: {response.status_code}, {response.json()}")
            return None

    def batch_analyze_sentiments(self, csv_file_path, db_manager, keyword_extractor):
        try:
            df = pd.read_csv(csv_file_path, on_bad_lines="skip")
            print("CSV 文件列名:", df.columns.tolist())

            required_columns = ['review_text', 'location', 'label', 'hotel']
            for col in required_columns:
                if col not in df.columns:
                    print(f"错误: CSV 文件中找不到 '{col}' 列！")
                    return []

            results = []
            for idx, row in df.iterrows():
                review = row['review_text']
                location = row['location']
                label = row['label']
                hotel = row['hotel']

                sentiment_results = self.analyze_sentiment(review)
                if sentiment_results:
                    keywords = keyword_extractor.extract_keywords(review)
                    results.append({
                        "review_index": idx,
                        "sentiment": sentiment_results['label'],
                        "score": sentiment_results['score'],
                        "location": location,
                        "label": label,
                        "hotel": hotel
                    })
                    db_manager.store_feedback('User1', review, sentiment_results['label'], sentiment_results['score'],
                                              keywords, place="", location=location, label=label, hotel=hotel)
                    db_manager.store_hotel_info(hotel, location, label)
                print(f"处理 {idx + 1}/{len(df)} 条评论")

            return results

        except Exception as e:
            print(f"处理 CSV 文件时出错: {e}")
            return []