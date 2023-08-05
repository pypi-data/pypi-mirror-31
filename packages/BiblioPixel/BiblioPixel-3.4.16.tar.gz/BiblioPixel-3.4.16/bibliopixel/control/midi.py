import fractions
from . import control
from .. util import log

try:
    import mido
    MESSAGE_TYPES = set(s['type'] for s in mido.messages.specs.SPECS)

except:
    mido = None
    MESSAGE_TYPES = set()

MIDO_ERROR = """You need to install mido.  Try
    pip install mido
"""


MIDO_BACKEND_ERROR = """You have the wrong rtmidi installed.  Try
    pip uninstall -y rtmidi
    pip install -y python-rtmidi
"""


class Midi(control.ExtractedControl):
    EXTRACTOR = {
        # There are more mido message types that we haven't used yet.
        'keys_by_type': {
            'aftertouch': (
                'port', 'channel', 'type', 'value'),
            'control_change': (
                'port', 'channel', 'type', 'control', 'value'),
            'note_off': (
                'port', 'channel', 'type', 'note', 'velocity'),
            'note_on': (
                'port', 'channel', 'type', 'note', 'velocity'),
            'pitchwheel': (
                'port', 'channel', 'type', 'pitch'),
            'program_change': (
                'port', 'channel', 'type', 'program'),
        },

        # Some numeric fields (channel, control, program and note) don't get
        # normalized because they are basically names.
        'normalizers': {
            'pitch': lambda x: fractions.Fraction(x - 8192) / 8192,
            'value': lambda x: fractions.Fraction(x) / 127,
            'velocity': lambda x: fractions.Fraction(x) / 127,
        },

        'omit': ('port', 'channel'),
    }

    def __init__(self, use_note_off=False, **kwds):
        super().__init__(**kwds)
        self.use_note_off = use_note_off

    def messages(self):
        if not mido:
            raise ValueError(MIDO_ERROR)
        try:
            input_names = mido.get_input_names()
        except AttributeError as e:
            e.args = (MIDO_ERROR,) + e.args
            raise

        ports = [mido.open_input(i) for i in input_names]

        if not ports:
            log.error('control.midi: no MIDI ports found')
            return

        log.info('Starting to listen for MIDI')
        for port, msg in mido.ports.MultiPort(ports, yield_ports=True):
            mdict = dict(vars(msg), port=port)
            if self.use_note_off or msg.type != 'note_off':
                yield mdict
            else:
                yield dict(mdict, type='note_on', velocity=0)
