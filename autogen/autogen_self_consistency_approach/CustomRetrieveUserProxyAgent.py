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


PROMPT_DEFAULT = """You're a retrieve augmented chatbot. You answer user's questions based on your own knowledge and the
context provided by the user. You should follow the following steps to answer a question:
Step 1, you estimate the user's intent based on the question and context. The intent is a question answering task.
Step 2, you reply based on the intent.
You must provide your best answer given the context.

If user's intent is question answering, you must give as short an answer as possible.

User's question is: {input_question}

Context is: {input_context}

The source of the context is: {input_sources}

If you can answer the question, in the end of your answer, add the source of the context in the format of `Sources: source1, source2, ...`.
"""

PROMPT_CODE = """You're a retrieve augmented coding assistant. You answer user's questions based on your own knowledge and the
context provided by the user.
If you can't answer the question with or without the current context, you should reply exactly `UPDATE CONTEXT`.
For code generation, you must obey the following rules:
Rule 1. You MUST NOT install any packages because all the packages needed are already installed.
Rule 2. You must follow the formats below to write your code:
```language
# your code
```

User's question is: {input_question}

Context is: {input_context}
"""

PROMPT_QA = """You're a retrieve augmented chatbot. You answer user's questions based on your own knowledge and the
context provided by the user.
You must provide your best answer given the current context.
You must give as short an answer as possible.

User's question is: {input_question}

Context is: {input_context}
"""


class CustomRetrieveUserProxyAgent(RetrieveUserProxyAgent):
    # The entire function is copied from the parent class and the only change is the addition of inserting batches of 2048 chunks (end)
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

        # Feed small chunks of data in 2048 at a time (insert_docs limit)
        BATCH_SIZE = 2048
        for start_idx in range(0, len(docs), BATCH_SIZE):
            end_idx = start_idx + BATCH_SIZE
            batch_docs = docs[start_idx:end_idx]
            self._vector_db.insert_docs(docs=batch_docs, collection_name=self._collection_name, upsert=True)

    def _generate_message(self, doc_contents, task="default"):
        if not doc_contents:
            # print(colored("No more context, will terminate.", "green"), flush=True)
            return "TERMINATE"
        if self.customized_prompt:
            message = self.customized_prompt.format(input_question=self.problem, input_context=doc_contents)
        elif task.upper() == "CODE":
            message = PROMPT_CODE.format(input_question=self.problem, input_context=doc_contents)
        elif task.upper() == "QA":
            message = PROMPT_QA.format(input_question=self.problem, input_context=doc_contents)
        elif task.upper() == "DEFAULT":
            message = PROMPT_DEFAULT.format(
                input_question=self.problem, input_context=doc_contents, input_sources=self._current_docs_in_context
            )
        else:
            raise NotImplementedError(f"task {task} is not implemented.")
        return message