import socket
import re
import email.parser
import os
import glob
import threading
# Get content of email
def getContent(emailInfo):
    content = []
    for part in emailInfo.walk():
        if part.get('Content-Disposition') is not None:
            continue
        elif part.get_content_type() == 'text/plain':
            content.append(part.get_payload(decode = True).decode("utf-8"))
    content = '\r\n'.join(content)
    return content

# Filter emails into different folders
def filterEmail(emailFile, emailId, filterWord):
    emailInfo = email.message_from_string(emailFile)
    content = getContent(emailInfo)
    # From ahihi@testing.com or ahuu@testing.com -> Project
    # Subject contains "urgent" or "ASAP" -> Important
    # Content contains "report", "meeting" -> Work
    # Subject or content contains "virus", "hack", "crack" -> Spam
    # Else -> Inbox
    # Flag is used to check if email is filtered or not, if not then put it in Inbox.
    # Case insensitive
    for i in filterWord["Project"]:
        if i in emailInfo['from'].lower():
            with open(f"Project/{emailId}", 'w') as file:
                file.write(emailFile)
                return
    for i in filterWord["Important"]:
        if i in emailInfo['subject'].lower():
            with open(f"Important/{emailId}", 'w') as file:
                file.write(emailFile)
                return
    for i in filterWord["Work"]:
        if i in content.lower():
            with open(f"Work/{emailId}", 'w') as file:
                file.write(emailFile)
                return
    for i in filterWord["Spam"]:
        if i in content.lower() or i in emailInfo['subject'].lower():
            with open(f"Spam/{emailId}", 'w') as file:
                file.write(emailFile)
                return
    with open(f"Inbox/{emailId}", 'w') as file:
        file.write(emailFile)
            
# Download emails from mail server and delete them from server
def downloadEmail(address, port, sender, password, filterWord):
    serverAddress = (address, port)
    # Initialize phase
    client = socket.socket()
    client.connect(serverAddress)
    client.recv(1024)
    client.sendall(f"USER {sender}\r\n".encode("utf-8"))
    client.recv(1024)
    client.sendall(f"PASS {password}\r\n".encode("utf-8"))
    client.recv(1024)
    # Execute phase
    client.sendall(f"UIDL\r\n".encode('utf-8'))
    data1 = client.recv(1024).decode('utf-8')
    if "+OK\r\n.\r\n" in data1:
        return
    else:
        # Split email id from UIDL response (ex: 123.msg) and store in a list
        emailId = re.findall(r'\b(\d+\.msg)\b', data1)
        client.sendall("LIST\r\n".encode('utf-8'))
        LIST_response = client.recv(1024).decode('utf-8')
        # Split email id and size (ex: 1 100) and store in a list
        info = re.findall(r'\d+', LIST_response[3:-2])
        for i in range(0, len(info), 2):
            client.sendall(f"RETR {info[i]}\r\n".encode('utf-8'))
            # Calculate number of receive times
            numReceive = int(info[i + 1]) // 1024 + 1
            emailFile = []
            for _ in range(numReceive):
                RETR_response = client.recv(1024).decode("utf-8")
                if not RETR_response:
                    break
                emailFile.append(RETR_response)
            emailFile = ''.join(emailFile)
            emailFile = emailFile.split('\r\n')
            emailFile = emailFile[1:]
            emailFile = '\r\n'.join(emailFile)
            filterEmail(emailFile, emailId[int(info[i]) - 1], filterWord)
            # Delete email from server
            client.sendall(f"DELE {info[i]}\r\n".encode('utf-8'))
            client.recv(1024)
    client.sendall("QUIT\r\n".encode('utf-8'))
    client.recv(1024)
    
# Autoload 10s
def downloadPeriodically(address, port, sender, password, filterWord, autoload):
    downloadEmail(address, port, sender, password, filterWord)
    timer = threading.Timer(int(autoload), downloadPeriodically, [address, port, sender, password, filterWord, autoload])
    timer.daemon = True
    timer.start()
# Get email list from a specific folder
def getEmailList(intFolder):
    if intFolder == 1:
        folder = "Inbox"
    elif intFolder == 2:   
        folder = "Project"
    elif intFolder == 3:
        folder = "Important"
    elif intFolder == 4:
        folder = "Work"
    elif intFolder == 5:
        folder = "Spam"
    emailList = {}
    filenameList = {}
    i = 1
    # Run through all .msg files in folder and store their parse results in a dictionary
    # Store filenames in a dictionary 
    # Both dictionaries have the same key
    for filename in glob.glob(os.path.join(folder, '*.msg')):
        with open(os.path.join(os.getcwd(), filename), 'r') as file:
            emailInfoRaw = file.read().split('\n\n')
            emailInfoRaw = '\r\n'.join(emailInfoRaw)
            emailInfo = email.message_from_string(emailInfoRaw)
            emailList.update({i: emailInfo})
            filenameList.update({i: filename.split('\\')[-1]})
            i += 1
    if emailList == {}:
        return None, None
    else:
        return emailList, filenameList
# viewStatus.txt contains filenames which have been read
# Get view status from viewStatus.txt and store in a list
def getViewStatus(): 
    viewedEmail = []
    if not os.path.exists("viewStatus.txt"):
        with open("viewStatus.txt", 'w') as file:
            pass
    else:
        with open("viewStatus.txt", 'r') as file:
            viewedEmail = file.read().split('\n')
    return viewedEmail

# Check if message id is stored in viewStatus.txt, if not then add it to viewStatus.txt
def saveViewStatus(filename):
    with open("viewStatus.txt", 'r') as file:
        comparison = file.read().split('\n')
    if filename not in comparison:
        with open("viewStatus.txt", 'a') as file:
            file.write(filename + '\n')

# Print folder
def printFolder(emailList, filenameList, viewStatus):
    print("0. Exit")
    for key in emailList:
        if filenameList[key] in viewStatus:
            print(f"{key}. {emailList[key]['from']}, {emailList[key]['subject']}")
        else:
            print(f"{key}.(Unread) {emailList[key]['from']}, {emailList[key]['subject']}")

# Print email
def printEmail(emailList, intEmail):
    print(f"Date: {emailList[intEmail]['date']}")
    print(f"To: {emailList[intEmail]['to']}")
    print(f"From: {emailList[intEmail]['from']}")
    print(f"Subject: {emailList[intEmail]['subject']}")
    for part in emailList[intEmail].walk():
        # If email contains attachment then ask user if they want to save it
        if part.get('Content-Disposition') is not None:
            fileName = part.get_filename()
            print(f"Attachment: {fileName}")
            option = input("This email contains attachment(s), do you want to save it?(Y/N): ").upper()
            match option:
                case "Y":
                    directory = input("Enter directory to save attachment: ")
                    with open(os.path.join(directory, fileName), 'wb') as file:
                        file.write(part.get_payload(decode = True))
                case "N":
                    continue
                case _:
                    print("Invalid option")
                    continue
        # Print text/plain content
        elif part.get_content_type() == 'text/plain':
            print(part.get_payload(decode = True).decode("utf-8"))
        else:
            continue
        
