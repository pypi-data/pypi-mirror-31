"""
kraken.lib.models
~~~~~~~~~~~~~~~~~

Wraps around legacy pyrnn and protobuf models to provide a single interface. In
the future it will also include support for clstm models.
"""

from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from future.utils import PY2

from os.path import expandvars, expanduser, abspath

from builtins import next
from builtins import chr

import numpy
import gzip
import bz2
import sys
import io

import kraken.lib.lstm
import kraken.lib.lineest

from kraken.lib import pyrnn_pb2
from kraken.lib.exceptions import KrakenInvalidModelException

import logging

logger = logging.getLogger(__name__)

class ClstmSeqRecognizer(kraken.lib.lstm.SeqRecognizer):
    """
    A class providing the same interface to CLSTM networks as to pyrnn
    ones.
    """
    def __init__(self, fname, normalize=kraken.lib.lstm.normalize_nfkc):
        self.fname = fname
        self.rnn = None
        self.normalize = normalize
        global clstm
        import clstm
        self._load_model()

    @classmethod
    def init_model(cls, ninput, nhidden, codec):
        """
        Initialize a new neural network.

        Args:
            ninput (int): Dimension of input vector
            nhidden (int): Number of nodes in hidden layer
            codec (list): List mapping n-th entry in output matrix to glyph
        """
        self = cls()
        self.rnn = clstm.make_net_init('bidi',
                                       'ninput={}:nhidden={}:noutput={}'.format(ninput,
                                                                                nhidden,
                                                                                len(codec)))
        self.rnn.initialize()

    def save_model(self, path):
        """
        Serializes a CLSTM model to protobuf.

        Args:
            path (str): Path to serialize model to.

        Raises:
            IndexError if serialization failed for any reason.
        """
        clstm.save_net(path, self.rnn)

    def _load_model(self):
        # swig autoconverts py3 str to C++ string but expect byte strings on
        # py2. As filenames should always be byte strings convert it back to
        # str on py3 for swig.
        if not PY2:
            self.rnn = clstm.load_net(self.fname.decode('utf-8'))
        else:
            self.rnn = clstm.load_net(self.fname)

    def predictString(self, line):
        """
        Predicts a string from an input image.

        Args:
            line (numpy.array): Input image

        Returns:
            A unicode string containing the recognition result.
        """
        line = line.reshape(-1, self.rnn.ninput(), 1)
        self.rnn.inputs.aset(line.astype('float32'))
        self.rnn.forward()
        self.outputs = self.rnn.outputs.array().reshape(line.shape[0], self.rnn.noutput())
        codes = [x[0] for x in kraken.lib.lstm.translate_back_locations(self.outputs)]
        cls = clstm.Classes()
        cls.resize(len(codes))
        for i, v in enumerate(codes):
            cls[i] = int(v)
        res = self.rnn.decode(cls)
        return res

    def trainSequence(self, line, labels, update=1):
        """
        Trains the network using an input numpy array and a series of labels.

        Args:
            line (numpy.array): Input image
            labels (clstm.Classes): Label sequence
            update (bool): Switch to disable weight updates

        Returns:
            clstm.Classes containing the recognized label sequence.
        """
        line = line.reshape(-1, self.rnn.ninput(), 1)
        self.rnn.inputs.aset(line.astype('float32'))
        self.rnn.forward()
        self.outputs = self.rnn.outputs.array().reshape(line.shape[0], self.rnn.noutput())

        # build CTC alignment
        targets = clstm.Sequence()
        aligned = clstm.Sequence()
        clstm.mktargets(targets, labels, self.rnn.noutput())
        clstm.seq_ctc_align(aligned, self.rnn.outputs, targets)

        # calculate deltas, backpropagate and update weights
        deltas = aligned.array() - self.rnn.outputs.array()
        self.rnn.d_outputs.aset(deltas)
        self.rnn.backward()
        if update:
            self.rnn.update()

        codes = kraken.lib.lstm.translate_back(self.outputs)
        cls = clstm.Classes()
        cls.resize(len(codes))
        for i, v in enumerate(codes):
            cls[i] = v

        return cls

    def trainString(self, line, s, update=1):
        """
        Trains the network using an input numpy array and a unicode string.

        Strings are assumed to be in ``display`` order as produced as the
        result of the BiDi algorithm.

        Args:
            line (numpy.array): Input image
            s (str): Expected output string
            update (bool): Switch to disable weight updates

        Returns:
            An unicode string containing the recognized sequence.
        """
        labels = clstm.Classes()
        self.rnn.encode(labels, s)

        cls = self.trainSequence(line, labels)
        return self.rnn.decode(cls)

    def setLearningRate(self, rate=1e-4, momentum=0.9):
        """
        Sets learning rate and momentum on the model.

        Args:
            rate (float): Learning rate
            momentum (float): Momentum
        """
        self.rnn.learning_rate = rate
        self.rnn.momentum = momentum


