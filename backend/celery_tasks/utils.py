import re
from bs4 import BeautifulSoup
from langchain_community.document_loaders import RecursiveUrlLoader
from dataclasses import dataclass


@dataclass
class DecisionMetadata:
    number: str
    proceeding: str
    date: str


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

def extract_text_from_url(url: str) -> str:
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
    
    return cleaned_text

def extract_metadata(text: str) -> DecisionMetadata:
    # Номер справи: 362/1318/13-ц
    case_number_match = re.search(r"(справа|категорія справи)?\s*№\s*(\d+/\d+/\d+(?:-[а-яґєіїА-ЯҐЄІЇ]+)?)", text, re.IGNORECASE)
    case_number = case_number_match.group(2) if case_number_match else None

    # Номер провадження: 2/362/87/14
    proceeding_number_match = re.search(r"(провадження)?\s*№\s*(\d+/\d+/\d+/\d+)", text, re.IGNORECASE)
    proceeding_number = proceeding_number_match.group(2) if proceeding_number_match else None

    # Дата рішення: 26.02.2014 або 26 лютого 2014 року
    date_match = re.search(
        r"(\d{2}\.\d{2}\.\d{4})|(\d{1,2}\s+[а-яґєії]+\s+20\d{2})", text, re.IGNORECASE
    )
    if date_match:
        if date_match.group(1):
            decision_date = date_match.group(1)
        else:
            decision_date = date_match.group(2)
    else:
        decision_date = None

    return DecisionMetadata(
        number=case_number,
        proceeding=proceeding_number,
        date=decision_date
    )
