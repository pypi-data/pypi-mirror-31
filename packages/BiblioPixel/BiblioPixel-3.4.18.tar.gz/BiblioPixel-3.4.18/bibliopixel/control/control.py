import collections, functools, sys, threading
from . extractor import Extractor
from .. project import construct, importer
from .. util.log_errors import LogErrors
from .. util import flatten, log, json
from .. util.threads import runnable
from . routing import ActionList, Routing


class Control(runnable.Runnable):
    DEFAULT = {'datatype': ActionList}

    def __init__(self, routing=None, default=None, errors='raise',
                 python_path='bibliopixel.control', verbose=False,
                 pre_routing=None):
        """
        :param Address pre_routing: This Address is set with with the message
            after the message is received and converted, but before it is
            routed.
        :param errors: either a number, indicating how many errors to report
           before ignoring them, or one of these strings:
           'raise', meaning to raise an exception
           'ignore', meaning to ignore all errors
           'report', meaning to report all errors
        """
        self.verbose = verbose
        self.receive = LogErrors(self._receive, errors)
        default = dict(self.DEFAULT, **(default or {}))
        self.pre_routing = ActionList(pre_routing)
        self.routing = Routing(routing or {}, default or {}, python_path)

    def set_root(self, root):
        self.pre_routing.set_root(root)
        self.routing.set_root(root)

    def start(self):
        super().start()
        if self.verbose:
            log.info('Starting %s', self)

        self.thread = self._make_thread()
        self.thread.start()

    def join(self, timeout=None):
        self.thread.join(timeout)

    def stop(self):
        super().stop()
        stop_thread = getattr(self.thread, 'stop', None)
        stop_thread and stop_thread()

    def _receive(self, msg):
        """
        Receive a message from the input source and perhaps raise an Exception.
        """
        msg = self._convert(msg)

        str_msg = self.verbose and self._msg_to_str(msg)
        if self.verbose and log.is_debug():
            log.debug('Message %s', str_msg)

        if self.pre_routing:
            self.pre_routing.receive(msg)

        receiver, msg = self.routing.receive(msg)
        if receiver:
            receiver.receive(msg)
            if self.verbose:
                log.info('Routed message %s (%s) to %s', str_msg, msg,
                         repr(receiver))

    def _convert(self, msg):
        """
        Convert the message to a Control-specific format
        """
        raise NotImplementedError

    def _make_thread(self):
        """
        Returns a new thread to run the loop for this control source.
        """
        raise NotImplementedError

    def _msg_to_str(self, msg):
        if msg is None:
            return '(None)'
        return '.'.join(str(s) for s in msg.values()) or '.'

    def __bool__(self):
        return bool(self.routing or self.pre_routing)


class ControlLoop:
    """Mixin class for looping controls"""
    def _receive_all_messages(self):
        for msg in self.messages():
            self.receive(msg)
            if not self.running:
                return

    def messages(self):
        """Should yield a sequence of messages from the input source."""
        raise NotImplementedError

    def _make_thread(self):
        return threading.Thread(target=self._receive_all_messages, daemon=True)


class ExtractedControl(Control):
    EXTRACTOR = {}

    def __init__(self, extractor=None, **kwds):
        super().__init__(**kwds)
        extractor = dict(self.EXTRACTOR, **(extractor or {}))
        self.extractor = Extractor(**extractor)

    def _convert(self, msg):
        return self.extractor.extract(msg)
