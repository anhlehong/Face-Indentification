import uuid
from dataclasses import dataclass, field
import numpy as np


@dataclass
class User:
    full_name: str
    embedding: np.ndarray
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
