from datetime import datetime, timezone
import math

LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo


def get_next_calc_time(epoch, granularity):

    nsecs = epoch + granularity

    new_epoch = math.floor(nsecs / granularity) * granularity

    return new_epoch