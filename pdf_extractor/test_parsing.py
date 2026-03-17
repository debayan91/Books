from pdf_utils import parse_ranges

tests = [
    ("1-5,8,10-12", 20, [0, 1, 2, 3, 4, 7, 9, 10, 11]),
    ("  2 - 4 , 6", 10, [1, 2, 3, 5]),
    ("", 5, [0, 1, 2, 3, 4]),
    ("15", 10, []), # out of bounds
    ("8-15", 10, [7, 8, 9]) # constrained
]

for t in tests:
    res = parse_ranges(t[0], t[1])
    assert res == t[2], f"Failed {t}: got {res}"
print("All parsing tests passed!")
