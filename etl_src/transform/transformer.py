import json
import uuid
from dataclasses import dataclass, field


@dataclass
class Genre:
    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Person:
    full_name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


class DataTransform:
    """
    Class to prepare extracted from PostgresQL data for loading into Elasticsearch indices
    """
    def __init__(self):
        pass

    def transform_data_genres(self, raw_data: list[Genre], batch_size: int, index_name: str):
        for row in raw_data:
            data = []
            item = {'_op_type': 'update', '_index': index_name,
                    'source': {
                        '_id': row['id'], 'name': row['name']}}
            data.append(item)
            json_data = json.dumps(item)
            yield json_data

    def transform_data_persons(self, raw_data: list[Person], batch_size: int, index_name: str):
        for row in raw_data:
            data = []
            item = {'_op_type': 'update', '_index': index_name,
                    'source': {
                        '_id': row['id'], 'full_name': row['full_name']}}
            data.append(item)
            json_data = json.dumps(item)
            yield json_data
