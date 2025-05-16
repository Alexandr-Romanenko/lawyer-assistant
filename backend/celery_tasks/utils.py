import os
import re

from bs4 import BeautifulSoup
from langchain_community.document_loaders import RecursiveUrlLoader
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from email.message import EmailMessage

from config.app_config import AppConfig
from user.models import User

from dotenv import load_dotenv
load_dotenv()


@dataclass
class DecisionMetadata:
    number: str
    proceeding: str


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

def get_email_template_user_verification(user_id: int, verification_code: str):

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist as e:
        raise ValueError(f"User with id={user_id} does not exist") from e

    email = EmailMessage()
    email['Subject'] = 'Verification link'
    email['From'] = os.getenv('SMTP_USER')
    email['To'] = user.email

    email.set_content(
        '<div>'
        f'<h1 style="color: red;">Hello, {user.first_name} {user.second_name}, please use code </h1>'
        f'http://{AppConfig.DOMAIN_NAME}/user/verify/{verification_code}'
        '</div>',
        subtype='html'
    )
    return email

def get_smtp_config():
    config = {
        "host": os.getenv("SMTP_HOST"),
        "port": int(os.getenv("SMTP_PORT", "465")),
        "user": os.getenv("SMTP_USER"),
        "password": os.getenv("SMTP_PASSWORD"),
    }
    if not all(config.values()):
        raise ValueError("Incomplete SMTP configuration")
    return config
