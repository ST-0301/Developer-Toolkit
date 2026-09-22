from datetime import datetime
from shared.database import get_connection

def log_usage(tool_name, action_name, total_duration_ms=None, preprocess_duration_ms=None, ai_duration_ms=None, postprocess_duration_ms=None, model_name=None, input_size=None, output_size=None, metadata=None):
    """Logs an action taken by a tool in the application."""
    conn = get_connection()
    
    conn.execute("""
        INSERT INTO ToolUsage
        (ToolName, ActionName, UsedAt, TotalDurationMs, PreprocessDurationMs, AiDurationMs, PostprocessDurationMs, ModelName, InputSize, OutputSize, Metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tool_name, 
        action_name, 
        datetime.now().isoformat(), 
        total_duration_ms,
        preprocess_duration_ms,
        ai_duration_ms,
        postprocess_duration_ms,
        model_name,
        input_size,
        output_size,
        metadata
    ))
    
    conn.commit()
    conn.close()