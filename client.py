import json
import sys
import time
from POP3 import *
from SMTP import *
def configFile():
    with open('config.json') as file:
        data = json.load(file)
        return data['user']['sender'], data['user']['password'], data['address'], data['port'], data["autoload"], data["filterWord"]

def main():
    sender, password, address, port, autoload, filterWord = configFile()
    while (True):
        print("Option:")
        print("0. Exit")
        print("1. Send email")
        print("2. Read received emails")
        intChoice = int(input("Choose: "))
        if (intChoice == 1):
            print("This is the information to compose an email: (If not filled in, please press Enter to skip)")      
            to_input = input("To: ")
            if to_input.lower() != "":
                to = to_input.split(",")
            else:
                to = []
               
            cc_input = input("CC: ")
            if cc_input.lower() != "":
                cc = cc_input.split(",")
            else:
                cc = []
                
            bcc_input = input("BCC: ")
            if bcc_input.lower() != "":
                bcc = bcc_input.split(",")
            else:
                bcc = []
            
            
            attach_files = input("Files attached (1. Yes, 2. No): ")
            if attach_files == "1":
                num_files = int(input("Number of files you want to send: "))
                attachment_paths = []
                for i in range(num_files):
                    file_path = input(f"Indicates the file path {i + 1}: ")
                    attachment_paths.append(file_path)
            else:
                attachment_paths = None
            
            subject = input("Subject: ")
            content = input("Content: ")
            send_email(sender, password, to, subject, content, attachment_paths, address, port['smtp'], cc=cc, bcc=bcc)
        elif (intChoice == 2):
            downloadPeriodically(address, port["pop3"], sender, password, filterWord, autoload)
            # Select email folder
            while True:
                print("List of folders in your mailbox:")
                print("0. Exit")
                print("1. Inbox")
                print("2. Project")
                print("3. Important")
                print("4. Work")
                print("5. Spam")
                intFolder = int(input("Choose a folder to view emails(Input 0 to exit): "))
                if intFolder == 0:
                    break
                else:
                    emailList, filenameList = getEmailList(intFolder)
                    if intFolder == 1:
                        while True:
                            viewStatus = getViewStatus()
                            if emailList is None:
                                print("Inbox is empty")
                                break
                            else:
                                print("List of emails in Inbox:")
                                printFolder(emailList, filenameList, viewStatus)
                                intEmail = int(input("Choose an email to read(Input 0 to exit): "))
                                if intEmail == 0:
                                    break
                                else:
                                    saveViewStatus(filenameList[intEmail])
                                    printEmail(emailList, intEmail)
                            time.sleep(1)
                    elif intFolder == 2:
                        while True:
                            viewStatus = getViewStatus()
                            if emailList is None:
                                print("Project is empty")
                                break
                            else:
                                print("List of emails in Project:")
                                printFolder(emailList, filenameList, viewStatus)
                                intEmail = int(input("Choose an email to read(Input 0 to exit): "))
                                if intEmail == 0:
                                    break
                                else:
                                    saveViewStatus(filenameList[intEmail])
                                    printEmail(emailList, intEmail)
                            time.sleep(1)
                    elif intFolder == 3:
                        while True:
                            viewStatus = getViewStatus()
                            if emailList is None:
                                print("Important is empty")
                                break
                            else:
                                print("List of emails in Important:")
                                printFolder(emailList, filenameList, viewStatus)
                                intEmail = int(input("Choose an email to read(Input 0 to exit): "))
                                if intEmail == 0:
                                    break
                                else:
                                    saveViewStatus(filenameList[intEmail])
                                    printEmail(emailList, intEmail)
                            time.sleep(1)
                    elif intFolder == 4:
                        while True:
                            viewStatus = getViewStatus()
                            if emailList is None:
                                print("Work is empty")
                                break
                            else:
                                print("List of emails in Work:")
                                printFolder(emailList, filenameList, viewStatus)
                                intEmail = int(input("Choose an email to read(Input 0 to exit): "))
                                if intEmail == 0:
                                    break
                                else:
                                    saveViewStatus(filenameList[intEmail])
                                    printEmail(emailList, intEmail)
                            time.sleep(1)
                    elif intFolder == 5:
                        while True:
                            viewStatus = getViewStatus()
                            if emailList is None:
                                print("Spam is empty")
                                break
                            else:
                                print("List of emails in Spam:")
                                printFolder(emailList, filenameList, viewStatus)
                                intEmail = int(input("Choose an email to read(Input 0 to exit): "))
                                if intEmail == 0:
                                    break
                                else:
                                    saveViewStatus(filenameList[intEmail])
                                    printEmail(emailList, intEmail)
                            time.sleep(1)
        else:
            break  
if __name__ == "__main__":
    main()
    sys.exit(0)