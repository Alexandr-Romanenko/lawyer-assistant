import re

from bs4 import BeautifulSoup
from langchain_community.document_loaders import RecursiveUrlLoader

from celery_tasks.utils import extract_metadata


def clean_text(text: str) -> str:
    """
    Очистка текста решения от мусора.
    """
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = text.replace('\u00A0', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r"^.*?Повний доступ\s*", "", text, flags=re.DOTALL)
    text = re.sub(r"\s*Логін: Для помилки:.*Зачекайте, будь ласка\.\.\..*$", "", text, flags=re.DOTALL)
    return text.strip()

def extract_text_from_url(url: str):
    """
    Загружает и извлекает текст со страницы по указанному URL.
    """
    def bs4_extractor(html: str) -> str:
        soup = BeautifulSoup(html, "lxml")
        return re.sub(r"\n\n+", "\n\n", soup.text).strip()
    loader = RecursiveUrlLoader(url, extractor=bs4_extractor)
    docs = loader.load()
    script_text = docs[0].page_content
    cleaned_text = clean_text(script_text)

    metadata = extract_metadata(cleaned_text)
    print(metadata)
    return metadata


extract_text_from_url("https://reyestr.court.gov.ua/Review/49586520")

