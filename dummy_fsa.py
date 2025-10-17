LABEL_CHAR = "@"
COMMENT_CHAR = "#"
START_CHAR = "!"
FINAL_CHAR = "*"

class FSA:
    """Stub FSA that accepts all strings"""
    def __init__(self, *args, **kwargs):
        pass
    def test(self, *args, **kwargs):
        return True
    def __str__(self):
        return "Stub FSA for UI prototype"
    def to_regex(self):
        return "Coming soon."