def load_any(fname):
    """
    Loads anything that was, is, and will be a valid ocropus model and
    instantiates a shiny new kraken.lib.lstm.SeqRecognizer from the RNN
    configuration in the file.

    Currently it recognizes the following kinds of models:
        * pyrnn models containing BIDILSTMs
        * protobuf models containing converted python BIDILSTMs
        * protobuf models containing CLSTM networks

    Additionally an attribute 'kind' will be added to the SeqRecognizer
    containing a string representation of the source kind. Current known values
    are:
        * pyrnn for pickled BIDILSTMs
        * proto-pyrnn for protobuf models converted from pickled objects
        * clstm for protobuf models generated by clstm

    Args:
        fname (str): Path to the model

    Returns:
        A kraken.lib.lstm.SeqRecognizer object.

    Raises:
        KrakenInvalidModelException if the model file could not be recognized.
    """
    seq = None

    fname = abspath(expandvars(expanduser(fname)))
    logger.info('Loading model from {}'.format(fname))
    try:
        seq = load_pronn(fname)
        seq.kind = 'proto-pyrnn'
        return seq
    except:
        try:
            seq = load_clstm(fname)
            seq.kind = 'clstm'
            return seq
        except Exception as e:
            if PY2:
                try:
                    seq = load_pyrnn(fname)
                    seq.kind = 'pyrnn'
                    return seq
                except Exception as e:
                    raise
            else:
                raise

def load_clstm(fname):
    """
    Loads a CLSTM model in protobuf format and instantiates an object
    implementing the kraken.lib.SeqRecognizer interface.

    Args:
        fname (str): Path to the protobuf file

    Returns:
        A SeqRecognizer object

    Raises:
        KrakenInvalidModelException if no clstm module is available or the
        model is broken.
    """
    logger.info(u'Trying to load clstm model from {}'.format(fname))
    try:
        import clstm
    except ImportError:
        logger.debug(u'No clstm module available')
        raise KrakenInvalidModelException('No clstm module available')

    try:
        return ClstmSeqRecognizer(fname)
    except Exception as e:
        logger.debug(u'Loading clstm model failed.')
        raise KrakenInvalidModelException(str(e))


def load_pronn(fname):
    """
    Loads a legacy pyrnn model in protobuf format and instantiates a
    kraken.lib.lstm.SeqRecognizer object.

    Args:
        fname (str): Path to the protobuf file

    Returns:
        A kraken.lib.lstm.SeqRecognizer object
    """
    logger.info(u'Trying to load prornn model from {}'.format(fname))
    with open(fname, 'rb') as fp:
        logger.debug(u'Initializing protobuf message')
        proto = pyrnn_pb2.pyrnn()
        try:
            proto.ParseFromString(fp.read())
        except:
            logger.debug(u'File does not contain valid proto msg')
            raise KrakenInvalidModelException('File does not contain valid proto msg')
        if not proto.IsInitialized():
            logger.debug(u'Message in file incomplete')
            raise KrakenInvalidModelException('Model incomplete')
        # extract codec
        logger.debug(u'Extracting codec')
        codec = kraken.lib.lstm.Codec().init(proto.codec)
        hiddensize = proto.fwdnet.wgi.dim[0]
        # next build a line estimator
        logger.debug(u'Add line estimator')
        lnorm = kraken.lib.lineest.CenterNormalizer(proto.ninput)
        network = kraken.lib.lstm.SeqRecognizer(lnorm.target_height,
                                                hiddensize,
                                                codec=codec,
                                                normalize=kraken.lib.lstm.normalize_nfkc)
        logger.debug(u'Setting weights on BIDILSTM')
        parallel, softmax = network.lstm.nets
        fwdnet, revnet = parallel.nets
        revnet = revnet.net
        for w in ('WGI', 'WGF', 'WGO', 'WCI', 'WIP', 'WFP', 'WOP'):
            fwd_ar = getattr(proto.fwdnet, w.lower())
            rev_ar = getattr(proto.revnet, w.lower())
            setattr(fwdnet, w, numpy.array(fwd_ar.value).reshape(fwd_ar.dim))
            setattr(revnet, w, numpy.array(rev_ar.value).reshape(rev_ar.dim))
        softmax.W2 = numpy.array(proto.softmax.w2.value).reshape(proto.softmax.w2.dim)
        return network


