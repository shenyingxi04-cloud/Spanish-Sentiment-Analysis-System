from .database_manager import DatabaseManager
from .keyword_extractor import KeywordExtractor
from .recommendation_engine import RecommendationEngine
from .sentiment_analyzer import SentimentAnalyzer
from .plotter import Plotter
from dotenv import load_dotenv
import os
class SentimentAnalysisBot:
    def __init__(self, api_token, dialogue_api_token):
        self.api_token = api_token
        self.dialogue_api_token = dialogue_api_token
        db_conn_string = 'DRIVER={ODBC Driver 11 for SQL Server};' \
                         'SERVER=localhost;' \
                         'DATABASE=school_new;' \
                         'Trusted_Connection=yes;'
        self.db_manager = DatabaseManager(db_conn_string)
        self.db_manager.remove_duplicate_feedback()
        self.keyword_extractor = KeywordExtractor()
        self.recommendation_engine = RecommendationEngine(self.db_manager)
        self.sentiment_analyzer = SentimentAnalyzer(api_token)
        self.plotter = Plotter()

    def run(self):
        print("¡Bienvenido al robot de análisis de sentimientos y conversación en español!")
        while True:
            choice = input("¿Quieres analizar un solo archivo CSV, un solo archivo o texto? (csv/archivo/texto/salir): ")
            if choice.lower() == 'salir':
                print("¡Gracias por usarlo, adiós!")
                break

            if choice.lower() == 'archivo':
                file_path = input("Introduce la ruta del archivo: ").strip('"')
                try:
                    with open(file_path, 'r', encoding='ISO-8859-1') as file:
                        content = file.read().replace('\n', ' ')
                        sentiment_result = self.sentiment_analyzer.analyze_sentiment(content)
                        if sentiment_result:
                            print("Resultado del análisis de sentimientos:")
                            print(f"Etiqueta: {sentiment_result['label']}, Puntuación: {sentiment_result['score']:.2f}")
                        else:
                            print("No se pudo determinar un sentimiento claro.")

                        user_location = input("Ingrese la ubicación para obtener recomendaciones: ")
                        user_label = input("Ingrese la etiqueta (opcional, deje en blanco si no desea filtrar por etiqueta): ")
                        recommendations = self.recommendation_engine.recommend_target_based_on_location(user_location,
                                                                                                        user_label)
                        print("Recomendaciones basadas en los resultados del análisis de sentimientos:")
                        for hotel, score in recommendations:
                            print(f"Hotel: {hotel}, Puntuación promedio: {score:.2f}")

                except FileNotFoundError:
                    print("Archivo no encontrado.")
                except Exception as e:
                    print(f"Ocurrió un error al leer el archivo: {e}")

            elif choice.lower() == 'csv':
                csv_file_path = input("Introduce la ruta del archivo CSV: ").strip('"')
                results = self.sentiment_analyzer.batch_analyze_sentiments(csv_file_path, self.db_manager,
                                                                           self.keyword_extractor)
                if results:
                    self.plotter.plot_sentiment_results(results)

                user_location = input("Ingrese la ubicación para obtener recomendaciones: ")
                user_label = input("Ingrese la etiqueta (opcional, deje en blanco si no desea filtrar por etiqueta): ")
                recommendations = self.recommendation_engine.recommend_target_based_on_location(user_location,
                                                                                                user_label)
                print("Recomendaciones basadas en los resultados del análisis de sentimientos:")
                for hotel, score in recommendations:
                    print(f"Hotel: {hotel}, Puntuación promedio: {score:.2f}")

            elif choice.lower() == 'texto':
                user_input = input("Escribe el texto que quieres analizar: ")
                sentiment_results = self.sentiment_analyzer.analyze_sentiment(user_input)
                if sentiment_results:
                    print(f"Resultado del análisis de sentimientos: {sentiment_results['label']}: {sentiment_results['score']:.2f}")
                else:
                    print("No se pudo determinar un sentimiento claro.")

                keywords = self.keyword_extractor.extract_keywords(user_input)
                print(f"Palabras clave extraídas: {keywords}")

                user_location = input("Ingrese la ubicación para obtener recomendaciones: ")
                user_label = input("Ingrese la etiqueta (opcional, deje en blanco si no desea filtrar por etiqueta): ")
                recommendations = self.recommendation_engine.recommend_target_based_on_location(user_location,
                                                                                                user_label)
                print("Recomendaciones basadas en los resultados del análisis de sentimientos:")
                for hotel, score in recommendations:
                    print(f"Hotel: {hotel}, Puntuación promedio: {score:.2f}")


if __name__ == '__main__':
    api_token = os.getenv('API_TOKEN')
    dialogue_api_token = os.getenv("DIALOGUE_API_TOKEN")
    bot = SentimentAnalysisBot(api_token, dialogue_api_token)
    bot.run()
