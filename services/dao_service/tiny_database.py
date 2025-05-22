import threading

from tinydb import TinyDB
from tinydb.queries import QueryInstance
from tinydb.table import Document

from .query_builder import QueryBuilder as QB


class TinyDatabase:
    """Data Access Object for accessing and managing data in TinyDB."""

    def __init__(self, tables: dict[str, list[str]]) -> None:
        """Initialize the DAO with the database and table.

        Args:
            tables (dict[str, list[str]]): tables
        """
        db_locks = {}
        self.tables = {}
        for name, key in tables.items():
            db_locks[key[0]] = db_locks.get(key[0], threading.Lock())
            self.tables[name] = {
                "db_lock": db_locks[key[0]],
                "table": TinyDB(
                    key[0], ensure_ascii=False, indent=4, encoding="utf-8"
                ).table(name, cache_size=None),
                "key": key[1:],
            }

    def create_one(self, item: dict, table_name: str) -> int:
        """Create a unique document in the database.

        Args:
            item (dict[str, Any]): The item to be created.
            table_name (str): The table to query.
        Returns:
            The inserted document's ID.
        """
        with self.tables[table_name]["db_lock"]:
            return self.tables[table_name]["table"].insert(item)

    def upsert_one(self, item: dict, table_name: str) -> list[int]:
        """Insert or update a chunk of documents in the database.

        Args:
            item (dict[str, Any]): The item to be inserted or updated.
            table_name (str): The table to upsert into.
        Returns:
            List[int]: A list containing the updated document's IDs.
        """
        with self.tables[table_name]["db_lock"]:
            return self.tables[table_name]["table"].upsert(
                item, QB.query(item, self.tables[table_name]["key"])
            )

    def upsert_many(self, items: list[dict], table_name: str, chunk_size=1):
        """Insert or update a document in the database.

        Args:
            items (list[dict[str, Any]]): The items to be inserted or updated.
            table_name (str): The table to upsert into.
            chunk_size (int): The minimum size of the upserted items list
        """
        if len(items) < chunk_size:
            return

        with self.tables[table_name]["db_lock"]:
            while items:
                self.tables[table_name]["table"].upsert(
                    item := items.pop(), QB.query(item, self.tables[table_name]["key"])
                )

    def find_one(self, item_keys: dict, table_name: str) -> dict:
        """Retrieve a document by its keys.

        Args:
            item_keys (dict[str, Any]): The keys of the item.
            table_name (str): The table to find in.

        Returns:
            Optional[Dict[str, Any]]: The retrieved document or an empty dict if not found.
        """
        with self.tables[table_name]["db_lock"]:
            result: list[Document] = self.tables[table_name]["table"].search(
                QB.query(item_keys, self.tables[table_name]["key"])
            )
            return result[0] if result else {}

    def read_all(self, table_name: str) -> list[Document]:
        """Retrieve all documents from the database.

        Args:
            table_name (str): The table to read from.

        Returns:
            list[Document]: A list of all items.
        """
        with self.tables[table_name]["db_lock"]:
            return self.tables[table_name]["table"].all()

    def drop_all(self, table_name="") -> None:
        """Drop all data from table.
        Args:
            table_name (str): The table to drop.
        """
        with self.tables[table_name]["db_lock"]:
            self.tables[table_name]["table"].truncate()

    def search_by(self, query: QueryInstance, table_name: str) -> list[Document]:
        """Get all documents that match a given query.
        Args:
            query: (QueryInstance): The query to perform.
            table_name (str): The table to read from.
        Returns:
            list[Document]: A list of all the matching documents.
        """
        with self.tables[table_name]["db_lock"]:
            return self.tables[table_name]["table"].search(query)
