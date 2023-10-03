import smtplib
import ssl
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO

#turn the pdf into a bytes object
def bufferise(pdf):
    pdf_string = pdf.output(dest='S').encode()
    buf = BytesIO(pdf_string)
    return buf


#turn the Img into a bytes object
def bufferImg(plt):
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf


def createEmail(filepath, emailBody):
    #Preamble
    sender_email = "Stocks4Nev@outlook.com"
    receiver_email = "phillipmjefferies@gmail.com"
    message = MIMEMultipart("alternative")
    message["Subject"] = "kgmTest"
    message["From"] = sender_email
    message["To"] = receiver_email

    #Attach Text to Email body
    part1 = MIMEText(emailBody)
    message.attach(part1)

    # Attach the pdf to the msg going by e-mail
    with open(filepath, "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="pdf")
    attach.add_header('Content-Disposition', 'attachment', filename=str("Patterns.pdf"))
    message.attach(attach)

    #Hand MIME message to sender
    sendEmail(message, receiver_email)

def sendEmail(message,receiver_email):
    smtp_server = "smtp.outlook.com"
    port = 587  # For starttls
    sender_email = "Stocks4Nev@outlook.com"
    password = "MadeForNevvy"

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        #Send email
        server.sendmail(sender_email, [receiver_email], message.as_string())
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        #wrapup
        server.quit()