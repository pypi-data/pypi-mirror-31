# -*- coding: utf-8 -*-
'''
Syslog TCP listener for napalm-logs.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
try:
    import Queue as queue
except ImportError:
    import queue
import time
import random
import socket
import logging
import threading

# Import third party libs

# Import napalm-logs pkgs
from napalm_logs.config import TIMEOUT
from napalm_logs.config import BUFFER_SIZE
from napalm_logs.config import MAX_TCP_CLIENTS
from napalm_logs.listener.base import ListenerBase
# exceptions
from napalm_logs.exceptions import BindException
from napalm_logs.exceptions import ListenerException

log = logging.getLogger(__name__)


class TCPListener(ListenerBase):
    '''
    TCP syslog listener class
    '''
    def __init__(self, address, port, **kwargs):
        if kwargs.get('address'):
            self.address = kwargs['address']
        else:
            self.address = address
        if kwargs.get('port'):
            self.port = kwargs['port']
        else:
            self.port = port
        self.buffer_size = kwargs.get('buffer_size', BUFFER_SIZE)
        self.socket_timeout = kwargs.get('socket_timeout', TIMEOUT)
        self.max_clients = kwargs.get('max_clients', MAX_TCP_CLIENTS)
        self.buffer = queue.Queue()

    def _client_connection(self, conn, addr):
        '''
        Handle the connecition with one client.
        '''
        log.debug('Established connection with %s:%d', addr[0], addr[1])
        conn.settimeout(self.socket_timeout)
        try:
            while self.__up:
                msg = conn.recv(self.buffer_size)
                if not msg:
                    # log.debug('Received empty message from %s', addr)
                    # disabled ^ as it was too noisy
                    continue
                log.debug('[%s] Received %s from %s. Adding in the queue', time.time(), msg, addr)
                self.buffer.put((msg, '{}:{}'.format(addr[0], addr[1])))
        except socket.timeout:
            if not self.__up:
                return
            log.debug('Connection %s:%d timed out', addr[1], addr[0])
            raise ListenerException('Connection %s:%d timed out' % addr)
        finally:
            log.debug('Closing connection with %s', addr)
            conn.close()

    def _serve_clients(self):
        '''
        Accept cients and serve, one separate thread per client.
        '''
        self.__up = True
        while self.__up:
            log.debug('Waiting for a client to connect')
            try:
                conn, addr = self.skt.accept()
                log.debug('Received connection from %s:%d', addr[0], addr[1])
            except socket.error as error:
                if not self.__up:
                    return
                msg = 'Received listener socket error: {}'.format(error)
                log.error(msg, exc_info=True)
                raise ListenerException(msg)
            client_thread = threading.Thread(target=self._client_connection, args=(conn, addr,))
            client_thread.start()

    def start(self):
        '''
        Start listening for messages.
        '''
        log.debug('Creating the TCP server')
        if ':' in self.address:
            self.skt = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.skt.bind((self.address, int(self.port)))
        except socket.error as msg:
            error_string = 'Unable to bind to port {} on {}: {}'.format(self.port, self.address, msg)
            log.error(error_string, exc_info=True)
            raise BindException(error_string)
        log.debug('Accepting max %d parallel connections', self.max_clients)
        self.skt.listen(self.max_clients)
        self.thread_serve = threading.Thread(target=self._serve_clients)
        self.thread_serve.start()

    def receive(self):
        '''
        Return one message dequeued from the listen buffer.
        '''
        while self.buffer.empty() and self.__up:
            # This sequence is skipped when the buffer is not empty.
            sleep_ms = random.randint(0, 1000)
            # log.debug('The message queue is empty, waiting %d miliseconds', sleep_ms)
            # disabled ^ as it was too noisy
            time.sleep(sleep_ms / 1000.0)
        if not self.buffer.empty():
            return self.buffer.get(block=False)
        return '', ''

    def stop(self):
        '''
        Closing the socket.
        '''
        log.info('Stopping the TCP listener')
        self.__up = False
        try:
            self.skt.shutdown(socket.SHUT_RDWR)
        except socket.error:
            log.error('The following error may not be critical:', exc_info=True)
        self.skt.close()
