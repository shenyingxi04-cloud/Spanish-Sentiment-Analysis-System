# Spanish Sentiment Analysis & Intelligent Recommendation System

A web-based system for Spanish review sentiment analysis and personalized recommendation. It combines a pretrained multilingual BERT sentiment model, spaCy keyword extraction, user-similarity-based recommendation, and data visualization in a Flask web application.

Undergraduate graduation project, Soochow University (2025–2026).

---

## Features

- **Spanish sentiment analysis**: predicts a 1–5 star sentiment score for Spanish reviews using a pretrained multilingual BERT model
- **Keyword extraction**: extracts representative keywords from reviews with spaCy
- **Personalized recommendation**: combines sentiment results with user preferences and user similarity
- **Data visualization**: charts for sentiment distribution and recommendation results
- **User feedback storage**: stores feedback and history in SQLite
- **Web interface**: simple Flask-based interface for interaction

---

## Project Structure

```
.
|-- backend/      # Flask app, chart and file utilities
|-- frontend/     # HTML templates
|-- models/       # Sentiment analysis, keyword extraction, recommendation, database modules
|-- scripts/      # Data collection and cleaning scripts
|-- tests/        # Model evaluation scripts
|-- data/         # Sample datasets and database
`-- README.md
```

---

## Tech Stack

| Area | Tools |
| --- | --- |
| Backend | Python, Flask, SQLite |
| NLP | Hugging Face Transformers, [nlptown/bert-base-multilingual-uncased-sentiment](https://huggingface.co/nlptown/bert-base-multilingual-uncased-sentiment), spaCy |
| Data processing | Pandas, NumPy |
| Visualization | Matplotlib |
| Frontend | HTML, CSS, JavaScript (Flask templates) |

---

## Main Modules

| Module | File | Description |
| --- | --- | --- |
| Sentiment analysis | `models/sentiment_analyzer.py` | Predicts sentiment of Spanish text with multilingual BERT |
| Keyword extraction | `models/keyword_extractor.py` | Extracts keywords from reviews using spaCy |
| Recommendation engine | `models/recommendation_engine.py` | Generates recommendations from user preferences and similarity |
| Database management | `models/database_manager.py` | Stores user feedback and history in SQLite |
| Visualization | `models/plotter.py`, `backend/chart_utils.py` | Generates sentiment and recommendation charts |
| Data pipeline | `scripts/get_data.py`, `scripts/wash_data.py` | Collects and cleans review data |
| Evaluation | `tests/evaluate_model.py` | Evaluates sentiment model performance |

---

## Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/shenyingxi04-cloud/Spanish-Sentiment-Analysis-System.git
cd Spanish-Sentiment-Analysis-System
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Download the sentiment model**

Before the first run, open `models/model_local.py`, set `save_directory` to a local folder on your machine, then run:

```bash
python models/model_local.py
```

Make sure the model path used by the sentiment analysis module points to the same folder.

**4. Run the application**

```bash
python backend/app.py
```

---

## Future Improvements

- Fine-tune multilingual BERT on the project's own Spanish review data and compare with the pretrained baseline
- Replace hardcoded paths with configuration files
- Deploy the application online
- Improve recommendation accuracy
- Optimize UI/UX

---

## License

This project is released under the MIT License.
