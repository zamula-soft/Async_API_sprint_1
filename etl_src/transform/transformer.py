import json
import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Genres:
    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Persons:
    full_name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


class DataTransform:
    def __init__(self):
        self.index_name = 'genres'

    def transform_data_genres(self, raw_data: Genres, batch_size: int):
        for row in raw_data:
            data = []
            item = {'_op_type': 'update', '_index': self.index_name,
                    'source': {
                        '_id': row['id'], 'name': row['name']}}
            data.append(item)
            json_data = json.dumps(item)
            yield json_data

    def transform_data_persons(self, raw_data: Persons, batch_size: int):
        for row in raw_data:
            data = []
            item = {'_op_type': 'update', '_index': self.index_name,
                    'source': {
                        '_id': row['id'], 'full_name': row['full_name']}}
            data.append(item)
            json_data = json.dumps(item)
            yield json_data
