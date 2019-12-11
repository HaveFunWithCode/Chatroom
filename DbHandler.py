import sqlite3

# database singleton - status for
class DbHandler:

    __instance=None
    def __init__(self):

        self.conn = self.__instance.conn
        self.cursor = self.__instance.cursor


    def __new__(cls):

        if  DbHandler.__instance is None:
            DbHandler.__instance=super().__new__(cls)
            try:
                DbHandler.__instance.conn = sqlite3.connect("chatroom")
                DbHandler.__instance.cursor = DbHandler.__instance.conn.cursor()
            except Exception as ex:
                DbHandler.__instance=None
                print("Error: connection to database not stablished")

            else:

                print("Connection to database is stablished")
                return DbHandler.__instance

        else:
            return DbHandler.__instance

    def __enter__(self):
        return self


    def __exit__(self):
        self.conn.close()



    def db_init_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users"
                            "(pid integer PRIMARY KEY AUTOINCREMENT ,"
                            " username VARCHAR(255),"
                            " age integer ,"
                            " gender BOOLEAN ,"
                            " country VARCHAR(255),"
                            "status int)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS chats(cid integer PRIMARY key AUTOINCREMENT,"
                            "user1 VARCHAR(255),user2 VARCHAR(255),date VARCHAR(255),message VARCHAR(255))")
        self.user_alter_status_forall_tooffline()

    def chat_insert_bylist(self,chatlist):
        query="INSERT INTO chats(user1,user2,date,message) VALUES(?,?,?,?)"
        dbQuery=self.dbQueryBylist(query,[tuple(chatlist)])
        if dbQuery:
            self.conn.commit()
            # self.conn.close()
            return True
        else:
            return False

    def chat_insert_single(self,user1,user2,date,message):
        query="INSERT INTO chats(user1,user2,date,message) VALUES({},{},{},{})".format(user1,user2,date,message)
        dbQuery=self.dbQueryBylist(query)
        if dbQuery:
            self.conn.commit()
            # self.conn.close()
            return True
        else:
            return False
    def chat_get_list(self,user1,user2):
        dbQuery="SELECT user1,user2,date,message from chats where (user1={0} and user2={1}) or (user2={0} and user1={1})  ".format("\'"+user1+"\'","\'"+user2+"\'")
        dbQuery = self.dbQueryByParam(dbQuery)
        if dbQuery:
            self.conn.commit()
            chats=self.cursor.fetchall()
            return chats
        else:
            # error in db connection
            # TODO: Should log
            return -2

    def user_register(self,user_info):

        query = "INSERT INTO users(username, age, gender,country,status)  VALUES(?,?,?,?,?)"
        dbQuery=self.dbQueryBylist( query, [tuple(user_info)])
        if dbQuery:
            self.conn.commit()
            # self.conn.close()
            return True
        else:

            return False

    def user_checkstatus(self,username):
        # 0: offline 1:online 2: busy     -1 no such username  -2 dbconnection erro
        query="SELECT status from users where username = {0} ".format("\'" + username + "\'")
        dbQuery=self.dbQueryByParam(query)
        if dbQuery:
            self.conn.commit()
            status=self.cursor.fetchall()

            # self.conn.close()
            if len(status)==0:
                # means not such username
                return -1
            return status[0][0]
        else:
            # error in db connection
            # TODO: Should log
            return -2
    def user_alter_status_forall_tooffline(self):
        query = "update users set status=0 "
        dbQuery = self.dbQueryByParam(query)
        if dbQuery:
            self.conn.commit()
            return True
        else:
            return False

    def user_alter_status(self,username,staus):
        # 0: offline 1:online 2: busy
        query="Update users set status={} where username= {}".format(staus,"\'"+username+"\'")
        dbQuery = self.dbQueryByParam(query)
        if dbQuery:
            self.conn.commit()
            return True
        else:
            return False


    def dbQueryByParam(self,query):
        try:
            self.cursor.execute(query)
            return True
        except:
            return False

    def dbQueryBylist(self, query, myList):
        try:
            self.cursor.executemany(query, myList)
            return True
        except Exception as ex:
            print(ex)
            return False




