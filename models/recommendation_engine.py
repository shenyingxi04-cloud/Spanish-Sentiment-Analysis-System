# filePath：recommendation_engine.py
class RecommendationEngine:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def recommend_target_based_on_location(self, user_location, user_label=None):
        cursor = self.db_manager.db_conn.cursor()
        try:
            if user_label:
                query = """
                    SELECT TOP 10 hotels.hotel, AVG(feedback.score) as avg_score 
                    FROM feedback 
                    JOIN hotels ON feedback.location = hotels.location AND feedback.label = hotels.label AND feedback.hotel = hotels.hotel
                    WHERE feedback.location =? AND feedback.label =?
                    GROUP BY hotels.hotel 
                    ORDER BY avg_score DESC
                """
                cursor.execute(query, (user_location, user_label))
            else:
                query = """
                    SELECT TOP 10 hotels.hotel, AVG(feedback.score) as avg_score 
                    FROM feedback 
                    JOIN hotels ON feedback.location = hotels.location AND feedback.hotel = hotels.hotel
                    WHERE feedback.location =? 
                    GROUP BY hotels.hotel 
                    ORDER BY avg_score DESC
                """
                cursor.execute(query, (user_location,))

            recommendations = cursor.fetchall()
            print("Recomendaciones basadas en los resultados del análisis de sentimientos:")
            for hotel, score in recommendations:
                print(f"Hotel: {hotel}, Puntuación promedio: {round(score, 2)}")

            return recommendations
        except Exception as e:
            print(f"执行推荐查询时出现错误: {e}")
            return []

    def recommend_movies_based_on_gender(self, gender):
        # 将输入的 gender 字符串按逗号分隔成列表
        gender_list = gender.split(',')
        cursor = self.db_manager.db_conn.cursor()
        try:
            conditions = []
            for g in gender_list:
                # 构建包含指定词缀的条件
                conditions.append(f"movie_feedback.gender LIKE '%{g.strip()}%'")
            condition_str = " OR ".join(conditions)

            query = f"""
                SELECT TOP 10 movies.movie, AVG(movie_feedback.score) as avg_score 
                FROM movie_feedback 
                JOIN movies ON movie_feedback.film_name = movies.movie
                WHERE {condition_str}
                GROUP BY movies.movie 
                ORDER BY avg_score DESC
            """
            # 执行 SQL 查询
            cursor.execute(query)
            recommendations = cursor.fetchall()
            if not recommendations:
                print("No se encontraron recomendaciones.")
                return []
            else:
                print("Recomendaciones de películas basadas en género:")
                for movie, score in recommendations:
                    print(f"Película: {movie}, Puntuación promedio: {round(score, 2)}")
                return recommendations
        except Exception as e:
            print(f"执行电影推荐查询时出现错误: {e}")
            return []
