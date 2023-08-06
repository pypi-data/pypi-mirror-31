from .constants import *
import zmq
import pickle
from zmq.asyncio import Context, Poller
import asyncio
import time
class QWeatherClient:

    class serverclass:
        def __init__(self,name,addr,methods,client):
            self.name = name
            self.addr = addr
            self.client = client
            for amethod in methods:
                setattr(self,amethod[0],self.bindingfunc(amethod[0],amethod[1]))


        def bindingfunc(self,methodname,methoddoc):
            def func(*args,**kwargs):
                return self.client.send_request([self.name.encode(),methodname.encode(),pickle.dumps([args,kwargs])])
            func.__name__ = methodname
            func.__doc__ = methoddoc
            func.is_remote_server_method = True
            return func


        def __repr__(self):
            msg = ""
            lst = [getattr(self,method) for method in dir(self) if getattr(getattr(self,method),'is_remote_server_method',False)]
            if len(lst) == 0:
                return 'No servers connected'
            else:
                for amethod in lst:
                    msg += amethod.__name__ +"\n"
            return msg.strip()
    

    context = None
    socket = None
    poller = None
    futureobjectdict = {}

    def __init__(self,QWeatherStationIP,name = None,loop = None):
        self.QWeatherStationIP = QWeatherStationIP
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

        if name is None:
            import socket
            name = socket.gethostname()
        self.name = name.encode()
        self.reconnect()
        self.loop.run_until_complete(self.get_server_info())
        self.running = False
        self.messageid = 0




    def reconnect(self):
        '''connects or reconnects to the broker'''
        if self.poller:
            self.poller.unregister(self.socket)
        if self.socket: 
            self.socket.close()
        if self.context:
            self.context.term()
        self.context = Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(self.QWeatherStationIP)
        self.poller = Poller()
        self.poller.register(self.socket,zmq.POLLIN)
        #lol = asyncio.ensure_future()
        
    
    async def get_server_info(self):
        msg = [b'',b'C',CREADY,PCLIENT,self.name]
        self.send_message(msg)
        msg =  await self.socket.recv_multipart()
        empty = msg.pop(0)
        assert empty == b''
        command = msg.pop(0)
        self.serverlist = []
        if command == CREADY + CFAIL:
            raise Exception(msg.pop(0).decode())
        else:
            for name,items in pickle.loads(msg.pop(0)).items():
                addr = items[0]
                methods = items[1]
                server = self.serverclass(name,addr,methods,self)
                server.is_remote_server = True
                setattr(self,name,server)
                self.serverlist.append(server)
            

#                _method = 
 #               _method = methodclass(self.send_request,server.name,amethod[0],amethod[1])
  #              _method.is_remote_server_method = True
   #             setattr(server,amethod[0],_method)
        #print('loaded servers')
        return None

    def send_request(self,body):
        self.messageid+=1
        if self.messageid > 255:
            self.messageid = 0
        if self.running:
            result =  asyncio.get_event_loop().create_task(self.async_send_request(body,self.messageid.to_bytes(1,'big')))
        else:
            result = self.sync_send_request(body,self.messageid.to_bytes(1,'big'))
        return result

    def sync_send_request(self,body,ident):
        msg = [b'',b'C',CREQUEST,ident]  + body
        server = body[0]
        self.send_message(msg)
        msg = self.loop.run_until_complete(self.socket.recv_multipart())
        empty = msg.pop(0)
        assert empty == b''
        command = msg.pop(0)
        ident = msg.pop(0)
        server = msg.pop(0)
        answ = pickle.loads(msg[0])
        return answ
    
    async def async_send_request(self,body,ident):
        server = body[0]
        msg = [b'',b'C',CREQUEST,ident]  + body


        self.send_message(msg)
        answ = await self.recieve_message(ident+server)
        self.futureobjectdict.pop(ident+server)
        return answ
       # return msg

    def send_message(self,msg):
        #self.loop.create_task(self.socket.send_multipart(msg))
        self.socket.send_multipart(msg)


    def recieve_message(self,ident):
        tmp = self.loop.create_future()
        self.futureobjectdict[ident] = tmp
        #print('went here')
        return tmp

        #ans =self.loop.create_task(self.socket.recv_multipart())

#        ans = await self.socket.recv_multipart()
  #      return ans

    async def run(self):
        self.running = True
        tic = time.time()
        while True:
            try:
                items = await self.poller.poll(1000)
                if items:
                    msg = await self.socket.recv_multipart()
                    empty = msg.pop(0)
                    assert empty == b''
                    command = msg.pop(0)
                    if command == CREQUEST + CSUCCESS:
                        messageid = msg.pop(0)
                        server = msg.pop(0)
                        msg = pickle.loads(msg[0])
                        self.futureobjectdict[messageid + server].set_result(msg)
                    elif command == CREQUEST + CFAIL:
                        messageid = msg.pop(0)
                        server = msg.pop(0)
                        self.futureobjectdict[messageid+server].set_exception(Exception(msg.pop(0)))

                    #print(msg)
                toc = time.time()
                if toc-tic > 30:
                    answ = [b'',b'H',self.name]
                    self.send_message(answ)    
                    tic = toc
            except KeyboardInterrupt:
                break
                #self.socket.close()
                #self.context.term()



    def __repr__(self):
        #self.get_server_info()
        msg = ""
        if len(self.serverlist) == 0:
            return 'No servers connected'
        else:
            for aserver in self.serverlist:
                msg += aserver.name + "\n"
        return msg.strip()

    def __iter__(self):
        return (aserv for aserv in self.serverlist)

    def __getitem__(self,key):
        return self.serverlist[key]