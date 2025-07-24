from datetime import datetime, timedelta
import numpy as np

def apply_memory_effects(response: dict, context: dict) -> dict:
    """Applies memory decay, emotional bias, primacy/recency effects"""
    # Primacy / Recency Bias
    if response['top_chunks']:
        response['top_chunks'][0]['cognitive_score'] *= 1.2  # Primacy
        response['top_chunks'][-1]['cognitive_score'] *= 1.1  # Recency

    # Emotional bias amplification
    for chunk in response['top_chunks']:
        if 'negative' in chunk.get('explanation', {}).get('emotional', []):
            chunk['content'] = intensify_language(chunk['content'])

    # Fading memories in emotion groups
    for group in response.get('emotion_groups', {}).values():
        for memory in group:
            ts = memory.get('timestamp')
            if ts and isinstance(ts, datetime) and (datetime.now() - ts) > timedelta(days=7):
                memory['content'] = fade_memory_details(memory['content'])

    # Add memory characteristics
    response['memory_characteristics'] = {
        "vividness": calculate_vividness(response['top_chunks']),
        "coherence": calculate_temporal_coherence(response.get('emotion_groups', {})),
        "emotional_valence": calculate_emotional_valence(response.get('top_chunks', []))
    }

    return response


def fade_memory_details(content: str) -> str:
    """Simulate vague or fuzzy memory over time"""
    return content[:int(len(content)*0.6)] + " [...]"

def intensify_language(text: str) -> str:
    """Simulate stronger negative recall"""
    return text.upper() if len(text) < 100 else text + "!!!"

def calculate_vividness(chunks: list) -> float:
    return sum(
        min(1, len(c['content'])/500) *
        (1.5 if 'excitement' in c.get('explanation', {}).get('emotional', []) else 1)
        for c in chunks
    ) / max(1, len(chunks))

def calculate_temporal_coherence(groups: dict) -> float:
    # Placeholder for improved chain-based scoring
    return float(len(groups)) / 10.0  # e.g., more emotions = more fragmentation

def calculate_emotional_valence(chunks: list) -> float:
    def e_intensity(emotion):
        return {"positive": 1, "neutral": 0.5, "negative": -1}.get(emotion, 0)
    
    emotions = [e for c in chunks for e in c.get('explanation', {}).get('emotional', [])]
    return np.mean([e_intensity(e) for e in emotions]) if emotions else 0.0