from datetime import datetime


class color_message:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

message_prefix = '({}){}: {}'

def loger(path,message):
    now=datetime.now()
    try:
        with open(path,"a") as myfile:
            myfile.write(now+'      '+message)
    except:
        return "wrong"
