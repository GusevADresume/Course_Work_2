import sqlalchemy


class Мemorizer():

    def __init__(self):
        self.database = ''
        self.engine = sqlalchemy.create_engine(self.database)
        self.connection = self.engine.connect()

    def find_previos_value(self, value) -> bool:
        return self.connection.execute(f"SELECT id FROM candidates WHERE vk_user_id = {value['id']}").fetchall()

    def add_to_common_list(self, value):
        name = "".join(c for c in value['first_name'] if c.isalpha())
        last = "".join(c for c in value['last_name'] if c.isalpha())
        self.connection.execute(
            f"INSERT INTO candidates(vk_user_id,vk_user_first_name,vk_user_last_name) Values('{value['id']}','{name}','{last}');")

    def add_to_whitelist(self, value):
        key = self.find_previos_value(value)[0][0]
        self.connection.execute(f"INSERT INTO whitelist(candidate_id,vk_user_id) Values('{key}','{value['id']}');")

    def add_to_blacklist(self, value):
        key = self.find_previos_value(value)[0][0]
        self.connection.execute(f"INSERT INTO blacklist(candidate_id,vk_user_id) Values('{key}','{value['id']}');")

