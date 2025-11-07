import re

from gimmegit import _version


fail_in_dev = {
    "condition": re.search(r"\.dev\d+$", _version.__version__),
    "reason": "Follow up before release",
    "strict": True,
}
