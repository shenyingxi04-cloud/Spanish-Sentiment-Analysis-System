import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class Plotter:
    def plot_sentiment_results(self, results):
        try:
            sns.set(style="whitegrid")
            if not results:
                print("Error: results is empty")
                return
            df = pd.DataFrame(results)

            plt.figure(figsize=(10, 6))
            sns.countplot(x="sentiment", data=df)
            plt.title("Resultados del análisis de sentimiento", fontsize=20)
            plt.xlabel("Sentimientos", fontsize=20)
            plt.ylabel("Número de archivos", fontsize=20)
            plt.show()

            plt.figure(figsize=(12, 6))
            sns.lineplot(x=df.index, y=df["score"], marker='o')

            xtick_labels = [f"{idx} - {name[:10]}..." if len(name) > 10 else f"{idx} - {name}"
                            for idx, name in zip(df.index, df["location"])]

            plt.xticks(ticks=df.index, labels=xtick_labels, rotation=90, fontsize=20)
            plt.tight_layout()
            plt.title("Puntuación de opinión para cada archivo", fontsize=20)
            plt.xlabel("Archivo", fontsize=20)
            plt.ylabel("Puntuación de sentimiento", fontsize=20)
            plt.show()
        except Exception as e:
            print(f"Error al generar las gráficas: {e}")
