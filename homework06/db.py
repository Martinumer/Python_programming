from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///news.db")
session = sessionmaker(bind=engine)


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    s = session()
    news_list = get_news('https://news.ycombinator.com/newest', n_pages=10)
    for i in range(len(news_list)):
        news = News(title=news_list[i]['title'], author=news_list[i]['author'], url=news_list[i]['url'], comments=news_list[i]['comments'], points=news_list[i]['points'])
        s.add(news)
        s.commit()