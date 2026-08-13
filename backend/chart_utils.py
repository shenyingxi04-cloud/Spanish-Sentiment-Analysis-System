import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import seaborn as sns
import pandas as pd

def generate_chart(chart_data, analysis_type):
    try:
        if not chart_data:
            print("Error: Los resultados están vacíos")
            return None, None

        df = pd.DataFrame(chart_data)

        # 判断是酒店评论数据集还是电影评论数据集
        is_hotel_data = "hotel" in df.columns
        is_movie_data = "film_name" in df.columns

        if analysis_type in ["texto", "archivo", "csv"]:
            # 处理文本、文件、CSV 分析结果
            plt.figure(figsize=(10, 6))
            sns.set(style="whitegrid")
            sns.countplot(x="sentiment", data=df)
            plt.title("Resultados del análisis de sentimiento")
            plt.xlabel("Sentimientos")
            plt.ylabel("Número de archivos")

            bar_img_buf = io.BytesIO()
            plt.savefig(bar_img_buf, format='png')
            plt.close()
            bar_img_buf.seek(0)
            bar_img_base64 = base64.b64encode(bar_img_buf.read()).decode('utf-8')

            plt.figure(figsize=(12, 6))
            sns.lineplot(x=df.index, y=df["score"], marker='o')

            if is_hotel_data:
                column_name = "hotel"
            elif is_movie_data:
                column_name = "film_name"
            else:
                # 如果既不是酒店也不是电影数据，默认使用 "location"
                column_name = "location"

            xtick_labels = [f"{idx} - {name[:10]}..." if len(name) > 10 else f"{idx} - {name}"
                            for idx, name in zip(df.index, df[column_name])]

            plt.xticks(ticks=df.index, labels=xtick_labels, rotation=90)
            plt.tight_layout()
            plt.title("Puntuación de opinión para cada archivo")
            plt.xlabel("Archivo")
            plt.ylabel("Puntuación de sentimiento")

            line_img_buf = io.BytesIO()
            plt.savefig(line_img_buf, format='png')
            plt.close()
            line_img_buf.seek(0)
            line_img_base64 = base64.b64encode(line_img_buf.read()).decode('utf-8')

        elif analysis_type == "recomendaciones":
            # 处理推荐查询结果
            plt.figure(figsize=(10, 6))
            sns.set(style="whitegrid")
            if is_hotel_data:
                sns.barplot(x="hotel", y="avg_score", data=df)
                plt.xlabel("Hoteles")
            elif is_movie_data:
                sns.barplot(x="film_name", y="avg_score", data=df)
                plt.xlabel("Películas")
            else:
                print("Tipo de datos no reconocido")
                return None, None

            plt.title("Recomendaciones")
            plt.ylabel("Puntuación promedio")
            plt.xticks(rotation=45)

            bar_img_buf = io.BytesIO()
            plt.savefig(bar_img_buf, format='png')
            plt.close()
            bar_img_buf.seek(0)
            bar_img_base64 = base64.b64encode(bar_img_buf.read()).decode('utf-8')

            line_img_base64 = None  # 推荐结果不绘制折线图

        elif analysis_type == "recomendaciones_peliculas":  # 新增电影评论分析类型
            # 处理电影评论分析结果
            plt.figure(figsize=(10, 6))
            sns.set(style="whitegrid")
            sns.countplot(x="sentiment", data=df)
            plt.title("Resultados del análisis de sentimiento de películas")
            plt.xlabel("Sentimientos")
            plt.ylabel("Número de películas")

            bar_img_buf = io.BytesIO()
            plt.savefig(bar_img_buf, format='png')
            plt.close()
            bar_img_buf.seek(0)
            bar_img_base64 = base64.b64encode(bar_img_buf.read()).decode('utf-8')

            plt.figure(figsize=(12, 6))
            sns.lineplot(x=df.index, y=df["score"], marker='o')

            xtick_labels = [f"{idx} - {name[:10]}..." if len(name) > 10 else f"{idx} - {name}"
                            for idx, name in zip(df.index, df["film_name"])]

            plt.xticks(ticks=df.index, labels=xtick_labels, rotation=90)
            plt.tight_layout()
            plt.title("Puntuación de opinión para cada película")
            plt.xlabel("Película")
            plt.ylabel("Puntuación de sentimiento")

            line_img_buf = io.BytesIO()
            plt.savefig(line_img_buf, format='png')
            plt.close()
            line_img_buf.seek(0)
            line_img_base64 = base64.b64encode(line_img_buf.read()).decode('utf-8')

        else:
            print("Tipo de análisis no soportado")
            return None, None

        return bar_img_base64, line_img_base64
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return None, None