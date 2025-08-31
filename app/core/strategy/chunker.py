from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from weaviate.util import generate_uuid5
from datetime import datetime, timezone
from httpx import AsyncClient, HTTPError

from app.conn.clients import post_json
from app.shared.logger import get_logger

logger = get_logger(__name__)
emotion_url = "http://127.0.0.1:8082/emotion-score"

class DialogChunker:
    def __init__(self, window_size: int = 5, overlap: int = 1, chunk_size: int = 500):
        self.window_size = window_size
        self.overlap = overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=50
        )

    async def chunk(self, messages: List[Dict], http_client: AsyncClient) -> List[Dict]:
        if not messages:
            return []
        
        try:
            logger.info(f"Starting chunking for session {messages[0]['session_id']}")
            session_id = messages[0]['session_id']
            
            chunks: List[Dict] = []
            buffer: List = []
            counter = 0
            processed: List[Dict] = []
            
            for msg in messages:
                try:
                    if len(msg["content"]) > 500 and msg["role"] == "assistant":
                        logger.debug("long message, splitting...")
                        splits = self.splitter.split_text(msg["content"])
                        for split_text in splits:
                            new_msg = msg.copy()
                            new_msg["content"] = split_text
                            processed.append(new_msg)
                    else:
                        processed.append(msg)
                except Exception as e:
                    logger.warning(f"Splitting message failed due to {str(e)}")
                    continue

            for i, msg in enumerate(processed):
                buffer.append((counter, msg))
                time_span: List[float] = []

                if len(buffer) >= self.window_size or i == len(processed) - 1:
                    content = "\n".join([f"{b[1]['role'].capitalize()}: {b[1]['content']}" for b in buffer])
                    text = "\n".join([f"{b[1]['content']}" for b in buffer if b[1]['role'] == 'user'])
                    emotions = None
                    if text.strip():
                        try:
                            emotions = await post_json(http_client, emotion_url, {"text": text})
                        except HTTPError as he:
                            logger.error(f"Emotion API error: {str(he)}")
                        except Exception as e:
                            logger.error(f"Unexpected emotion fetch error: {str(e)}")

                    for k in range(1, len(buffer)):
                        prev_time = buffer[k-1][1]['message_created_at']
                        curr_time = buffer[k][1]['message_created_at']
                        diff = (curr_time-prev_time).total_seconds()
                        time_span.append(diff)

                    timestamps = [
                        ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
                        for ts in [b[1]["message_created_at"] for b in buffer]
                    ]
                    
                    metadata = {
                        "session_id": session_id,
                        "username": list(set(b[1]['name'] for b in buffer)),
                        "speakers": list(set(b[1]['role'] for b in buffer)),
                        "emotions": emotions['emotions'],
                        "temporal_context": {
                            "start_index": buffer[0][0] if buffer else -1,
                            "end_index": buffer[-1][0] if buffer else -1,
                            "session_position": [b[1]['session_position'] for b in buffer],
                            "message_indices": [b[0] for b in buffer],
                            "prev_chunk_id": chunks[-1]["id"] if chunks else None,
                            "time_span_seconds": time_span,
                        },
                        "timestamp": timestamps,
                    }

                    chunks.append({
                        "id": generate_uuid5(f"{session_id}_{buffer[0][0]}-{buffer[-1][0]}"),
                        "content": content,
                        "metadata": metadata
                    })

                    # Slide window
                    buffer = buffer[-self.overlap:] if self.overlap > 0 else []

                counter += 1

            logger.info(f"Generated {len(chunks)} chunks for session {session_id}")
            return chunks
        
        except Exception as e:
            sid = messages[0].get("session_id", "unknown") if messages else "unknown"
            logger.warning(f"Error generating chunks for session {sid}: {str(e)}")
            return []