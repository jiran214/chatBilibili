"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: embedding.py
 @DateTime: 2023/4/7 22:18
 @SoftWare: PyCharm
"""
from typing import List

import numpy as np
import tiktoken
from scipy import spatial

COST = {
    "gpt-3.5-turbo": 0.002/1000,
    "text-embedding-ada-002": 0.0004/1000,
}


def num_tokens_and_cost_from_string(text: str, model: str) -> (int, float):
    encoder = tiktoken.encoding_for_model(model)
    """Returns the number of tokens in a text string."""
    num_tokens = len(encoder.encode(text))
    cost = num_tokens * COST[model]
    return num_tokens, cost


def distances_from_embeddings(
    query_embedding: List[float],
    embeddings: List[List[float]],
    distance_metric="cosine",
) -> List[List]:
    """Return the distances between a query embedding and a list of embeddings."""
    distance_metrics = {
        "cosine": spatial.distance.cosine,
        "L1": spatial.distance.cityblock,
        "L2": spatial.distance.euclidean,
        "Linf": spatial.distance.chebyshev,
    }
    distances = [
        distance_metrics[distance_metric](query_embedding, embedding)
        for embedding in embeddings
    ]
    return distances


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))