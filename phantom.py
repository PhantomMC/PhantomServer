"""
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 
 @author: Thorin
"""
import socket
from pha_connection import connection_manager
from pha_json import json_creator
from pha_logging import logger
from pha_yaml import yaml_manager
from pha_bstats import bstats
import threading
import _thread
import time

Version = "0.7.13"
defaultConfig = {
        "configVersion" : 8,
        "serverInfo" : {
            "host" : "0.0.0.0",
            "port" : 25565
        },
        "Style" : 1, #chose between 1, 2 and 3
        "Content" : {
            "lowerMessage" : "A message",
            "upperMessage": "This msg appears above the server!",
            "hoverMessage" : "You should have brought a config",
            "kickMessage" : "Angry",
            "imagePath" : "server-icon.png"
        },
        "Logging" : 
            {
                "storeMessages" : False,
                "storeUsers":True
             },
        "debug" : False
        }


class pha_server(threading.Thread):
    def __init__(self):
        config_path = "config"
        is_config = True
        config_retriever = yaml_manager(defaultConfig, config_path, is_config)
        self.config = config_retriever.get_yml()
        self.host = self.config["serverInfo"]["host"]
        self.port = int(self.config["serverInfo"]["port"])
        self.serverSocket = self.getServerSocket()
        self.logger = logger(Version,self.config)
        self.json_creator = json_creator(self.config,self.logger)
        
        plugin_id = 10892
        bstats(plugin_id, self.logger, self.config).start()
        self.logger.debug("host:", self.host, "port", self.port)
        
    def getServerSocket(self):
        tryAmount = 3
        tryWait = 16 # s
        for i in range(tryAmount):
            try:
                serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                addr_info = socket.getaddrinfo(self.host, self.port)
                serverSocket.bind(addr_info[0][-1])
                return serverSocket
            except OSError:
                print("Port is already in use")
                time.sleep(tryWait)
                tryWait *= 2
        
    def run(self):
        try:
            i = 1
            while True:
                self.serverSocket.listen(1)
                (conn, addr) = self.serverSocket.accept()
                conn_mngr = connection_manager(conn,self.json_creator,self.logger,i,addr)
                self.logger.debug("Addres:",socket.inet_ntop(socket.AF_INET, addr))
                conn_mngr.start()
                i += 1
            print("This will never get triggered, but has to be here because of python")
        except Exception as e:
            self.logger.error(e)
        finally:
            self.serverSocket.close()
    def stop(self):
        self.serverSocket.close()
    
class phantom:
    def __init__(self):
        self.startServer()
        
    def acceptCommands(self):
        while(True):
            command = input()
            if (command.lower() == "stop") or ("exit" == command.lower()):
                self.phantom_server.stop()
                break;
            if command.lower() is "restart":
                print("<< restart is currently not implemented yet")
                #self.phantom_server.stop
                #self.startServer()
                continue
            
            print("unknown command")
        
    def startServer(self):
        self.phantom_server = pha_server()
        self.phantom_server.start()
        
        
phantomServer = phantom()
phantomServer.acceptCommands()
