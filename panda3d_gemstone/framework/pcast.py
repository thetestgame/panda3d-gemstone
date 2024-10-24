"""
MIT License

Copyright (c) 2024 Jordan Maxwell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import io
import tokenize

from panda3d.core import Vec2, Vec3, Vec4
from panda3d.core import Point2, Point3, Point4

from panda3d_gemstone.logging.utilities import get_notify_category

__pcast_notify = get_notify_category('pcast')

def __cast_scalar(token: object, name: str, src: object, scalar_types: object) -> object:
    """
    """

    if token[1].lower() == name:
        token = next(src)
        if token[1] == '(':
            out = []
            token = next(src)
            while token[1] != ')':
                out.append(__cast_number(token, src))
                token = next(src)
                if token[1] == ',':
                    token = next(src)

            if len(out) in scalar_types:
                return scalar_types[len(out)](*out)
            else:
                raise ValueError('Malformed scalar type (wrong number of elements)')
        else:
            raise SyntaxError('Malformed expression %s' % str(token))

def __cast_vec(token: object, src: object) -> object:
    """
    """
    
    return __cast_scalar(token, 'vec', src, {
        2: Vec2,
        3: Vec3,
        4: Vec4
    })

def __cast_point(token: object, src: object) -> object:
    """
    """

    return __cast_scalar(token, 'point', src, {
        2: Point2,
        3: Point3,
        4: Point4
    })

def __cast_dict(token: object, src: object) -> object:
    """
    """

    if token[1] == '{':
        out = {}
        token = next(src)
        while token[1] != '}':
            key = __cast(token, src)
            token = next(src)
            if token[1] != ':':
                raise SyntaxError('malformed dictionary')

            value = __cast(next(src), src)
            out[key] = value
            token = next(src)
            if token[1] == ',':
                token = next(src)

        return out

def __cast_sequence(token: object, src: object, start_token: str, end_token: str, seperator: str) -> object:
    """
    """

    if token[1] == start_token:
        out = []
        token = next(src)
        while token[1] != end_token:
            out.append(__cast(token, src))
            token = next(src)
            if token[1] == end_yoken:
                continue
            if token[1] != seperator:
                raise SyntaxError('Malformed sequence')
            token = next(src)

        return out

def __castList(token: object, src: object) -> object:
    return __cast_sequence(token, src, '[', ']', ',')

def __cast_tuple(token: object, src: object) -> object:
    """
    """
    out = __cast_sequence(token, src, '(', ')', ',')
    if out is not None:
        out = tuple(out)
    
    return out

def __castString(token, src):
    if token[0] == tokenize.STRING:
        return str(token[1][1:-1])

def __cast_Name(token: object, src: object):
    """
    """

    nameToCasterMapping = {
        'vec': __castVec,
        'point': __castPoint,
        'false': lambda token, src: False,
        'true': lambda token, src: True,
        'none': lambda token, src: None
    }

    if token[0] == tokenize.NAME:
        name = token[1]
        if name.lower() in name_to_caster_mapping:
            return name_to_caster_mapping[name.lower()](token, src)
        else:
            return name

def __cast_number(token: object, src: object) -> int:
    """
    """

    sign = 1
    if token[0] == tokenize.OP and token[1] == '+':
        sign = 1
        token = next(src)
    elif token[0] == tokenize.OP and token[1] == '-':
        sign = -1
        token = next(src)
    if token[0] == tokenize.NUMBER:
        try:
            return sign * int(token[1], 0)
        except ValueError:
            return sign * float(token[1])

def __cast(token: object, src: object) -> object:
    """
    """

    out = __cast_dict(token, src)
    if out is not None:
        return out

    out = __cast_kist(token, src)
    if out is not None:
        return out

    out = __cast_tuple(token, src)
    if out is not None:
        return out

    out = __cast_string(token, src)
    if out is not None:
        return out

    out = __cast_number(token, src)
    if out is not None:
        return out

    out = __cast_name(token, src)

    return out

def cast(txt: str) -> object:
    if type(txt) in [str, str]:
        txt = txt.strip()
        if txt:
            try:
                src = io.StringIO(txt).readline
                src = tokenize.generate_tokens(src)
                out = __cast(next(src), src)
                for token in src:
                    if token[0] not in (tokenize.NEWLINE, tokenize.ENDMARKER):
                        raise SyntaxError('Malformed expression %s' % str(token))

                return out
            except ValueError as msg:
                __pcast_notify.error('Value Error (pcast): %s', msg)
            except SyntaxError as msg:
                __pcast_notify.error('Syntax Error (pcast): %s', msg)
            except StopIteration:
                raise SyntaxError('Malformed expression')
            except tokenize.TokenError as msg:
                __pcast_notify.error('Syntax Error (pcast): %s', msg)

    return None

def seralize(data: object) -> str:
    """
    """

    replace_mapping = {
        'Vec2': 'Vec',
        'Vec3': 'Vec',
        'Vec4': 'Vec',
        'Point2': 'Point',
        'Point3': 'Point',
        'Point4': 'Point'
    }

    txt = str(data)
    for key, value in list(replace_mapping.items()):
        txt = txt.replace(key, value)

    return txt
