import hanja
from hanja import hangul
import re

def clean_title(text):
    text = re.sub(r'<[^>]+>', '', text)  # HTML 태그 제거
    text = text.replace('\"', '').replace('\'', '')  # 따옴표 제거
    text = re.sub(r'[\[\]\(\)▶◀#$^&*[\]{}<>/|』◇◆▲△■□=·●]', '', text)  # 특수기호 및 특수문자 제거
    text = hanja.translate(text, 'substitution')  # 한자 변환
    return text.strip()

def clean_date(text):
    text = re.sub(r'<[^>]+>', '', text)  # HTML 태그 제거
    text = text.replace('\"', '').replace('\'', '')  # 따옴표 제거
    text = re.sub(r'(\d{4}-\d{2}-\d{2})\s.*', r'\1', text)  # 시간 제거
    return text.strip()

def clean_content(text):
    text = re.sub(r'<[^>]+>', '', text)  # HTML 태그 제거
    text = text.replace('\"', '').replace('\'', '')  # 따옴표 제거
    text = re.sub(r'[\[\]\(\)▶◀#$^&*[\]{}<>/|』◇◆▲△■□=·●]', '', text)  # 특수기호 및 특수문자 제거
    text = re.sub(r'\n+', ' ', text)    #줄바꿈 제거
    # 본문 내용 전용 처리
    text = re.sub(r'\S+@\S+', '', text)  # 이메일 주소 제거
    return text.strip()

def clean_company(text):
    text = re.sub(r'<[^>]+>', '', text)  # HTML 태그 제거
    text = text.replace('\"', '').replace('\'', '')  # 따옴표 제거
    return text.strip()