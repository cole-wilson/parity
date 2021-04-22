from adicity import Adicity, Pointer, errors
from parity.arrays import Array, expandarray, ensureArray
import sys

code = """
$'Hello!'
"""


class SkipIteration(Exception):
    """This Excpetion is raised on a 'continue' statement in the Parity language."""
    pass


Parity = Adicity('Parity')

Parity.ignore(r'\s')
Parity.ignore(r'[\(\)]')
Parity.ignore(r'\n')
Parity.ignore(r',')
Parity.ignore(r'".*?"')
Parity.ignore(r'^".*?$')

Parity.token(r'\+', custom_name='ADDITION')(lambda a, b: a + b)
Parity.token(r'-', custom_name='SUBTRACTION')(lambda a, b: a - b)
Parity.token(r'\*', custom_name='MULTIPLICATION')(lambda a, b: a * b)
Parity.token(r'/', custom_name='DIVISION')(lambda a, b: a / b)
Parity.token(r'%', custom_name='MODULUS')(lambda a, b: a % b)
Parity.token(r'^', custom_name='EXPONENTATION')(lambda a, b: a ** b)
Parity.token(r'k', custom_name='BOOL')(lambda a: int(bool(a)))
Parity.token(r't', custom_name='EQUAL_MORETHAN')(lambda a, b: a >= b)


@Parity.totype
def to_array(value):
    if isinstance(value, int):
        return Array(value)
    elif isinstance(value, (str, float)):
        return Array(value)
    elif isinstance(value, Array):
        return value
    else:
        return Array(*value)


@Parity.token(r'x([a-f0-9]+)')
def HEX_INTEGER(self):
    """An integer in (lowercase) hex format."""
    return Array(int(self.capture, 16))


@Parity.token(r'-?[0-9]+\.[0-9]+')
def FLOAT(self):
    """A floating point decimal number."""
    return float(self.capture)


@Parity.token(r'-?[0-9]+')
def INTEGER(self):
    """A base 10 signed integer."""
    return int(self.capture, 10)


@Parity.token(r"'(.*?)'")
def STRING(self):
    """A string literal, single quotes only. No escapes."""
    return Array(*map(ord, self.capture))


@Parity.token(r'[A-Z]')
def VARIABLE(self):
    """A variable."""
    result = Parity.getvar(self.capture)
    return 0 if result is None else result


@Parity.token(r'h', custom_name='TWO_ARRAY', args=2)
@Parity.token(r'\[', end=r'\]')
def ARRAY(self):
    items = []
    for arg in self.args:
        val = arg()
        if len(val) == 1:
            items += val.items
        else:
            items.append(val)
    return Array(*items)


@Parity.token(r'b', custom_name='TWO_BLOCK', args=2)
@Parity.token(r'c', custom_name='THREE_BLOCK', args=3)
@Parity.token(r'\{', end=r'\}')
def BLOCK(self):
    out = 0
    for arg in self.args:
        out = arg()
    return out

# @Parity.token(r'`', custom_name='DEBUG_DUMP')
# def DEBUG_DUMP(self):
#     pretty_print(PROGRAM)

# @Parity.token(r'~', custom_name='BREAKPOINT')
# def DEBUG_LINE(self):
#     pass


@Parity.token(r'!')
def NOT(value):
    return int(not bool(value))


@Parity.token(r'\|')
def OR(value1, value2):
    return int(bool(value1) or bool(value2))


@Parity.token(r'&')
def AND(a, b):
    return int(bool(a) and bool(b))


@Parity.token(r'=')
def EQUALITY(a, b):
    return int(a == b)


@Parity.token(r'>')
def MORETHAN(a, b):
    return int(a > b)


@Parity.token(r'\$')
def ECHO_NEWLINE(self, value):
    """
    Prints the Unicode values of $1 to stdout with a trailing newline.
    This is equivalent to ECHO_OLDLINE, but with a newline at the end.
    """
    ECHO_OLDLINE(self, value)
    print()


@Parity.token(r';')
def ECHO_OLDLINE(self, value):
    """
    Prints the Unicode values of $1 to stdout with no trailing newline.
        -   $1: Unicode values to be printed, these are expanded.
    """
    try:
        print("".join(map(chr, expandarray(value))), end="")
    except ValueError:
        raise errors.InvalidAdicityCharacter(self)
    return 0


@Parity.token(r'#')
def TO_STR(value):
    str_value = str(value)
    if len(value) == 1:
        value = str_value[1:-1]
    return Array(*map(ord, map(str, value)))


@Parity.token(r':')
def RANGE(lower_bound, upper_bound):
    out = Array()
    out.items = []
    for i in range(lower_bound, upper_bound + 1):
        out.append(i)
    return out


@Parity.token(r'\?')
def IF(condition, then: Pointer, otherwise: Pointer):
    if bool(condition):
        return then()
    else:
        return otherwise()


