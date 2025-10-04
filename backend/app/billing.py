import pathway as pw

# A simple in-memory store for usage data
usage_data = {
    "questions_asked": 0,
    "reports_generated": 0,
}

def record_usage(event_type: str, credits: int):
    """Records usage events and associated credits."""
    if event_type in usage_data:
        usage_data[event_type] += credits
    else:
        print(f"Unknown event type: {event_type}")

def get_usage_data():
    """Returns the current usage data."""
    return usage_data
