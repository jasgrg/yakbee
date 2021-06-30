from datetime import datetime, timezone

LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo
