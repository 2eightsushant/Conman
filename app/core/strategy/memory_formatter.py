from datetime import datetime, timezone

class MemoryFormatter:
    def __init__(self, include_metadata: bool = True, readable_time: bool = True):
        self.include_metadata = include_metadata
        self.readable_time = readable_time

    def format(self, reranked_chunks: list, limit: int = 5) -> list[str]:
        formatted = []

        for i, (score, props, meta) in enumerate(reranked_chunks[:limit]):
            content = props.get("content", "")
            emotion = props.get("emotions", ["neutral"])
            emotion_str = ", ".join(emotion).capitalize()
            timestamps = props.get("timestamp", [])
            timestamp = max(timestamps) if isinstance(timestamps, list) and timestamps else None
            time_str = self._format_time(timestamp) if self.readable_time and timestamp else "Unknown time"

            prev_link = props.get("temporal_context", {}).get("prev_chunk_id")
            continuity_note = "Continues from earlier memory." if prev_link else ""

            importance = self._score_label(score)

            # Semantic-rich block
            memory_block = (
                f"Memory {i+1}:\n"
                f"- Importance: {importance}\n"
                f"- Emotion: {emotion_str}\n"
                f"- Time: {time_str}\n"
            )

            if continuity_note:
                memory_block += f"- Note: {continuity_note}\n"

            memory_block += f"- Content: {content.strip()}\n"

            formatted.append(memory_block.strip())

        return formatted

    def _format_time(self, timestamp):
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
        """Maps cognitive score into importance labels"""
        if score >= 0.85:
            return "Highly relevant"
        elif score >= 0.6:
            return "Relevant"
        elif score >= 0.4:
            return "Mildly relevant"
        else:
            return "Low relevance"