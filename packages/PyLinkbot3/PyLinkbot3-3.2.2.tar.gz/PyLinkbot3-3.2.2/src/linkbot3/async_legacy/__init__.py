import asyncio
import logging
import os
import ribbonbridge as rb
import sys
import websockets

from . import peripherals
from .. import _util as util

from . import commontypes_legacy_pb2 as rbcommon

if sys.version_info < (3,4,4):
    asyncio.ensure_future = asyncio.async

__all__ = ['AsyncLinkbot', 'config', 'AsyncDaemon']

_dirname = os.path.dirname(os.path.realpath(__file__))

def config(**kwargs):
    ''' Configure linkbot module settings

        :param use_sfp: default:False Use WebSockets daemon communication transport, or the old SFP transport?
        :type use_sfp: bool
        :param daemon_hostport: default:'localhost:42000' Location of the linkbotd daemon.
        :type daemon_hostport: string
        :param timeout: default: 30 (seconds)
        :type timeout: float
    '''
    my_config = util.Config()
    if 'use_sfp' in kwargs:
        use_sfp = kwargs['use_sfp']
        if use_sfp:
            use_websockets = False
        else:
            use_websockets = True
        my_config.use_websockets = use_websockets

    if 'daemon_hostport' in kwargs:
        daemon_host = kwargs['daemon_hostport']
        my_config.daemon_host = daemon_host

    if 'timeout' in kwargs:
        timeout = kwargs['timeout']
        my_config.timeout = timeout

