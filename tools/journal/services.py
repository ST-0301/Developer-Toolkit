from shared.database import get_connection
from datetime import datetime

def split_into_chunks(text, max_chars=12000):
    lines = text.split('\n')
    chunks = []
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

def save_journal_to_db(filename, content):
    conn = get_connection()
    generated_at = datetime.now().isoformat()
    
    conn.execute(
        """
        INSERT INTO Journals (FileName, GeneratedAt, JournalContent)
        VALUES (?, ?, ?)
        """,
        (filename, generated_at, content)
    )
    conn.commit()
    conn.close()