def load_pyrnn(fname):
    """
    Loads a legacy RNN from a pickle file.

    Args:
        fname (str): Path to the pickle object

    Returns:
        Unpickled object

    Raises:
        KrakenInvalidModelException on python 3, when unpickling fails, or the
        unpickled object is not a SeqRecognizer.
    """
    logger.info(u'Trying to load pyrnn model from {}'.format(fname))
    if not PY2:
        logger.error(u'Loading pickle models is not support on python 3')
        raise KrakenInvalidModelException('Loading pickle models is not '
                                          'supported on python 3')
    import cPickle

    def find_global(mname, cname):
        aliases = {
            'lstm.lstm': kraken.lib.lstm,
            'ocrolib.lstm': kraken.lib.lstm,
            'ocrolib.lineest': kraken.lib.lineest,
        }
        if mname in aliases:
            return getattr(aliases[mname], cname)
        return getattr(sys.modules[mname], cname)

    of = io.open
    if fname.endswith(u'.gz'):
        of = gzip.open
    with io.BufferedReader(of(fname, 'rb')) as fp:
        unpickler = cPickle.Unpickler(fp)
        unpickler.find_global = find_global
        try:
            rnn = unpickler.load()
        except Exception as e:
            logger.error(u'Model file is not a pickle')
            raise KrakenInvalidModelException(str(e))
        if not isinstance(rnn, kraken.lib.lstm.SeqRecognizer):
            logger.error(u'Model file is {} instead of SeqRecognizer'.format(type(rnn).__name__))
            raise KrakenInvalidModelException('Pickle is {} instead of '
                                              'SeqRecognizer'.format(type(rnn).__name__))
        return rnn


def pyrnn_to_pronn(pyrnn=None, output='en-default.pronn'):
    """
    Converts a legacy python RNN to the new protobuf format. Benefits of the
    new format include independence from particular python versions and no
    arbitrary code execution issues inherent in pickle.

    Args:
        pyrnn (kraken.lib.lstm.SegRecognizer): pyrnn model
        output (str): path of the converted protobuf model
    """
    logger.info(u'Converting pyrnn model to prornn')
    proto = pyrnn_pb2.pyrnn()
    proto.kind = 'pyrnn-bidi'
    proto.ninput = pyrnn.Ni
    proto.noutput = pyrnn.No
    proto.codec.extend(pyrnn.codec.code2char.values())

    parallel, softmax = pyrnn.lstm.nets
    fwdnet, revnet = parallel.nets
    revnet = revnet.net
    for w in ('WGI', 'WGF', 'WGO', 'WCI', 'WIP', 'WFP', 'WOP'):
            fwd_weights = getattr(fwdnet, w)
            rev_weights = getattr(revnet, w)
            fwd_ar = getattr(proto.fwdnet, w.lower())
            rev_ar = getattr(proto.revnet, w.lower())
            fwd_ar.dim.extend(fwd_weights.shape)
            fwd_ar.value.extend(fwd_weights.reshape(-1).tolist())
            rev_ar.dim.extend(rev_weights.shape)
            rev_ar.value.extend(rev_weights.reshape(-1).tolist())
    proto.softmax.w2.dim.extend(softmax.W2.shape)
    proto.softmax.w2.value.extend(softmax.W2.reshape(-1).tolist())
    logger.debug(u'Saving converted model to {}'.format(output))
    with open(output, 'wb') as fp:
        fp.write(proto.SerializeToString())
