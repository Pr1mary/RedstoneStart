from mcrcon import MCRcon, MCRconException
from datetime import datetime
import re

class MCRconUtil:

    def __init__(self, host, secret, port = 25575, is_vanilla=False):
        self.host = host
        self.secret = secret
        self.port = port
        self.is_vanilla = is_vanilla

    def __command(self, command: str):

        if self.is_vanilla and not command.startswith("/"):
            command = "/{}".format(command)
        elif not self.is_vanilla and command.startswith("/"):
            command = command[1:]

        resp_cmd = ""

        starttime = datetime.now().timestamp()
        try:
            with MCRcon(self.host, self.secret, self.port, timeout=1) as mcrcon:
                resp_cmd = mcrcon.command(command)
                print("resp: [{}] >> {}".format(command, resp_cmd))
        except Exception as err:
            print("Error mc rcon: {}".format(err))
            resp_cmd = "[ERROR]"
        
        endtime = datetime.now().timestamp()
        deltatime = endtime-starttime
        print(deltatime)

        return resp_cmd
    
    def getPlayerList(self):
        
        command_str = "list"
        resp_cmd = self.__command(command_str)
        name_list = []
        reg_ptrn = r"There are \d+ of a max of \d+ players online:"
        
        if re.search(reg_ptrn, resp_cmd):
            name_list_str = re.sub(reg_ptrn, "", resp_cmd)
            name_list = name_list_str.strip().replace(" ", "").split(",")

        if len(name_list) == 1 and name_list[0] in ["", None]:
            name_list = []
        
        return name_list

    def addWhitelist(self, username: str):

        if not isinstance(username, str):
            return False
        
        command_str = "whitelist add {}".format(username)
        self.__command(command_str)

        return True
    
    def delWhitelist(self, username: str):

        if not isinstance(username, str):
            return False
        
        command_str = "whitelist remove {}".format(username)
        self.__command(command_str)

        return True
    
    def getWhitelist(self):
        
        command_str = "whitelist list"
        resp_cmd = self.__command(command_str)
        name_list = []
        reg_ptrn = r"There are \d+ whitelisted player\(s\):"
        
        if re.search(reg_ptrn, resp_cmd):
            name_list_str = re.sub(reg_ptrn, "", resp_cmd)
            name_list = name_list_str.strip().replace(" ", "").split(",")
        
        return name_list
    
    def banPlayer(self, username: str, reason:str = None):

        if not isinstance(username, str):
            return False
        
        if not reason:
            reason = "Banned by an operator"

        command_str = "ban {} {}".format(username, reason)
        self.__command(command_str)

        return True
    
    def pardonPlayer(self, username: str):

        if not isinstance(username, str):
            return False
        
        command_str = "pardon {}".format(username)
        self.__command(command_str)

        return True

    def setDifficulty(self, difficulty: str):

        if not isinstance(difficulty, str):
            return False
        
        command_str = "difficulty {}".format(difficulty)
        self.__command(command_str)

        return True
    
    def getDifficulty(self):
        
        command_str = "difficulty".format()
        resp_cmd = self.__command(command_str)
        difficulty_str = None

        if "The difficulty is" in resp_cmd:
            difficulty_str = resp_cmd.replace("The difficulty is", "").strip()
        
        return difficulty_str
    
    def isOnline(self):
        
        command_str = "version"
        resp_cmd = self.__command(command_str)

        if resp_cmd in ["", None, "[ERROR]"]:
            return False
        
        return True
