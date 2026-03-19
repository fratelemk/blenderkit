import re

PATTERN = re.compile(
    r"""
    ^(?P<time>\d{2}:\d{2}\.\d{3})\s+
    render\s+\|\s+
    Fra:\s+(?P<frame>\d+)\s+\|\s+
    Remaining:\s+(?P<remaining>\d+:\d{2}\.\d{2})\s+\|\s+
    Mem:\s+(?P<memory>\d+)M\s+\|\s+
    Sample\s+(?P<sample>\d+)/(?P<total>\d+)
    """,
    re.VERBOSE,
)

def parse(line):
    match = PATTERN.match(line)
    if not match:
        return None

    data = match.groupdict()
    data["frame"] = int(data["frame"])
    data["sample"] = int(data["sample"])
    data["total"] = int(data["total"])
    data["memory_MB"] = int(data.pop("memory"))

    return data

with open("render.test.log", "r") as f:
    entries = [parse(line) for line in f if parse(line)]
    for e in entries:
        print(e)
