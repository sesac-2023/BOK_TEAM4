'''
#코드 실행 시 참고사항
[50번째 줄] data_processor = DataPreprocessing('./news_temp.csv') <<< './news_temp.csv' 부분에 전처리 진행할 파일 경로 설정
[53번째 줄] preprocessed_data.to_csv('./save_preprocessing.csv') <<< 전처리 완료된 결과를 저장할 csv 파일명과 저장 경로 설정
[22번째 줄] self.df = self.df.dropna() # nan/none값 제거(네이버뉴스는 데이터 클렌징 할 때 처리했으므로 이 줄 삭제, 의사록/채권보고서는 아직 논의 못함)
'''

import pandas as pd
from ekonlpy.tag import Mecab

class DataPreprocessing:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.mecab = Mecab()
        self.stopPos = ['NNP', 'NNB', 'NNBC', 'NR', 'NP',
                        'VX', 'VCP', 'MM', 'MAJ', 'IC', 'JKS',
                        'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ',
                        'JX', 'JC', 'EP', 'EF', 'EC', 'ETN', 'ETM',
                        'XPN', 'XSN', 'XSV', 'XSA', 'XR', 'SF', 'SE',
                        'SSO', 'SSCSY', 'SSC', 'SC', 'SY', 'SN']
    
    def making_df(self):
        self.df = self.df.dropna()
        data = self.df.groupby('date').agg({'title': '/'.join, 'contents': '/'.join}).reset_index()
        melted_data = pd.melt(data, id_vars=['date'], value_vars=['title', 'contents'], var_name='column', value_name='title_contents')
        data = melted_data.groupby('date')['title_contents'].agg('/'.join).reset_index()
        return data
    
    def pos_tag(self, text):
        return self.mecab.pos(text)
    
    def rm_stopPos(self, text):
        return [word for word in text if word[1] not in self.stopPos]
    
    def synonyms(self, text):
        return self.mecab.replace_synonyms(text)
    
    def lemmas(self, text):
        return self.mecab.lemmatize(text)

    def preprocess_data(self):
        total_news = self.making_df()
        total_news = total_news.assign(pos_tagging="")
        total_news['pos_tagging'] = total_news['title_contents'].apply(self.pos_tag)
        total_news['remove_stopPos'] = total_news['pos_tagging'].apply(self.rm_stopPos)
        total_news['synonyms'] = total_news['remove_stopPos'].apply(self.synonyms)
        total_news['lemmas'] = total_news['synonyms'].apply(self.lemmas)
        return total_news[['date', 'lemmas']]
    
    print("전처리 진행중")
        

data_processor = DataPreprocessing('./news_temp.csv')
preprocessed_data = data_processor.preprocess_data()

preprocessed_data.to_csv('./save_preprocessing.csv')
print("전처리 완료")