class _DaemonProxy(rb.Proxy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_protocol(self, protocol):
        self._protocol = protocol

    @asyncio.coroutine
    def rb_emit_to_server(self, bytestring):
        yield from self._protocol.send(bytestring)

class _AsyncLinkbot(rb.Proxy):
    '''
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def __del__(self):
        self.close()
    '''

    @classmethod
    @asyncio.coroutine
    def create(cls, serial_id):
        my_config = util.Config()

        if serial_id is None:
            serial_id = my_config.linkbot

        logging.info('Creating async Linkbot handle to ID:{}'.format(serial_id))
        logger=logging.getLogger('RBProxy.'+serial_id)
        self = cls( os.path.join(_dirname, 'robot_legacy_pb2.py'), logger=logger)

        serial_id = serial_id.upper()
        self._serial_id = serial_id
        self._loop = asyncio.get_event_loop()

        self.__daemon = _DaemonProxy(
                os.path.join(_dirname, 'daemon_legacy_pb2.py'))

        if my_config.use_websockets:
            self.__log('Creating Websocket connection to daemon...')
            protocol = yield from websockets.connect(
                    'ws://'+my_config.daemon_host[0]+':'+my_config.daemon_host[1], loop=self._loop)
        else:
            self.__log('Creating tcp connection to daemon...')
            import sfp
            (transport, protocol) = yield from sfp.client.connect(
                    my_config.daemon_host[0], my_config.daemon_host[1], loop=self._loop)

        self.__log('Daemon TCP connection established.')
        protocol.connection_lost = self.__connection_closed

        self.__daemon.set_protocol(protocol)
        self._daemon_protocol = protocol
        daemon_consumer = asyncio.ensure_future(self.__daemon_consumer(protocol))
        self.__log('Initiating daemon handshake...')
        yield from asyncio.sleep(0.5)
        yield from self.__daemon.rb_connect()
        self.__log('Daemon handshake finished.')

        yield from asyncio.sleep(0.5)
        self.__log('Resolving serial id: ' + serial_id)
        args = self.__daemon.rb_get_args_obj('resolveSerialId')
        args.serialId.value = serial_id
        result_fut = yield from self.__daemon.resolveSerialId(args)
        tcp_endpoint = yield from result_fut
        if tcp_endpoint.status != rbcommon.OK:
            self.logger.warning('Could not connect to robot: {}'.format(
                rbcommon.Status.Name(tcp_endpoint.status)))
            raise RuntimeError('Could not connect to remote robot: {}'.format(
                rbcommon.Status.Name(tcp_endpoint.status)))
        self.__log('Connecting to robot endpoint:'+my_config.daemon_host[0]+':'+str(tcp_endpoint.endpoint.port)) 
        if my_config.use_websockets:
            linkbot_protocol = yield from websockets.client.connect(
                    'ws://'+my_config.daemon_host[0]+':'+str(tcp_endpoint.endpoint.port),
                    loop=self._loop)
        else:
            (_, linkbot_protocol) = \
                    yield from sfp.client.connect(
                            tcp_endpoint.endpoint.address,
                            tcp_endpoint.endpoint.port)
        self.__linkbot_consumer_handle = \
            asyncio.ensure_future(self.__linkbot_consumer(linkbot_protocol))
        self.__log('Connected to robot endpoint.')
        self._linkbot_protocol = linkbot_protocol
        self.__log('Sending connect request to robot...')
        yield from asyncio.sleep(0.5)
        yield from self.rb_connect()
        self.__log('Done sending connect request to robot.')

        #Get the form factor
        fut = yield from self.getFormFactor()
        result_obj = yield from fut
        self.form_factor = result_obj.value
        return self

    @asyncio.coroutine
    def disconnect(self):
        yield from self._linkbot_protocol.close()
        yield from self._daemon_protocol.close()

    @asyncio.coroutine
    def __daemon_consumer(self, protocol):
        while True:
            try:
                msg = yield from protocol.recv()
                if msg is None:
                    continue
            except asyncio.CancelledError:
                logging.warning('Daemon consumer received asyncio.CancelledError')
                return
            except websockets.exceptions.ConnectionClosed:
                logging.info('Daemon consumer connection closed.')
                return
            yield from self.__daemon.rb_deliver(msg)

    @asyncio.coroutine
    def __linkbot_consumer(self, protocol):
        logging.info('Linkbot message consumer starting...')
        while True:
            try:
                logging.info('Consuming Linkbot message from WS...')
                msg = yield from protocol.recv()
            except asyncio.CancelledError:
                return
            except websockets.exceptions.ConnectionClosed:
                logging.info('Connection Closed.')
                return
            yield from self.rb_deliver(msg)

    def close(self):
        self._linkbot_protocol.close()
        self.__linkbot_consumer_handle.cancel()

    def __connection_closed(self, exc):
        ''' Called when the connection is closed from the other end.
           
            :param exc: An exception or "None"
        '''
        if exc:
            self.__log('Remote closed connection: '+str(exc), 'warning')
        else:
            self.__log('Remote closed connection gracefully.')
        self.rb_close()

    @asyncio.coroutine
    def rb_emit_to_server(self, bytestring):
        yield from self._linkbot_protocol.send(bytestring)

    def __log(self, msg, logtype='info'):
        getattr(logging, logtype)(self._serial_id + ': ' + msg)

    @asyncio.coroutine
    def event_handler(self, payload):
        joint = payload.encoder
        value = payload.value
        timestamp = payload.timestamp
        try:
            yield from self._handlers[joint](util.rad2deg(value), timestamp)
        except IndexError:
            # Don't care if the callback doesn't exist
            pass
        except TypeError:
            pass

    def set_event_handler(self, index, callback):
        assert(index >= 0 and index < 3)
        self._handlers[index] = callback

class AsyncLinkbot():
    @classmethod
    @asyncio.coroutine
    def create(cls, serial_id):
        """ Create a new asynchronous Linkbot object.

        :param serial_id: The robot to connect to
        :type serial_id: str
        :returns: AsyncLinkbot() object.
        """
        try:
            self = cls()
            self._proxy = yield from asyncio.wait_for( _AsyncLinkbot.create(serial_id), 
                                                  util.DEFAULT_TIMEOUT )
            self.rb_add_broadcast_handler = self._proxy.rb_add_broadcast_handler
            self.close = self._proxy.close
            self.enableButtonEvent = self._proxy.enableButtonEvent
            self._accelerometer = yield from peripherals.Accelerometer.create(self)
            self._battery = yield from peripherals.Battery.create(self)
            self._button = yield from peripherals.Button.create(self)
            self._buzzer = yield from peripherals.Buzzer.create(self)
            self._eeprom_obj = yield from peripherals.Eeprom.create(self)
            self._led = yield from peripherals.Led.create(self)
            self._motors = yield from peripherals.Motors.create(self)
            self._twi = yield from peripherals.Twi.create(self)
            self._serial_id = serial_id

            # Enable joint events
            yield from self._proxy.enableJointEvent(enable=True)
            self._proxy.rb_add_broadcast_handler('jointEvent', self.__joint_event)
            self._proxy.rb_add_broadcast_handler('debugMessageEvent',
                    self.__debug_message_event)
            return self
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(
                'Timed out trying to connect to remote robot. Please ensure '
                'that the remote robot is on and not currently connected to '
                'another computer.' )

    @asyncio.coroutine
    def disconnect(self):
        yield from self._proxy.disconnect()

    @property
    def accelerometer(self):
        """
        The Linkbot accelerometer.

        See :class:`linkbot3.async.peripherals.Accelerometer`.
        """
        return self._accelerometer

    @property
    def battery(self):
        """
        The Linkbot battery.

        Access the Linkbot's battery voltage. See
        :class:`linkbot3.async.peripherals.Battery`
        """
        return self._battery

    @property
    def buttons(self):
        """
        Access to the Linkbot's buttons. 

        See :class:`linkbot3.async.peripherals.Button`.
        """
        return self._button

    @property
    def buzzer(self):
        """
        Access to the Linkbot's buzzer.

        See :class:`linkbot3.async.peripherals.Buzzer`.
        """
        return self._buzzer

    @property
    def _eeprom(self):
        """
        Access the robot's EEPROM memory.

        Warning: Improperly accessing the robot's EEPROM memory may yield
        unexpected results. The robot uses EEPROM memory to store information
        such as its serial ID, calibration data, etc.
        """
        return self._eeprom_obj

    @property
    def led(self):
        """
        The Linkbot multicolor LED.

        See :class:`linkbot3.async.peripherals.Led`.
        """
        return self._led

    @property
    def motors(self):
        """
        The motors of the Linkbot.

        See :class:`linkbot3.async.peripherals.Motors` . To access individual motors, you may do:

            AsyncLinkbot.motors[0].is_moving()

        or similar. Also see :class:`linkbot3.async.peripherals.Motor`
        """
        return self._motors

    @property
    def twi(self):
        """
        Access the I2C two-wire interface of the Linkbot.

        See :class:`linkbot3.async.peripherals.Twi` .
        """
        return self._twi

    @asyncio.coroutine
    def reboot(self):
        result_fut = yield from self._proxy.reboot({})
        return result_fut

    @asyncio.coroutine
    def version(self):
        '''
        Get the firmware version

        :returns: asyncio.Future with result (major, minor, patch)
        :rtype: asyncio.Future with result type: (int, int, int)
        '''
        def conv(payload):
            return (payload.major, payload.minor, payload.patch)

        fut = yield from self._proxy.getFirmwareVersion()
        user_fut = asyncio.Future()
        util.chain_futures(fut, user_fut, conv=conv)
        return user_fut

    @asyncio.coroutine
    def form_factor(self):
        '''
        Get the robot's self-identified form factor

        :returns: asyncio.Future with result int
        :rtype: asyncio.Future with result type: int
        '''
        def conv(payload):
            return payload.value

        fut = yield from self._proxy.getFormFactor()
        user_fut = asyncio.Future()
        util.chain_futures(fut, user_fut, conv=conv)
        return user_fut

    @asyncio.coroutine
    def set_peripherals_reset(self, peripheral_mask, mask=0xff):
        '''
        Specify which peripherals to reset when the robot is disconnected.

        Values should be "1<<Linkbot.MOTOR1 | 1<<Linkbot.LED", etc. Valid peripheral_mask values are:

        Linkbot.MOTOR1
        Linkbot.MOTOR2
        Linkbot.MOTOR3
        Linkbot.LED
        Linkbot.BUZZER
        '''
        args_obj = self._proxy.rb_get_args_obj('setResetOnDisconnect')
        args_obj.peripheralResetMask = peripheral_mask
        args_obj.mask = mask
        fut = yield from self._proxy.setResetOnDisconnect(args_obj)
        return fut
    
    @asyncio.coroutine    
    def __joint_event(self, payload):
        # Update the motor states
        self.motors[payload.joint].state = payload.event

    @asyncio.coroutine
    def __debug_message_event(self, payload):
        logging.warning('Received DEBUG message from robot {}: {}'
                .format(self._serial_id, payload.bytestring))

class AsyncDaemon(_DaemonProxy):
    @classmethod
    @asyncio.coroutine
    def create(cls):
        my_config = util.Config()

        self = cls(os.path.join(_dirname, 'daemon_legacy_pb2.py'))

        if my_config.use_websockets:
            #self.__log('Creating Websocket connection to daemon...')
            protocol = yield from websockets.connect(
                    'ws://'+my_config.daemon_host[0]+':'+my_config.daemon_host[1])
        else:
            #self.__log('Creating tcp connection to daemon...')
            (transport, protocol) = yield from sfp.client.connect(
                    my_config.daemon_host[0], my_config.daemon_host[1])
        
        self.set_protocol(protocol)
        self.consumer = asyncio.ensure_future(self.__consumer(protocol))
        yield from self.rb_connect()

        return self

    @asyncio.coroutine
    def cycle(self, seconds):
        args = self.rb_get_args_obj('cycleDongle')
        args.seconds = seconds
        result_fut = yield from self.cycleDongle(args)
        return result_fut

    @asyncio.coroutine
    def reboot(self):
        result_fut = yield from self.reboot({})
        return result_fut

    @asyncio.coroutine
    def ping(self, destinations = [], peripheral_reset_mask = 0x1f):
        args = self.rb_get_args_obj('sendRobotPing')
        for d in destinations:
            serial_id_obj = args.destinations.add()
            serial_id_obj.value = d
        args.peripheralResetMask = peripheral_reset_mask
        result_fut = yield from self.sendRobotPing(args)
        return result_fut

    @asyncio.coroutine
    def __consumer(self, protocol):
        while True:
            try:
                msg = yield from protocol.recv()
                if msg is None:
                    continue
            except asyncio.CancelledError:
                logging.warning('Daemon consumer received asyncio.CancelledError')
                return
            except websockets.exceptions.ConnectionClosed:
                logging.info('Connection Closed.')
                return
            yield from self.rb_deliver(msg)

