class Row:
    def __init__(self, row_id: str, row_data: dict):
        self.row_id = row_id
        self.row_data = row_data

    def get_row_id(self) -> str:
        return self.row_id

    def get_row_data(self) -> dict:
        return self.row_data

    def set_row_data(self, new_data: dict):
        self.row_data = new_data