from shared.database import get_connection

def get_settings():
    conn = get_connection()
    cursor = conn.execute(
        "SELECT Prompt, OneDrivePath, FastModelName, FinalModelName FROM Settings LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()
    return row

def save_settings(prompt, onedrive_path, fast_model, final_model):
    conn = get_connection()
    conn.execute("DELETE FROM Settings")
    conn.execute(
        """
        INSERT INTO Settings
        (Prompt, OneDrivePath, FastModelName, FinalModelName)
        VALUES (?,?,?,?)
        """,
        (prompt, onedrive_path, fast_model, final_model)
    )
    conn.commit()
    conn.close()