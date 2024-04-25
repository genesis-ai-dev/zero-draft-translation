from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.vectordb.utils import get_logger
import hashlib
import os

from autogen.agentchat.contrib.vectordb.base import Document
from autogen.agentchat.contrib.vectordb.utils import get_logger
from autogen.retrieve_utils import (
    get_files_from_dir,
    split_files_to_chunks,
)

logger = get_logger(__name__)

HASH_LENGTH = int(os.environ.get("HASH_LENGTH", 8))

class CustomRetrieveUserProxyAgent(RetrieveUserProxyAgent):
    def _init_db(self):
        if not self._vector_db:
            return

        IS_TO_CHUNK = False  # whether to chunk the raw files
        if self._new_docs:
            IS_TO_CHUNK = True
        if not self._docs_path:
            try:
                self._vector_db.get_collection(self._collection_name)
                logger.warning(f"`docs_path` is not provided. Use the existing collection `{self._collection_name}`.")
                self._overwrite = False
                self._get_or_create = True
                IS_TO_CHUNK = False
            except ValueError:
                raise ValueError(
                    "`docs_path` is not provided. "
                    f"The collection `{self._collection_name}` doesn't exist either. "
                    "Please provide `docs_path` or create the collection first."
                )
        elif self._get_or_create and not self._overwrite:
            try:
                self._vector_db.get_collection(self._collection_name)
                logger.info(f"Use the existing collection `{self._collection_name}`.", color="green")
            except ValueError:
                IS_TO_CHUNK = True
        else:
            IS_TO_CHUNK = True
        
        self._vector_db.active_collection = self._vector_db.create_collection(
            self._collection_name, overwrite=self._overwrite, get_or_create=self._get_or_create
        )

        docs = None
        if IS_TO_CHUNK:
            if self.custom_text_split_function is not None:
                chunks, sources = split_files_to_chunks(
                    get_files_from_dir(self._docs_path, self._custom_text_types, self._recursive),
                    custom_text_split_function=self.custom_text_split_function,
                )
            else:
                chunks, sources = split_files_to_chunks(
                    get_files_from_dir(self._docs_path, self._custom_text_types, self._recursive),
                    self._max_tokens,
                    self._chunk_mode,
                    self._must_break_at_empty_line,
                )
            logger.info(f"Found {len(chunks)} chunks.")

            if self._new_docs:
                all_docs_ids = set(
                    [
                        doc["id"]
                        for doc in self._vector_db.get_docs_by_ids(ids=None, collection_name=self._collection_name)
                    ]
                )
            else:
                all_docs_ids = set()

            chunk_ids = [hashlib.blake2b(chunk.encode("utf-8")).hexdigest()[:HASH_LENGTH] for chunk in chunks]
            chunk_ids_set = set(chunk_ids)
            chunk_ids_set_idx = [chunk_ids.index(hash_value) for hash_value in chunk_ids_set]
            docs = [
                Document(id=chunk_ids[idx], content=chunks[idx], metadata=sources[idx])
                for idx in chunk_ids_set_idx
                if chunk_ids[idx] not in all_docs_ids
            ]
        BATCH_SIZE = 2048
        for start_idx in range(0, len(docs), BATCH_SIZE):
            end_idx = start_idx + BATCH_SIZE
            batch_docs = docs[start_idx:end_idx]
            self._vector_db.insert_docs(docs=batch_docs, collection_name=self._collection_name, upsert=True)
