import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

import os

# read log for if price dropped
with open("log.txt", "r") as text_file:
    log = text_file.read()

if log.startswith("T"):
    drop_count = log.replace("T", "").replace(",", "")
    title = drop_count + " item(s) are on sale!"
else:
    title = "No Price Drop"

os.remove("log.txt")

# user config
sender_email = "price.report.zys@gmail.com"
receiver_email = sender_email

with open("email.txt", "r") as text_file:
    custome_mail = text_file.read()

if "@" in custome_mail:
    receiver_email = custome_mail.strip()

password = "PriceReportPython"

print("sending email")

html = """
<html>
 <body>
   <img src="cid:Mailtrapimage" width="750">
 </body>
</html>
"""

message = MIMEMultipart("alternative")
message['To'] = formataddr(("PriceReport", receiver_email))
message['From'] = formataddr(("PriceReport", sender_email))
message['Subject'] = title

part = MIMEText(html, "html")
message.attach(part)

with open('price_report_newest.jpg', "rb") as attachment:
    image = MIMEImage(attachment.read())

image.add_header('Content-ID', '<Mailtrapimage>')
message.attach(image)

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()

    context = ssl.create_default_context()
    server.starttls(context=context)
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    print('email sent')
except Exception as e:
    print(f'Error\n{e}')
finally:
    print('Closing server')
    server.quit()