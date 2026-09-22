import streamlit as st
from tools.analytics.services import get_summary_metrics, get_tool_metrics, get_daily_usage_last_7_days, get_recent_activity

def render_dashboard():
    # Load Data
    metrics = get_summary_metrics()
    tool_metrics = get_tool_metrics()
    daily_usage = get_daily_usage_last_7_days()
    recent_activity = get_recent_activity(limit=8)

    # --- ROW 1: Top Metrics ---
    st.markdown("### 📊 Overview & Performance")
    m1, m2, m3, m4, m5 = st.columns(5)
    
    m1.metric("Uses Today", metrics["Today"] or 0)
    m2.metric("Uses This Week", metrics["ThisWeek"] or 0)
    m3.metric("Total Uses", metrics["Total"] or 0)
    
    # Format the averages safely (handle None/NaN if DB is empty)
    avg_wait = (metrics.get("AvgTotalDurationMs") or 0) / 1000
    avg_ai = (metrics.get("AvgAiDurationMs") or 0) / 1000
    
    m4.metric("Avg Wait Time", f"{avg_wait:.2f} s")
    m5.metric("Avg AI Execution", f"{avg_ai:.2f} s")
    
    st.write("")

    # --- ROW 2: Charts & Tool Averages ---
    c1, c2 = st.columns([1.5, 2])
    
    with c1:
        st.markdown("**Daily Activity (Last 7 Days)**")
        if not daily_usage.empty:
            st.bar_chart(daily_usage, y="Count", color="#4CAF50", height=250)
        else:
            st.info("Not enough data to display chart yet.")

    with c2:
        st.markdown("**Tool Popularity & Speed**")
        if not tool_metrics.empty:
            # Highlight max values in the speed columns for quick visual identification
            st.dataframe(
                tool_metrics.style.highlight_max(subset=['Avg Wait (s)', 'Avg AI (s)'], color='#5c2a2a'), 
                use_container_width=True, 
                hide_index=True, 
                height=250
            )
        else:
            st.info("No tool usage recorded.")

    st.write("")

    # --- ROW 3: Recent Activity Log ---
    st.markdown("**Recent Activity Logs**")
    if not recent_activity.empty:
        # Fill NaN values with empty strings for clean UI presentation (e.g., Formatter has no AI/Model data)
        clean_activity = recent_activity.fillna("")
        st.dataframe(clean_activity, use_container_width=True, hide_index=True)
    else:
        st.info("Your recent tool actions will appear here.")