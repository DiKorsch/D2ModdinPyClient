'''
Created on 11.06.2014

@author: Schleppi
'''
from websocket import WebSocketApp as ConnectionManager
import json, thread

from d2mp.utils import log

class XSockets:
    Version = "3.0"
    class Events:
        onError = u"0x1f4"
        open = u"0xc8"
        close = u"0x12e0"
        onBlob = u"0x12d0"
        class storage:
            set = u"0x190"
            get = u"0x191"
            getAll = u"0x192"
            remove = u"0x193"
        class connection:
            onclientconnect = u"0xc9"
            onclientdisconnect = u"0xca"
            disconnect = u"0xcb"
        class bindings:
            completed = u"0x12c0"
        class pubSub:
            subscribe = u"0x12c"
            unsubscribe = u"0x12d"

class Message(object):
    def __init__(self, event, obj):
        super(Message, self).__init__()
        self.event = event
        self.object = obj

    def to_json(self):
        return json.dumps({
            "event": self.event,
            "data": json.dumps(self.object)})

class Callback(object):
    def __init__(self, name, fn, state = {}):
        super(Callback, self).__init__()
        self.name = name
        self.fn = fn
        self.state = state
    
    def __str__(self):
        return str(self.__dict__)
     
    def __repr__(self):
        return str(self.__dict__)

class Subscription(object):
    def __init__(self, name):
        super(Subscription, self).__init__()
        self.name = name
        self.callbacks = []
    
    def __str__(self):
        return "<%s: %s>" %(self.name, self.callbacks)
    
    def __repr__(self):
        return str(self)

    def addCallback(self, fn, state = {}):
        self.callbacks.append(Callback(self.name, fn, state))

    def removeCallback(self, idx):
        if idx is None or idx >= len(self.callbacks): return
        self.callbacks.pop(idx)

    def fireCallback(self, message, cb, idx = []):
        idxs = idx or range(len(self.callbacks))
        if not isinstance(idxs, list): idxs = [idxs]
        for idx in idxs:
            self.callbacks[idx].fn(message)
            # do some more magic...

class Subscriptions(object):
    def __init__(self):
        super(Subscriptions, self).__init__()
        self._subs = {}

    def add(self, name, fn, state = {}):
        name = name.lower()
        storedSub = self.get(name)
        if storedSub is None:
            sub = Subscription(name)
            sub.addCallback(fn, state)
            self._subs[name] = sub
            return 1

        storedSub.addCallback(fn, state)
        return len(storedSub.callbacks)

    def get(self, name):
        return self._subs.get(name.lower(), None)

    def getAll(self):
        return self._subs.values()

    def _pop(self, name):
        self._subs.pop(name.lower())


    def remove(self, name, ix = None):
        sub = self.get(name)
        if sub is None: return False
        sub.removeCallback(ix)

        if ix is None or len(sub.callbacks) == 0:
            self._pop(name)
        return True


    def fire(self, name, message, callback = None, ix = None):
        sub = self.get(name)
        if sub is None: return
        sub.fireCallback(message, callback, ix)

class XSocketsClient(object):
    def __init__(self, url, onerror = None, onopen = None, onclose = None):
        super(XSocketsClient, self).__init__()
        self.onerror = onerror
        self.onopen = onopen
        self.subscriptions = Subscriptions()
        self.webSocket = None
        self.bind(XSockets.Events.open, self._open_event_handler, opts = {"skip": True})

        thread.start_new_thread(self.start, (url, onopen, onclose))

    def _open_event_handler(self, data):
        log.DEBUG(data)
        data[u"clientType"] = u"RFC6455"
        self.connection = data
        self.XSocketsClientStorageGuid = data["StorageGuid"]
        for sub in self.subscriptions.getAll():
            for callback in sub.callbacks:
                if sub.name and callback.state.get("options", {}).get("skip", False): continue
                self.trigger(Message(
                    XSockets.Events.pubSub.subscribe,
                    {"Event": sub.name, "Confim": False}))
        self.dispatchEvent(XSockets.Events.bindings.completed, self.subscriptions.getAll())
        
        if self.onopen: self.onopen()


    def start(self, url, onopen, onclose):
        self.webSocket = ConnectionManager(url,
            on_message = self._on_message,
            on_error = self.print_error,
            on_close = onclose)
        self.webSocket.run_forever()

    def print_error(self, *args, **kwargs):
      print args, kwargs

    def __del__(self, *args):
        if self.webSocket is not None:
            self.webSocket.close()

    def _on_message(self, ws, message):
        cont = json.loads(message)
        log.DEBUG(cont)
        self.dispatchEvent(cont["event"], cont["data"])
        if cont["event"] == XSockets.Events.onError:
            if self.onerror: self.onerror(message)
            self.dispatchEvent(cont["event"], cont["data"])

    def bind(self, event, fn, opts = {}, callback = None):
        state = {
            "options": opts,
            "ready": self.webSocket is not None and self.webSocket.sock is not None,
            "confim": callback is not None
        }

        log.DEBUG("%s - %s" %(event, fn))
        if state["ready"]:
            self.trigger(Message(
                XSockets.Events.pubSub.subscribe,
                {"Event": event, "Confim": state["confim"]}))

        if isinstance(fn, list):
            for f in fn:
                self.subscriptions.add(event, f, state)
        else:
            self.subscriptions.add(event, fn, state)

        return self
    on = bind
    subscribe = bind

    def trigger(self, event, json = {}, callback = None):
        if isinstance(event, Message):
            message = event
        else:
            event = event.lower()
            message = Message(event, json)

        log.DEBUG(message.to_json())
        self.webSocket.send(message.to_json())
        if callback is not None: callback()
        return self

    publish = trigger
    emit = trigger

    def dispatchEvent(self, event, message):
        if self.subscriptions.get(event) is None: return
        self.subscriptions.fire(event, json.loads(message))
    
    def send(self, data, event):
        mes = Message(event, data)
        log.DEBUG(mes.to_json())
        self.webSocket.send(mes.to_json())

'''
def handleFoo(*args):
    logger.debug("foo says: %s" % (", ".join(args)))

logger.debug("START")
socket = XSocketsClient("ws://127.0.0.1:4502/Generic")
socket.bind("foo", handleFoo)



mes = raw_input("Enter a message: ")
while mes:
    socket.trigger("foo", mes)
    mes = raw_input("Enter a message: ")'''
