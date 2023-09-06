'''
#코드 실행 시 참고사항
[51번째 줄] data_processor = DataPreprocessing('./news_temp.csv') <<< './news_temp.csv' 부분에 전처리 진행할 파일 경로 설정
[54번째 줄] preprocessed_data.to_csv('./save_preprocessing.csv') <<< 전처리 완료된 결과를 저장할 csv 파일명과 저장 경로 설정
'''

import pandas as pd
from ekonlpy.tag import Mecab

class DataPreprocessing:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path, index_col=0)
        self.mecab = Mecab()
        self.stopPos = ['NNP', 'NNB', 'NNBC', 'NR', 'NP',
                        'VX', 'VCP', 'MM', 'MAJ', 'IC', 'JKS',
                        'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ',
                        'JX', 'JC', 'EP', 'EF', 'EC', 'ETN', 'ETM',
                        'XPN', 'XSN', 'XSV', 'XSA', 'XR', 'SF', 'SE',
                        'SSO', 'SSCSY', 'SSC', 'SC', 'SY', 'SN']
    
    def making_df(self):
        df = self.df.assign(pos_tagging="")
        return df
    
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