@Parity.token(r'@')
def WHILE_LOOP(condition: Pointer, counter: Pointer, work: Pointer):
    count = 0
    out = Array()
    out.items = []
    while condition():
        try:
            Parity.setvar(counter.capture, count)
            out.append(work())
            count += 1
        except SkipIteration:
            continue
        except StopIteration:
            break
    return out


@Parity.token(r'<')
def INPUT(_type):
    index = int(_type)
    argv = sys.argv[1:]
    if index == 0:
        return Array(input('DEBUG REMOVE ME!! (input) > '))
    try:
        return [
            Array(*argv),
            Array(0)
        ][index - 1]
    except IndexError:
        return 0


@Parity.token(r'i')
def INSERT(into, indices, value):
    value = ensureArray(value)
    if len(value) == 1:
        value = value[0]
    if len(indices) != len(value):
        into.insert(int(indices), value)
    else:
        for valcount, index in enumerate(indices):
            into.insert(index, value[valcount])
    return into


@Parity.token(r'\\')
def CONSTANTS(index):
    items = [
        Array("Hello, World!"),
        Array("Fizz"),
        Array("Buzz"),
        Array("3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067"),
        Array("FizzBuzz"),
        Array(0)
    ]
    try:
        return items[index]
    except IndexError:
        return 0


@Parity.token(r'\.')
def INCREMENT(variable: Pointer):
    return Parity.setvar(variable.capture, variable() + 1)


@Parity.token(r'_')
def DECREMENT(variable: Pointer):
    return Parity.setvar(variable.capture, variable() - 1)


@Parity.token(r'a')
def RANGELOOP(length, counter: Pointer, work: Pointer):
    out = Array()
    out.items = []
    for i in range(length + 1):
        Parity.setvar(counter.capture, Array(i))
        out.append(work())
    return out


@Parity.token(r'd')
def DELETE(array, index):
    out = array
    for i in index:
        out[int(i())] = None
    newout = Array()
    for i in out:
        if i[0] is not None:
            newout.append(i)
    out = newout
    return out


@Parity.token(r'e')
def EDIT(array, indices, value):
    value = ensureArray(value)
    if len(value) == 1:
        value = value[0]
    if len(indices) != len(value):
        array[indices] = value
    else:
        for valcount, index in enumerate(indices):
            array[index] = value[valcount]
    return array


@Parity.token(r'f')
def SETFUNC(variable: Pointer, function: Pointer):
    return Parity.setvar(variable, function)


@Parity.token(r'g')
def GET(array, indices):
    out = []
    for i in indices:
        out.append(array[i])
    return Array(*out)


@Parity.token(r'j')
def JOIN(array, joiner):
    out = Array()
    out.items = []
    out.append(array[0])
    for i in array[1:]:
        out.append(joiner)
        out.append(i)
    return out


@Parity.token(r'l')
def ITER(array, counter: Pointer, work: Pointer):
    count = 0
    out = Array()
    out.items = []
    for i in array:
        Parity.setvar(counter, i)
        out.append(work())
        count += 1
    return out


@Parity.token(r'm')
def MAP(array, variable: Pointer, func: Pointer):
    out = Array()
    out.items = []
    for item in array:
        Parity.setvar(variable, item)
        out.append(func())
    return out


@Parity.token(r'n')
def LENGTH(array):
    return len(array)


@Parity.token(r'o')
def FILTER(array, variable: Pointer, func: Pointer):
    out = Array()
    out.items = []
    for item in array:
        Parity.setvar(variable, item)
        if func():
            out.append(item)
    return out


@Parity.token(r'p')
def PUSH(array, value):
    return array.append(value)


@Parity.token(r'q')
def PREPEND(array, value):
    return array.insert(Array(0), value)


@Parity.token(r'r')
def REPLACE(array, lookfor, replacewith):
    out = Array()
    out.items = []
    for item in array:
        if item == lookfor:
            out.append(replacewith)
        else:
            out.append(item)
    return out


@Parity.token(r's')
def SET(variable: Pointer, value):
    return Parity.setvar(variable, value)


@Parity.token(r'u')
def UPTO(value):
    out = Array()
    out.items = []
    for i in range(0, value + 1):
        out.append(i)
    return out


@Parity.token(r'v')
def SKIP():
    raise SkipIteration


@Parity.token(r'w')
def WHERE(array, search):
    count = 0
    for count, item in enumerate(array):
        if item == search:
            break
    return count


@Parity.token(r'x')
def BREAK():
    raise StopIteration


@Parity.token(r'y')
def ENUMERATE(array):
    out = Array()
    out.items = []
    for item in enumerate(array):
        item = list(item)
        if len(item[1]) == 1:
            item[1] = item[1][0]
        out.append(Array(*item))
    return out


@Parity.token(r'z')
def ZIP(a, b):
    out = Array()

    out.items = [*map(Array, zip(a, b))]
    return out
