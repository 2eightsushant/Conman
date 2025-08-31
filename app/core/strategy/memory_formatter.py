from datetime import datetime, timezone
from typing import List, Dict, Any


class MemoryFormatter:
    def __init__(self, readable_time: bool = True):
        self.readable_time = readable_time

    def format(self, reranked_chunks: List[tuple], limit: int = 5) -> List[Dict[str, Any]]:
        formatted = []

        for score, props, meta in reranked_chunks[:limit]:
            content = props.get("content", "").strip()
            if not content:
                continue

            timestamps = props.get("timestamp", [])
            timestamp = max(timestamps) if isinstance(timestamps, list) and timestamps else None
            time_str = self._format_time(timestamp) if timestamp and self.readable_time else "unknown time"

            formatted.append({
                "time": time_str,
                "content": content,
                "emotion": props.get("emotions", ["neutral"]),
                "importance": self._score_label(score),
                "continues_from": bool(props.get("temporal_context", {}).get("prev_chunk_id"))
            })

        return formatted

    def _format_time(self, timestamp: datetime) -> str:
        now = datetime.now(timezone.utc)
        diff = now - timestamp
        hours = diff.total_seconds() / 3600
        if hours < 1:
            return "just now"
        elif hours < 24:
            return f"{int(hours)} hour(s) ago"
        elif hours < 48:
            return "yesterday"
        else:
            return timestamp.strftime("%b %d, %Y")

    def _score_label(self, score: float) -> str:
        if score >= 0.85:
            return "Highly relevant"
        elif score >= 0.6:
            return "Relevant"
        elif score >= 0.4:
            return "Mildly relevant"
        else:
            return "Low relevance"