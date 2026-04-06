from io import BytesIO

from pypdf import PdfReader

from app.utils.text import normalize_whitespace


class DocumentParsingError(Exception):
    pass


class DocumentParserService:
    SUPPORTED_EXTENSIONS = {".txt", ".pdf"}

    @staticmethod
    def get_extension(filename: str) -> str:
        if "." not in filename:
            return ""
        return "." + filename.rsplit(".", 1)[-1].lower()

    @classmethod
    def validate_extension(cls, filename: str) -> str:
        extension = cls.get_extension(filename)
        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise DocumentParsingError(
                f"Unsupported file type '{extension or 'unknown'}'. "
                f"Only .txt and .pdf are allowed in MVP."
            )
        return extension

    @staticmethod
    def parse_txt(file_bytes: bytes) -> str:
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = file_bytes.decode("latin-1")
            except Exception as exc:
                raise DocumentParsingError("Failed to decode TXT file.") from exc

        return normalize_whitespace(text)

    @staticmethod
    def parse_pdf(file_bytes: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(file_bytes))
            pages = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                pages.append(page_text)

            combined = "\n\n".join(pages)
            normalized = normalize_whitespace(combined)

            if not normalized:
                raise DocumentParsingError(
                    "PDF text extraction returned empty text. "
                    "This MVP does not support OCR-only scanned PDFs yet."
                )
            return normalized
        except DocumentParsingError:
            raise
        except Exception as exc:
            raise DocumentParsingError("Failed to parse PDF file.") from exc

    @classmethod
    def parse(cls, filename: str, file_bytes: bytes) -> tuple[str, str]:
        extension = cls.validate_extension(filename)

        if extension == ".txt":
            return "txt", cls.parse_txt(file_bytes)

        if extension == ".pdf":
            return "pdf", cls.parse_pdf(file_bytes)

        raise DocumentParsingError("Unsupported file type.")