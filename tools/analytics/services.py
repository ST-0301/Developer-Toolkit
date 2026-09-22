from shared.database import get_connection
import pandas as pd

def get_summary_metrics():
    conn = get_connection()
    query = """
    SELECT 
        COUNT(*) as Total,
        SUM(CASE WHEN date(UsedAt) = date('now', 'localtime') THEN 1 ELSE 0 END) as Today,
        SUM(CASE WHEN date(UsedAt) >= date('now', '-7 days', 'localtime') THEN 1 ELSE 0 END) as ThisWeek,
        SUM(CASE WHEN date(UsedAt) >= date('now', '-30 days', 'localtime') THEN 1 ELSE 0 END) as ThisMonth,
        AVG(TotalDurationMs) as AvgTotalDurationMs,
        AVG(AiDurationMs) as AvgAiDurationMs
    FROM ToolUsage
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.iloc[0] if not df.empty else {"Total": 0, "Today": 0, "ThisWeek": 0, "ThisMonth": 0, "AvgTotalDurationMs": 0, "AvgAiDurationMs": 0}

def get_tool_metrics():
    """Replaces get_tool_distribution to include speed metrics."""
    conn = get_connection()
    query = """
    SELECT 
        ToolName as Tool, 
        COUNT(*) as Uses,
        ROUND(AVG(TotalDurationMs) / 1000.0, 2) as 'Avg Wait (s)',
        ROUND(AVG(AiDurationMs) / 1000.0, 2) as 'Avg AI (s)'
    FROM ToolUsage 
    GROUP BY ToolName
    ORDER BY Uses DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_daily_usage_last_7_days():
    conn = get_connection()
    query = """
    SELECT date(UsedAt) as Date, COUNT(*) as Count 
    FROM ToolUsage 
    WHERE date(UsedAt) >= date('now', '-7 days', 'localtime')
    GROUP BY date(UsedAt)
    ORDER BY date(UsedAt) ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    if not df.empty:
        df = df.set_index('Date')
    return df

def get_recent_activity(limit=10):
    """Updated to pull performance and model data."""
    conn = get_connection()
    query = f"""
    SELECT 
        time(UsedAt) as Time, 
        ToolName as Tool, 
        ActionName as Action,
        ROUND(TotalDurationMs / 1000.0, 2) as 'Total (s)',
        ROUND(AiDurationMs / 1000.0, 2) as 'AI (s)',
        ModelName as Model
    FROM ToolUsage 
    ORDER BY UsedAt DESC 
    LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df