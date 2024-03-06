import socket
import email.utils
import os
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Create a unique Message-ID
def generate_message_id():
    return email.utils.make_msgid()

def send_email(sender, password, to, subject, body, attachment_paths, address, smtp_port, cc=None, bcc=None,max_file_size=3):
    message = MIMEMultipart()
    # Set up important fields
    message_id = generate_message_id()
    message["Message-ID"] = message_id
    message["Date"] = email.utils.formatdate(localtime=True)
    message["To"] = ", ".join(to) 
    message["Content-Language"] = "en-US"
    message["From"] = sender   
    message["Subject"] = subject
    #Create a list of all email recipients
    if cc:
        #put email addresses from the cc list into the "Cc" field of the email
        message["Cc"] = ", ".join(cc)
        to += cc
    if bcc:
        to += bcc

    # Add the text of the email
    message.attach(MIMEText(body, "plain", _charset="utf-8")) 
    #Send list of attached files
    if attachment_paths:
        for attachment_path in attachment_paths:
            try:
                # Check file size
                file_size = os.path.getsize(attachment_path) / (1024 * 1024)
                if file_size > max_file_size:
                    print(f"Error: Attachment file '{attachment_path}' exceeds the maximum allowed size of {max_file_size} MB.")
                    return
                # open file
                with open(attachment_path, "rb") as file:
                    file_name = os.path.basename(attachment_path)
                    attachment = MIMEApplication(file.read(), Name=file_name)
                    attachment["Content-Disposition"] = f'attachment; filename="{file_name}"'
                    message.attach(attachment)
            except FileNotFoundError:
                print(f"Error: Attachment file '{attachment_path}' not found.")
                return
            except Exception as e:
                print(f"Error: {e}")
                return

    #Calculate size before sending
    message_size = len(message.as_string())
    with socket.create_connection((address, smtp_port)) as client:
        client.recv(1024)
        #Send EHLO command to the server
        client.sendall(f"EHLO [{address}]\r\n".encode())
        #Read response from server
        client.recv(1024)

        #Send MAIL FROM command to the server
        client.sendall(f"MAIL FROM: <{sender}>\r\n".encode())
        client.recv(1024)

        # sends the RCPT TO command to the email server for each recipient in the to list
        for recipient in to:
            rcpt_to_command = f"RCPT TO: <{recipient}>\r\n".encode()
            
            client.sendall(rcpt_to_command)
            client.recv(1024)
            
        #sends a DATA command to the server to begin the process of sending the message body
        client.sendall(b"DATA\r\n")
        client.recv(1024)
        # Represent email content into standard format
        message_body = message.as_string()

        #send email content to the server
        client.sendall(f"{message_body}\r\n.\r\n".encode())
        client.recv(1024)

        client.sendall(b"NOOP\r\n")
        response = client.recv(1024).decode()
        if response.startswith("250"):
            print("\nEmail sent successfully!\n")
        else:
            print(f"\nError sending email.\n")