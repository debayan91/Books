from pdf2docx import Converter

inp = "/Users/debayan/Downloads/books/cloud.pdf"
out = "output.docx"

cv = Converter(inp)
cv.convert(out, start=0, end=None)
cv.close()