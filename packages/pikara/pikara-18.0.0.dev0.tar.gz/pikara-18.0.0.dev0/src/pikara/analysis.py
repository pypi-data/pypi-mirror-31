import pickletools
from pickletools import anyobject, markobject, stackslice

import attr
from six import next

proto_opcode_names = [
    'PROTO',
    'FRAME',
    'STOP',
    'GLOBAL',
    'STACK_GLOBAL'
]

exec_opcode_names = [
    'INST', # v0
    'OBJ', # v1
    'REDUCE',
    'NEWOBJ', # v2; [cls, args] -> [cls.__new__(*args)]
    'NEWOBJ_EX', # v4; NEWOBJ, but with kwargs
    'BUILD' # __setstate__ or __dict__ update
]

persid_opcode_names = [
    'PERSID',
    'BINPERSID'
]


ext_opcode_names = [
    'EXT1',
    'EXT2',
    'EXT4'
]


safe_opcode_names = [
    'INT',
    'BININT',
    'BININT1',
    'BININT2',
    'LONG',
    'LONG1',
    'LONG4',
    'STRING',
    'BINSTRING',
    'SHORT_BINSTRING',
    'BINBYTES',
    'SHORT_BINBYTES',
    'BINBYTES8',
    'NONE',
    'NEWTRUE',
    'NEWFALSE',
    'UNICODE',
    'SHORT_BINUNICODE',
    'BINUNICODE',
    'BINUNICODE8'
]


float_opcode_names = [
    'FLOAT',
    'BINFLOAT'
]


list_opcode_names = [
    'EMPTY_LIST',
    'APPEND',
    'APPENDS',
    'LIST'
]


tuple_opcode_names = [
    'EMPTY_TUPLE',
    'TUPLE',
    'TUPLE1',
    'TUPLE2',
    'TUPLE3'
]


dict_opcode_names = [
    'EMPTY_DICT',
    'DICT',
    'SETITEM',
    'SETITEMS'
]


set_opcode_names = [
    'EMPTY_SET',
    'ADDITEMS',
    'FROZENSET'
]


stack_opcode_names = [
    'POP',
    'DUP',
    'MARK',
    'POP_MARK'
]


memo_opcode_names = [
    'GET',
    'BINGET',
    'LONG_BINGET',
    'PUT',
    'BINPUT',
    'LONG_BINPUT',
    'MEMOIZE'
]


def _last(stack):
    if stack: return stack[-1]


def _rfind(stack, elem, default=None):
    """
    Like _find but starts from the back.
    """
    for i in reversed(range(len(stack))):
        if stack[i] == elem:
            return i
    else:
        return default


def _find(stack, elem, default=None):
    """
    Like the venerable list.find: like list.index but doesn't raise an
    exception on error.
    """
    try:
        return stack.index(elem)
    except ValueError:
        return default


@attr.s(str=True)
class PickleException(RuntimeError):
    msg = attr.ib()

    op = attr.ib()
    arg = attr.ib()
    pos = attr.ib()
    stackslice = attr.ib()

    parsed = attr.ib()
    maxproto = attr.ib()
    stack = attr.ib()
    memo = attr.ib()



@attr.s(str=True)
class StackException(PickleException):
    pass


class StackUnderflowException(StackException):
    stackdepth = attr.ib()
    numtopop = attr.ib()


@attr.s(str=True)
class MemoException(PickleException):
    memoidx = attr.ib(default=None)


@attr.s
class _ParseResult(object):
    parsed = attr.ib()
    maxproto = attr.ib()
    stack = attr.ib()
    memo = attr.ib()


@attr.s
class _ParseEntry(object):
    op = attr.ib()
    arg = attr.ib()
    pos = attr.ib()
    stackslice = attr.ib()


