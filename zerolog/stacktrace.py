import re
import traceback
from typing import Any, Dict, List


# marshal_stack implements stack trace marshaling.
#
# zerolog.ExceptionStackMarshaler = marshal_stack
def marshal_stack(e: Exception) -> List[Dict[str, Any]]:
    stack = []
    for line in traceback.format_exception(e):
        if line.startswith("  File"):
            pattern = re.compile(
                r'"(?P<source>[^"]+)", line (?P<line>\d+), in (?P<func>\w+)'
            )
            match = pattern.search(line)
            if match:
                stack.append(match.groupdict())
    return stack
