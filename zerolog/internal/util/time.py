# convert_offset takes a RFC3339 time string and
# changes the offset to Z if it's UTC.
def convert_offset(s: str) -> str:
    if s[-6:] == "+00:00":
        s = f"{s[0:-6]}Z"
    return s
