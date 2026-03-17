from reportlab.pdfgen import canvas

def create_pdf(filename, pages, prefix):
    c = canvas.Canvas(filename)
    for i in range(1, pages + 1):
        c.drawString(100, 750, f"{prefix} - Page {i}")
        c.showPage()
    c.save()

create_pdf("test1.pdf", 10, "Document 1")
create_pdf("test2.pdf", 10, "Document 2")
