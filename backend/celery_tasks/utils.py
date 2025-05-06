import re
from bs4 import BeautifulSoup
from langchain_community.document_loaders import RecursiveUrlLoader
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.app_config import AppConfig
from typing import Any, Dict, List, Optional


@dataclass
class DecisionMetadata:
    number: str
    proceeding: str
    #date: str


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
    # Универсальное регулярное выражение
    pattern = r"(?:Категорія справи|Справа)?\s*№?\s*([\dа-яА-Я\-]+(?:/[\dа-яА-Я\-]+)+)"
    # Ищем все подходящие номера в тексте
    case_numbers = re.findall(pattern, text, flags=re.IGNORECASE)
    # Выбираем первый номер (если важно только один)
    case_number = case_numbers[0] if case_numbers else "unspecified"


    # Номер провадження
    proceeding_number_match = re.search(r"(провадження)?\s*№\s*(\d+/\d+/\d+/\d+)", text, re.IGNORECASE)
    proceeding_number = proceeding_number_match.group(2) if proceeding_number_match else "unspecified"

    # # Дата рішення: 26.02.2014 або 26 лютого 2014 року
    # date_match = re.search(
    #     r"(\d{2}\.\d{2}\.\d{4})|(\d{1,2}\s+[а-яґєії]+\s+20\d{2})", text, re.IGNORECASE
    # )
    # if date_match:
    #     if date_match.group(1):
    #         decision_date = date_match.group(1)
    #     else:
    #         decision_date = date_match.group(2)
    # else:
    #     decision_date = "unspecified"

    return DecisionMetadata(
        number=case_number,
        proceeding=proceeding_number,
        # date=decision_date
    )

def split_text_into_chunks(text: str, decision_id: str, decision_metadata: DecisionMetadata) -> List[Document]:
    """Разделение текста на чанки с сохранением метаданных."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=AppConfig.MAX_CHUNK_SIZE,
        chunk_overlap=AppConfig.CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )

    documents = [
        Document(
            page_content=chunk,
            metadata={
                "document_id": decision_id,
                "decision_number": decision_metadata.number,
            },
        )
        for chunk in text_splitter.split_text(text)
    ]

    return documents
    # import logging
    # logger = logging.getLogger(__name__)
    #logger.info(documents)
    # with open("chunks_debug.txt", "w", encoding="utf-8") as f:
    #     for chunk in chunks:
    #         f.write(f"{chunk.page_content}\n{chunk.metadata}\n\n")

