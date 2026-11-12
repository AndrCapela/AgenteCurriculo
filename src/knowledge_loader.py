import logging
from pathlib import Path
from typing import Dict, Tuple
import pypdf

from src.config import KNOWLEDGE_DIR

logger = logging.getLogger(__name__)

class KnowledgeLoader:
    """
    Carrega e gerencia dinamicamente arquivos da base de conhecimento (PDF, Markdown, Texto).
    Detecta automaticamente novos arquivos adicionados ou excluídos da pasta data/knowledge/.
    """

    def __init__(self, knowledge_dir: Path = KNOWLEDGE_DIR):
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self._cached_content: str = ""
        self._cached_file_mtimes: Dict[str, float] = {}

    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extrai texto de um arquivo PDF usando pypdf."""
        try:
            reader = pypdf.PdfReader(str(file_path))
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    pages_text.append(f"[Página {i+1}]\n{text.strip()}")
            return "\n\n".join(pages_text)
        except Exception as e:
            logger.error(f"Erro ao extrair PDF {file_path.name}: {e}")
            return f"[Erro ao ler arquivo {file_path.name}: {e}]"

    def _extract_text_file(self, file_path: Path) -> str:
        """Lê arquivo de texto ou markdown com codificação UTF-8."""
        try:
            return file_path.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            try:
                return file_path.read_text(encoding="latin-1").strip()
            except Exception as e:
                logger.error(f"Erro ao ler texto de {file_path.name}: {e}")
                return f"[Erro ao ler arquivo {file_path.name}: {e}]"
        except Exception as e:
            logger.error(f"Erro ao ler texto de {file_path.name}: {e}")
            return f"[Erro ao ler arquivo {file_path.name}: {e}]"

    def get_current_files(self) -> Dict[str, float]:
        """Retorna os arquivos suportados e seus timestamps de modificação."""
        supported_extensions = {".pdf", ".md", ".txt"}
        files_state = {}
        if not self.knowledge_dir.exists():
            return files_state

        for file_path in self.knowledge_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    files_state[str(file_path)] = file_path.stat().st_mtime
                except OSError:
                    pass
        return files_state

    def load_knowledge(self, force_reload: bool = False) -> str:
        """
        Carrega todo o conhecimento disponível. Se nenhum arquivo tiver sido modificado,
        retorna o cache em memória para máxima performance.
        """
        current_files = self.get_current_files()

        # Verifica se houve alteração (arquivos novos, excluídos ou modificados)
        if not force_reload and self._cached_content and current_files == self._cached_file_mtimes:
            return self._cached_content

        if not current_files:
            self._cached_content = "Nenhum documento encontrado na base de conhecimento."
            self._cached_file_mtimes = {}
            return self._cached_content

        sections = []
        for file_str in sorted(current_files.keys()):
            file_path = Path(file_str)
            ext = file_path.suffix.lower()

            if ext == ".pdf":
                content = self._extract_pdf_text(file_path)
            elif ext in {".md", ".txt"}:
                content = self._extract_text_file(file_path)
            else:
                continue

            if content:
                relative_path = file_path.relative_to(self.knowledge_dir)
                section = (
                    f"==================================================\n"
                    f"DOCUMENTO: {relative_path}\n"
                    f"==================================================\n"
                    f"{content}\n"
                )
                sections.append(section)

        self._cached_content = "\n\n".join(sections)
        self._cached_file_mtimes = current_files
        logger.info(f"Base de conhecimento atualizada com {len(sections)} arquivo(s).")
        return self._cached_content

    def get_summary(self) -> Tuple[int, int]:
        """Retorna (quantidade de arquivos carregados, total aproximado de palavras)."""
        content = self.load_knowledge()
        total_files = len(self._cached_file_mtimes)
        total_words = len(content.split())
        return total_files, total_words

# Instância padrão para uso no projeto
knowledge_loader = KnowledgeLoader()
