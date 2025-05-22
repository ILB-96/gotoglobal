from tinydb.queries import QueryInstance, Query


class QueryBuilder:
    """A utility class for building TinyDB query instances."""

    @staticmethod
    def query(item: dict, fields: list[str] | None = None, pos=True) -> QueryInstance:
        """Generate a query based on the provided item keys.

        Args:
            item (dict): The item to generate the query for.
            fields (list[str], optional): The fields to include in the query. Defaults to None.
            pos (bool, optional): If True, generate a positive query; if False, generate a negative query. Defaults to True.

        Returns:
            QueryInstance: The generated query instance.
        """
        if not fields:
            fields = list(item.keys())

        query = None
        for key in fields:
            q = Query()[key] == item[key] if pos else Query()[key] != item[key]
            if not query:
                query = q
            else:
                query = query & (q)

        return query if query else Query()

    @staticmethod
    def and_query(queries: list[QueryInstance]) -> QueryInstance:
        """Generate a query that combines multiple queries with an AND operation.

        Args:
            queries (list[QueryInstance]): A list of query instances to be combined.

        Returns:
            QueryInstance: A single query instance that represents the AND combination of all provided queries.
        """
        query = None
        for q in queries:
            if not query:
                query = q
            else:
                query = query & (q)

        return query if query else Query()

    @staticmethod
    def or_query(queries: list[QueryInstance]) -> QueryInstance:
        """Generate a query that combines multiple queries with an OR operation.

        Args:
            queries (list[QueryInstance]): A list of query instances to be combined.

        Returns:
            QueryInstance: A single query instance that represents the OR combination of all provided queries.
        """
        query = None
        for q in queries:
            if not query:
                query = q
            else:
                query = query | (q)

        return query if query else Query()
