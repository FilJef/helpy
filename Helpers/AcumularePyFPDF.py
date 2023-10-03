from fpdf import FPDF
import datetime as DT

def createPDF():
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    for i in range(1, 41):
        pdf.cell(0, 10, 'Printing line number ' + str(i), 0, 1)
    pdf.output('tuto2.pdf', 'F')


#creates a table
def createTable(pdf, data):
    epw = pdf.w - 2 * pdf.l_margin
    th = pdf.font_size
    temp = len(data[0])
    col_width = epw / temp
    pdf.set_font('Arial', '', 12)

    for row in data:
        for datum in row:
            # Enter data in colums
            pdf.cell(col_width, 2 * th, str(datum), border=1)
        pdf.ln(2 * th)

    pdf.ln(th)
    return pdf


def sidebyside(pdf, data, img_loc):
    thirds = (pdf.w - 2 * pdf.l_margin) / 3
    th = pdf.font_size
    temp = len(data[0])
    col_width = thirds / temp
    pdf.set_font('Arial', 'B', 12)
    tempy = pdf.get_y()
    pdf.image(img_loc, x=pdf.get_x(), y=pdf.get_y(), w=2*thirds, type='png')
    print(2*int(thirds))
    pdf.set_xy(x=2*thirds + pdf.l_margin,y=tempy + 5)
    tempx = pdf.get_x()
    for row in data:
        for datum in row:
            # Enter data in colums
            pdf.cell(col_width -pdf.l_margin/2, 2 * th, str(datum), border=1)
        pdf.set_xy(tempx, pdf.get_y()+2*th)
        pdf.set_font('Arial', '', 8)

    pdf.set_font('Arial', '', 12)
    pdf.ln(th)
    return pdf


#sets up the header and footer
class PDF(FPDF):
    ticker = "Test"
    def set_ticker(self, ticker):
        self.ticker = ticker

    #Page Header
    def header(self):
        today = str(DT.date.today())
        self.line(self.l_margin, 25, self.w-self.l_margin, 25)
        # Logo
        self.image('Logo.jpeg', 10, 5, 30)
        # Arial bold 15
        self.set_font('Arial', 'I', 15)
        # Move to the right
        # Title
        self.set_y(7)
        self.set_x(150)
        self.cell(50, 5, f'{self.ticker} Daily Report', 0, align ='R')
        self.set_y(12)
        self.set_x(150)
        self.cell(50, 5, f'Date: {today}', 0, align ='R')
        # Line break
        self.ln(15)
        self.set_font('Arial', '', 12)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')
        self.set_fill_color(159)
        self.set_font('Arial', '', 12)