def _parse(pickle):
    """
    Parses a pickle into a sequence of opcodes. Walks through the opcodes to
    build the memo and pickle stack without actually executing anything.
    Produces a parse tree that includes opcodes, positions, the memo at the
    end, any errors that were encountered along the way. Each opcode is
    annotated with the stackslice it operates on (if any); for example: an
    APPENDS instruction will have the list, a mark object, and the elements
    being appended to a list.
    """
    parsed = []
    annotations = []  # TODO: put exceptions here
    stack = []
    markstack = []
    stackslice = None
    memo = {}
    maxproto = -1
    op = arg = pos = None

    def _raise(E, msg, **kwargs):
        """
        Tiny helper for raising exceptions with lots of context.
        """
        raise E(
            msg=msg,
            op=op, arg=arg, pos=pos, stackslice=stackslice,
            parsed=parsed, maxproto=maxproto, stack=stack, memo=memo,
            **kwargs
        )

    for (op, arg, pos) in pickletools.genops(pickle):
        maxproto = max(maxproto, op.proto)

        before, after = op.stack_before, op.stack_after
        numtopop = len(before)

        # Should we pop a MARK?
        if markobject in before or (op.name == "POP" and _last(stack) is markobject):
            # instructions that take a stackslice claim to take only 1 object
            # off the stack, but that's really "anything up to a MARK
            # instruction" so it can be any number; this corrects the stack to
            # reflect that
            try:
                markpos = markstack.pop() # position in the _instruction stream_
                markidx = _rfind(stack, markobject) # position in the _stack_
                stack = stack[:markidx] + [markobject, stack[markidx + 1:]]
            except IndexError:
                _raise(StackException, "unexpected empty markstack")
            except ValueError:
                _raise(StackException, "expected markobject on stack to process")

        if op.name in ("PUT", "BINPUT", "LONG_BINPUT", "MEMOIZE"):
            memoidx = len(memo) if op.name == "MEMOIZE" else arg
            if memoidx in memo:
                _raise(MemoException, "double memo assignment", memoidx=memoidx)
            elif not stack:
                _raise(StackException, "empty stack when attempting to memoize")
            elif stack[-1] is markobject:
                _raise(MemoException, "can't store markobject in memo")
            else:
                memo[memoidx] = stack[-1]
        elif op.name in ("GET", "BINGET", "LONG_BINGET"):
            try:
                after = [memo[arg]]
            except KeyError:
                _raise(MemoException, "missing memo element {arg}")

        if numtopop:
            if len(stack) >= numtopop:
                stackslice = stack[-numtopop:]
                del stack[-numtopop:]
            else:
                _raise(StackUnderflowException, stackdepth=len(stack), numtopop=numtopop)
        else:
            stackslice = None

        if markobject in after:
            markstack.append(pos)

        if len(after) == 1 and stackslice:
            stack.append(stackslice)
        else:
            stack.extend(after)

        parsed.append(_ParseEntry(op=op, arg=arg, pos=pos, stackslice=stackslice))

    if pos != (len(pickle) - 1):
        raise PickleException(f"final pos is {pos} but pickle length is {len(pickle)}")

    return _ParseResult(parsed=parsed, stack=stack, maxproto=maxproto, memo=memo)


_critiquers = set()


def _critiquer(f):
    """
    Decorator to add a critiquer fn.
    """
    _critiquers.add(f)
    return f


@_critiquer
def _critique_end(parse_result):
    """
    The STOP opcode is the last thing in the stream.
    """
    if parse_result.parsed[-1].op.name != "STOP":
        raise PickleError("last opcode wasn't STOP", )


@attr.s
class CritiqueException(PickleException):
    issues = attr.ib()


def critique(pickle, brine=None, fail_fast=True):
    """
    Critiques a pickle.
    """
    issues = []
    optimized = pickletools.optimize(pickle)
    parse_result = _parse(optimized)
    for critiquer in _critiquers:
        try:
            critiquer(parse_result)
        except PickleException as e:
            if fail_fast:
                raise
            else:
                issues.append(e)
    if issues:
        raise CritiqueException(issues=issues)
    else:
        return optimized


def sample(pickle):
    """
    Given a pickle, return an abstraction ("brine") that can be used to see if
    a different pickle has a sufficiently similar structure.
    """
    raise NotImplementedError()


def safe_loads(pickle, brine):
    """
    Loads a pickle as safely as possible by using as much information as
    possible from the given distillate.
    """
    raise NotImplementedError()

# Tasting notes:

# POP, POP_MARK never occur in legitimate pickles, but they are an effective
# way of hiding a malicious object (created for side effects) from the
# algorithm that checks if the stack is fully consumed.

# In optimized pickles, PUTs/GETs only exist to support recursive structures.
# They also exist in non-optimized pickles, so we should optimize the pickle
# first. DUP is never used, even though it could work the same way.

# declaredproto < maxproto

#     if op.name != "STOP":
#        raise PickleException (f"final instruction was {op.name}, expected STOP")
