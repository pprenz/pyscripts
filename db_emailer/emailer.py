import sys
import os
import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.Encoders import encode_base64
import ConfigParser


def send_mail(server_addr, server_port, username, password, from_name, from_addr, to_addr, subject, body):
  msg = MIMEMultipart()
  msg['From'] = from_name
  msg['To'] = to_addr
  msg['Subject'] = subject
  msg.attach(MIMEText(body))

  mailServer = smtplib.SMTP(server_addr, server_port)
  mailServer.ehlo()
  mailServer.starttls()
  mailServer.ehlo()
  mailServer.login(username, password)
  mailServer.sendmail(from_addr, to_addr, msg.as_string())
  mailServer.close()

  print('Sent email to %s' % to_addr)


def get_body():
  file = open("content.txt")
  lines = file.readlines()
  file.close()
  string = "".join(lines)
  return string

if __name__ == "__main__":
  config = ConfigParser.ConfigParser()
  config.read("smtp.cfg")
  send_mail(
    server_addr=config.get("server","address"),
    server_port=config.get("server","port"),
    username=config.get("authentication","username"),
    password=config.get("authentication","password"),
    from_name=config.get("from","name"),
    from_addr=config.get("from","email"),
    to_addr=config.get("to","email"),
    subject="[DB-Alert] DB Push!",
    body=get_body()
  )
