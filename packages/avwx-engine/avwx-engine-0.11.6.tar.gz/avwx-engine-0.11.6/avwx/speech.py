"""
Contains functions for converting translations into a speech string
Currently only supports METAR
"""

# stdlib
from copy import deepcopy
# module
from avwx import core, translate
from avwx.static import SPOKEN_UNITS, NUMBER_REPL, FRACTIONS


def numbers(num: str) -> str:
    """
    Returns the spoken version of a number

    Ex: 1.2 -> one point two
    """
    if num in FRACTIONS:
        return FRACTIONS[num]
    return ' '.join([NUMBER_REPL[char] for char in num if char in NUMBER_REPL])


def remove_leading_zeros(num: str) -> str:
    """
    Strips zeros while handling -, M, and empty strings
    """
    if not num:
        return num
    if num.startswith('M'):
        ret = 'M' + num[1:].lstrip('0')
    elif num.startswith('-'):
        ret = '-' + num[1:].lstrip('0')
    else:
        ret = num.lstrip('0')
    return ret if ret else '0'


def wind(wdir: str, wspd: str, wgst: str, wvar: [str] = None, unit: str = 'kt') -> str:
    """
    Format wind details into a spoken word string
    """
    if unit in SPOKEN_UNITS:
        unit = SPOKEN_UNITS[unit]
    if wdir not in ('000', 'VRB'):
        wdir = numbers(wdir)
    wvar = wvar if not wvar is None else []
    for i, val in enumerate(wvar):
        wvar[i] = numbers(val)
    return 'Winds ' + translate.wind(wdir, remove_leading_zeros(wspd),
                                     remove_leading_zeros(wgst), wvar,
                                     unit, cardinals=False)


def temperature(header: str, temp: str, unit: str = 'C') -> str:
    """
    Format temperature details into a spoken word string
    """
    if core.is_unknown(temp):
        return header + ' Unknown'
    if unit in SPOKEN_UNITS:
        unit = SPOKEN_UNITS[unit]
    temp = numbers(remove_leading_zeros(temp))
    use_s = '' if temp in ('one', 'minus one') else 's'
    return ' '.join((header, temp, 'degree' + use_s, unit))


def unpack_fraction(num: str) -> str:
    """
    Returns unpacked fraction string 5/2 -> 2 1/2
    """
    nums = [int(n) for n in num.split('/')]
    if nums[0] > nums[1]:
        over = nums[0] // nums[1]
        rem = nums[0] % nums[1]
        return '{} {}/{}'.format(over, rem, nums[1])
    return num


def visibility(vis: str, unit: str = 'm') -> str:
    """
    Format visibility details into a spoken word string
    """
    if core.is_unknown(vis):
        return 'Visibility Unknown'
    elif vis.startswith('M'):
        vis = 'less than ' + numbers(remove_leading_zeros(vis[1:]))
    elif vis.startswith('P'):
        vis = 'greater than ' + numbers(remove_leading_zeros(vis[1:]))
    elif '/' in vis:
        vis = unpack_fraction(vis)
        vis = ' and '.join([numbers(remove_leading_zeros(n)) for n in vis.split(' ')])
    else:
        vis = translate.visibility(vis, unit=unit)
        if unit == 'm':
            unit = 'km'
        vis = vis[:vis.find(' (')].lower().replace(unit, '').strip()
        vis = numbers(remove_leading_zeros(vis))
    ret = 'Visibility ' + vis
    if unit in SPOKEN_UNITS:
        ret += ' ' + SPOKEN_UNITS[unit]
        if not (('one half' in vis and ' and ' not in vis) or 'of a' in vis):
            ret += 's'
    else:
        ret += unit
    return ret


def altimeter(alt: str, unit: str = 'inHg') -> str:
    """
    Format altimeter details into a spoken word string
    """
    ret = 'Altimeter '
    if core.is_unknown(alt):
        ret += 'Unknown'
    elif unit == 'inHg':
        ret += numbers(alt[:2]) + ' point ' + numbers(alt[2:])
    elif unit == 'hPa':
        ret += numbers(alt)
    return ret


def other(wxcodes: [str]) -> str:
    """
    Format wx codes into a spoken word string
    """
    ret = []
    for item in wxcodes:
        item = translate.wxcode(item)
        if item.startswith('Vicinity'):
            item = item.lstrip('Vicinity ') + ' in the Vicinity'
        ret.append(item)
    return '. '.join(ret)


def metar(wxdata: {str: object}) -> str:
    """
    Convert wxdata into a string for text-to-speech
    """
    _data = deepcopy(wxdata)
    units = deepcopy(wxdata['Units'])
    speech = []
    if _data['Wind-Direction'] and _data['Wind-Speed']:
        speech.append(wind(_data['Wind-Direction'], _data['Wind-Speed'],
                           _data['Wind-Gust'], _data['Wind-Variable-Dir'],
                           units['Wind-Speed']))
    if _data['Visibility']:
        speech.append(visibility(_data['Visibility'], units['Visibility']))
    if _data['Temperature']:
        speech.append(temperature('Temperature', _data['Temperature'], units['Temperature']))
    if _data['Dewpoint']:
        speech.append(temperature('Dew point', _data['Dewpoint'], units['Temperature']))
    if _data['Altimeter']:
        speech.append(altimeter(_data['Altimeter'], units['Altimeter']))
    if _data['Other-List']:
        speech.append(other(_data['Other-List']))
    speech.append(translate.clouds(_data['Cloud-List'],
                                   units['Altitude']).replace(' - Reported AGL', ''))
    return ('. '.join([l for l in speech if l])).replace(',', '.')
