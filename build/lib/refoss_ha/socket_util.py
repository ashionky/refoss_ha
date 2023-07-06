from socket import *
import json,time,threading
from typing import  List


from .http_device import HttpDeviceInfo
from .util import killSocketPid
from .const import LOGGER


discoverMap=dict()
pushStateDataList=[]


class MerossSocket :

    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.event = threading.Event()

    def SocketReveiveMsg(self):

        # Empty IP address indicates receiving broadcast messages from any network segment
        address = ('', 9989)
        global discoverMap,pushStateMap
        if self.socket is None:
            self.socket = socket(AF_INET, SOCK_DGRAM)
            self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

            LOGGER.info("create global_socket ok")


        try:
            self.socket.bind(address)
            while True:
                if self.event.is_set():
                    return

                data, address = self.socket.recvfrom(1024)

                cdata=format(data.decode('utf-8'))
                dataDic=json.loads(cdata)


                if "payload" in dataDic and "header" in dataDic:
                    # Push state messages from device
                    pushStateDataList.append(dataDic)

                elif  "channels" in dataDic and "uuid" in dataDic:
                    #  Received broadcast reply message from  device
                    discoverMap[dataDic["uuid"]]=dataDic

        except Exception as e:
            LOGGER.info("socket SocketReveiveMsg stop")





    def startReveiveMsg(self):
        t1 = threading.Thread(target=self.SocketReveiveMsg)
        t1.start()


    def stopReveiveMsg(self):
        global discoverMap,pushStateMap
        try:
            self.event.set()
            if self.socket is not None:
                self.socket.close()
                self.socket=None

            discoverMap.clear()
            pushStateMap=[]
            killSocketPid(9989)

        except Exception as e:
            LOGGER.warning("socket stopReveiveMsg, %s", e)


    def SocketBroadcast(self):

        address = ('255.255.255.255', 9988)

        LOGGER.info("discovering  devices......")
        try:
            data={
                "id":"48cbd88f969eb3c486085cfe7b5eb1e4",
                "devName":"*",
            }
            strdata = json.dumps(data,separators=(',', ':'))
            msg=strdata.encode("utf-8")


            # send socket broadcast
            for i in range(3):
                self.socket.sendto(msg, address)
                time.sleep(1)

        except Exception as e:
            LOGGER.warning("socket SocketBroadcast, %s", e)



    def async_socket_find_devices(self)->List[HttpDeviceInfo]:
        global discoverMap

        # start thread for discover devices
        t = threading.Thread(target=self.SocketBroadcast)
        t.start()

        t.join() # wait thread  stop


        result=[]
        for key in discoverMap:
            info=HttpDeviceInfo.from_dict(discoverMap[key])
            result.append(info)
            LOGGER.info(f"discovered  device : {info.dev_name if info.dev_name is not None else info.device_type}")

        return result


