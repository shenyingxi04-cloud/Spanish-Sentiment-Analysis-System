# filePath：app.py
from flask import Flask, render_template, request, jsonify
from sentiment_analysis_project.models.main import SentimentAnalysisBot
from chart_utils import generate_chart
import pandas as pd
import os
import file_utils  # 导入file_utils模块
from wordcloud import WordCloud
import base64
from io import BytesIO
from dotenv import load_dotenv
app = Flask(__name__, template_folder=os.path.abspath('../frontend/templates'))  # ✅ 指定路径
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.secret_key = 'your_secret_key'

api_token = os.getenv('API_TOKEN')
dialogue_api_token = os.getenv("DIALOGUE_API_TOKEN")
bot = SentimentAnalysisBot(api_token, dialogue_api_token)

# 定义最大长度
MAX_LENGTH = 512

def generate_wordcloud(keywords):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(keywords)
    img = wordcloud.to_image()
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    analysis_type = request.form.get('analysis_type')
    if analysis_type == "texto":
        user_text = request.form.get('user_text')
        # 截断文本
        user_text = user_text[:MAX_LENGTH]
        sentiment_results = bot.sentiment_analyzer.analyze_sentiment(user_text)
        keywords = bot.keyword_extractor.extract_keywords(user_text)
        chart_data = [sentiment_results] if sentiment_results else []
        bar_img_base64, line_img_base64 = generate_chart(chart_data, analysis_type)  # 传递 analysis_type

        # 生成关键词图云
        wordcloud_img_base64 = generate_wordcloud(keywords)

        # 处理电影评论相关逻辑
        if 'film_name' in request.form:
            film_name = request.form.get('film_name')
            gender = request.form.get('gender')
            bot.db_manager.store_movie_feedback('User1', user_text, sentiment_results['label'],
                                                sentiment_results['score'], keywords, film_name=film_name,
                                                gender=gender)
            bot.db_manager.store_movie_info(film_name, gender)

        return jsonify({'result': sentiment_results, 'keywords': keywords, 'bar_chart': bar_img_base64,
                        'line_chart': line_img_base64, 'wordcloud': wordcloud_img_base64})

    elif analysis_type == "archivo":
        file_path = request.form.get('user_text').strip('"')
        try:
            content = file_utils.read_file(file_path)
            # 截断文本
            content = content[:MAX_LENGTH]
            sentiment_results = bot.sentiment_analyzer.analyze_sentiment(content)
            keywords = bot.keyword_extractor.extract_keywords(content)
            chart_data = [sentiment_results] if sentiment_results else []
            bar_img_base64, line_img_base64 = generate_chart(chart_data, analysis_type)  # 传递 analysis_type

            # 生成关键词图云
            wordcloud_img_base64 = generate_wordcloud(keywords)

            # 处理电影评论相关逻辑
            if 'film_name' in request.form:
                film_name = request.form.get('film_name')
                gender = request.form.get('gender')
                bot.db_manager.store_movie_feedback('User1', content, sentiment_results['label'],
                                                    sentiment_results['score'], keywords, film_name=film_name,
                                                    gender=gender)
                bot.db_manager.store_movie_info(film_name, gender)

            return jsonify({'result': sentiment_results, 'keywords': keywords, 'bar_chart': bar_img_base64,
                            'line_chart': line_img_base64, 'wordcloud': wordcloud_img_base64})
        except FileNotFoundError:
            return jsonify({'error': 'Archivo no encontrado.'})
        except Exception as e:
            return jsonify({'error': f'Error al procesar el archivo: {str(e)}'})

    elif analysis_type == "csv":
        csv_file = request.files.get('user_file')
        if not csv_file:
            return jsonify({'error': 'No se ha proporcionado el archivo CSV.'})
        try:
            df = file_utils.read_csv_file(csv_file)
            # 区分酒店和电影的 CSV 文件
            if 'hotel' in df.columns:  # 处理酒店评论
                required_columns = ['review_text', 'location', 'label', 'hotel']
                for col in required_columns:
                    if col not in df.columns:
                        return jsonify({'error': f'Error: No se encontró la columna \'{col}\' en el archivo CSV!'})
                results = []
                for idx, row in df.iterrows():
                    review = row['review_text']
                    # 截断文本
                    review = review[:MAX_LENGTH]
                    location = row['location']
                    label = row['label']
                    hotel = row['hotel']
                    sentiment_results = bot.sentiment_analyzer.analyze_sentiment(review)
                    if sentiment_results:
                        keywords = bot.keyword_extractor.extract_keywords(review)  # 提取关键词
                        result = {
                            "review_index": idx,
                            "sentiment": sentiment_results['label'],
                            "score": sentiment_results['score'],
                            "location": location,
                            "label": label,
                            "hotel": hotel
                        }
                        results.append(result)
                        bot.db_manager.store_feedback('User1', review, sentiment_results['label'],
                                                      sentiment_results['score'], keywords, place="", location=location,
                                                      label=label, hotel=hotel)
                        bot.db_manager.store_hotel_info(hotel, location, label)

                bar_img_base64, line_img_base64 = generate_chart(results, analysis_type)  # 传递 analysis_type
                return jsonify({'result': results, 'bar_chart': bar_img_base64, 'line_chart': line_img_base64})

            elif 'film_name' in df.columns:  # 处理电影评论
                required_columns = ['review_text', 'film_name', 'gender']
                for col in required_columns:
                    if col not in df.columns:
                        return jsonify({'error': f'Error: No se encontró la columna \'{col}\' en el archivo CSV!'})

                results = []
                for idx, row in df.iterrows():
                    review = row['review_text']
                    # 截断文本
                    review = review[:MAX_LENGTH]
                    film_name = row['film_name']
                    gender = row['gender']
                    sentiment_results = bot.sentiment_analyzer.analyze_sentiment(review)
                    if sentiment_results:
                        keywords = bot.keyword_extractor.extract_keywords(review)  # 提取关键词
                        result = {
                            "review_index": idx,
                            "sentiment": sentiment_results['label'],
                            "score": sentiment_results['score'],
                            "film_name": film_name,
                            "gender": gender
                        }
                        results.append(result)
                        # 假设存在 store_movie_feedback 和 store_movie_info 方法
                        bot.db_manager.store_movie_feedback('User1', review, sentiment_results['label'],
                                                            sentiment_results['score'], keywords, film_name=film_name,
                                                            gender=gender)
                        bot.db_manager.store_movie_info(film_name, gender)

                bar_img_base64, line_img_base64 = generate_chart(results, analysis_type)  # 传递 analysis_type
                return jsonify({'result': results, 'bar_chart': bar_img_base64, 'line_chart': line_img_base64})

            else:
                return jsonify({'error': 'El archivo CSV no contiene columnas de hotel ni de película.'})

        except Exception as e:
            return jsonify({'error': f'Error al procesar el archivo CSV: {str(e)}'})

    elif analysis_type == "recomendaciones":
        user_location = request.form.get('user_location')
        user_label = request.form.get('user_label')
        if user_label:
            recommendations = bot.recommendation_engine.recommend_target_based_on_location(user_location, user_label)
        else:
            recommendations = bot.recommendation_engine.recommend_target_based_on_location(user_location)
        result = [{'hotel': hotel, 'avg_score': score} for hotel, score in recommendations]
        bar_img_base64, line_img_base64 = generate_chart(result, analysis_type)  # 传递
        return jsonify({'result': result, 'bar_chart': bar_img_base64, 'line_chart': line_img_base64})

    elif analysis_type == "recomendaciones_peliculas":  # 新增电影推荐功能
        user_gender = request.form.get('user_gender')
        if user_gender:
            movie_recommendations = bot.recommendation_engine.recommend_movies_based_on_gender(user_gender)
            if movie_recommendations:
                result = [{'movie': movie, 'avg_score': score} for movie, score in movie_recommendations]
                bar_img_base64, line_img_base64 = generate_chart(result, analysis_type)  # 传递 analysis_type
                return jsonify({'movie_recommendations': result, 'bar_chart': bar_img_base64, 'line_chart': line_img_base64})
            else:
                return jsonify({'error': 'No se encontraron recomendaciones de películas.'})
        else:
            return jsonify({'error': 'No se proporcionó el género de película.'})

if __name__ == '__main__':
    app.run(debug=True,port=5001)
