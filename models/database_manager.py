import pyodbc

class DatabaseManager:
    def __init__(self, db_conn_string):
        self.db_conn = pyodbc.connect(db_conn_string)
        print("Database connected successfully!")
        self.create_tables()
        self.add_id_column_to_feedback()

    def create_tables(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='feedback' AND xtype='U')
            CREATE TABLE feedback (
                id INT IDENTITY(1,1) PRIMARY KEY,
                username NVARCHAR(255),
                content NVARCHAR(MAX),
                sentiment NVARCHAR(255),
                score FLOAT,
                keywords NVARCHAR(255),
                place NVARCHAR(255),
                location NVARCHAR(255),
                label NVARCHAR(255),
                hotel NVARCHAR(255)
            )
        ''')
        # 创建酒店表，用于存储酒店的基本信息
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='hotels' AND xtype='U')
            CREATE TABLE hotels (
                id INT IDENTITY(1,1) PRIMARY KEY,
                hotel NVARCHAR(255),  -- 酒店名称
                location NVARCHAR(255),  -- 酒店所在位置
                label NVARCHAR(255)  -- 酒店的类别标签，如星级等
            )
        ''')

        # 创建电影反馈表，专门用于存储电影相关的用户反馈信息
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='movie_feedback' AND xtype='U')
            CREATE TABLE movie_feedback (
                id INT IDENTITY(1,1) PRIMARY KEY,
                username NVARCHAR(255),  -- 提供反馈的用户姓名
                review_text NVARCHAR(MAX),  -- 电影评论的具体内容
                review_rate FLOAT,  -- 用户对电影的评分
                film_name NVARCHAR(255),  -- 电影名称
                gender NVARCHAR(255),  -- 推测可能是电影的性别受众倾向，可根据实际修改
                sentiment NVARCHAR(255),  -- 评论的情感倾向，如积极、消极、中性
                score FLOAT,  -- 情感分析得出的分数
                keywords NVARCHAR(MAX)  -- 从评论中提取的关键词
            )
        ''')

        # 创建电影表，用于存储电影的基本信息
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='movies' AND xtype='U')
            CREATE TABLE movies (
                id INT IDENTITY(1,1) PRIMARY KEY,
                movie NVARCHAR(255),  -- 电影名称
                gender NVARCHAR(255),  -- 电影的类别，如动作、喜剧等
                ave_rate FLOAT  -- 电影的平均评分
            )
        ''')

        self.db_conn.commit()

    def add_id_column_to_feedback(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS
                           WHERE TABLE_NAME = 'feedback' AND COLUMN_NAME = 'id')
            ALTER TABLE feedback ADD id INT IDENTITY(1,1) PRIMARY KEY
        ''')
        self.db_conn.commit()

    def store_feedback(self, user, content, sentiment, score, keywords, place="", location="", label="", hotel=""):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE content = ? AND hotel = ?", (content, hotel))
        count = cursor.fetchone()[0]
        if count > 0:
            #print(f"评论内容已存在，跳过插入：{content}，酒店：{hotel}")
            return

        max_length = 255
        truncated_location = self.truncate_string(location, max_length)
        try:
            cursor.execute('''INSERT INTO feedback (username, content, sentiment, score, keywords, place, location, label, hotel)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (user, content, sentiment, score, keywords, place, truncated_location, str(label), hotel))
            self.db_conn.commit()
            #print(f"已插入评论：{content}，关联位置：{location}，酒店：{hotel}")
        except Exception as e:
            print(f"插入评论时出现错误：{e}")

    def store_hotel_info(self, hotel, location, label):
        max_length = 255
        truncated_location = self.truncate_string(location, max_length)
        cursor = self.db_conn.cursor()
        cursor.execute('''INSERT INTO hotels (hotel, location, label) VALUES (?, ?, ?)''',
                       (hotel, truncated_location, str(label)))
        self.db_conn.commit()
        #print(f"已插入酒店信息：{hotel}，关联位置：{location}")

    def store_movie_feedback(self, user, review, sentiment, score, keywords, film_name, gender):
        # 修改此处，直接使用 self.db_conn.cursor()
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM movie_feedback WHERE review_text = ? AND film_name = ?", (review, film_name))
        count = cursor.fetchone()[0]
        if count > 0:
            # print(f"评论内容已存在，跳过插入：{review}，电影：{film_name}")
            return

        try:
            cursor.execute('''INSERT INTO movie_feedback (username, review_text, sentiment, score, keywords, film_name, gender)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (user, review, sentiment, score, keywords, film_name, gender))
            # 修改此处，直接使用 self.db_conn.commit()
            self.db_conn.commit()
            # print(f"已插入电影评论：{review}，电影名称：{film_name}")
        except Exception as e:
            print(f"插入电影评论时出现错误：{e}")

    def store_movie_info(self, film_name, gender):
        # 修改此处，直接使用 self.db_conn.cursor()
        cursor = self.db_conn.cursor()
        cursor.execute('''INSERT INTO movies (movie, gender) VALUES (?, ?)''',
                       (film_name, gender))
        # 修改此处，直接使用 self.db_conn.commit()
        self.db_conn.commit()
        # print(f"已插入电影信息：{film_name}，类别：{gender}")
    def truncate_string(self, s, max_length):
        return s[:max_length] if len(s) > max_length else s

    def remove_duplicate_feedback(self):
        cursor = self.db_conn.cursor()
        query = """
            WITH CTE AS (
                SELECT 
                    id,
                    ROW_NUMBER() OVER (PARTITION BY content, hotel ORDER BY id) as rn
                FROM 
                    feedback
            )
            DELETE FROM CTE WHERE rn > 1;
        """
        cursor.execute(query)
        self.db_conn.commit()
        print("重复的反馈记录已删除。")