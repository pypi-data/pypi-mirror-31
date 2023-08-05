from ack import ack
from announce import Announce
from channel import Channel
from connection import connection as Connection
from pika.spec import BasicProperties
from nrask.base import Base
from retry import retry

__all__ = [
    'ack',
    'Announce',
    'BasicProperties',
    'RMQ',
    'retry'
]

class RMQ(Base):
    __channels = None
    connection = None

    @property
    def channels(self):
        try:
            assert self.__channels
        except AssertionError:
            self.__channels = {}
        except:
            raise
        return self.__channels

    def __init__(self,url,future=None,stop=False,on_close=None,on_error=None):
        self.stop = stop
        self.url = url
        self.ioengine.loop.add_callback(
            self.connect,
            future=future,
            on_close=on_close,
            on_error=on_error
        )

    def __channel__(self,name,future,prefetch=None):
        try:
            assert self.channels[name].active
        except AssertionError:
            self.channels[name].promises.append(future)
        except (AttributeError,KeyError):
            self.channels[name] = Channel(self.connection,future=future,prefetch=prefetch)
        except:
            raise
        else:
            future.set_result(self.channels[name])
        return True

    def channel(self,name,future,prefetch=None):
        try:
            assert self.active
        except AssertionError:
            def on_active(_):
                self.ioengine.loop.add_callback(
                    self.__channel__,
                    name=name,
                    future=future,
                    prefetch=prefetch
                )
                return True

            self.promises.append(self.ioengine.future(on_active))
        except:
            raise
        else:
            self.ioengine.loop.add_callback(
                self.__channel__,
                name=name,
                future=future,
                prefetch=prefetch
            )
        return True

    def connect(self,future=None,on_close=None,on_error=None):
        def on_conn(result):
            self.active = True
            self.connection = result.result()

            try:
                future.set_result(self)
            except AttributeError:
                pass
            except:
                raise

            self.log.info('Connected')
            return True

        def on_error(conn,error):
            try:
                assert self.stop
            except AssertionError:
                self.log.warning(error)
                self.ioengine.loop.add_callback(
                    on_error,
                    conn,
                    error
                )
            except:
                raise
            else:
                self.log.error(error)
                self.ioengine.stop()
            return True

        Connection(
            future=self.ioengine.future(on_conn),
            on_close=on_close,
            on_error=on_error,
            url=self.url
        )
        return True
