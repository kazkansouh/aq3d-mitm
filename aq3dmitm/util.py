from enum import IntEnum
import math

def split(lst,d) :
    "split a list on a given delimiter"
    idx = [i for i , z in enumerate(lst) if z == d]
    return [ lst[i+1:j] for i , j in zip([-1] + idx,idx + [len(lst)]) ]

def contains(lst,x) :
    "tests if an element is in a list"
    try :
        return lst.index(x)
    except :
        return -1

def encdec(key,bytes) :
    "applies xor to the bytes"
    for i in range(0,len(bytes)) :
        if bytes[i] != key[i%len(key)] :
            bytes[i] ^= key[i%len(key)]
    return bytes

class LogLevel(IntEnum) :
    Low = 1
    Medium = 2
    High = 3

def distance3d(a,b) :
    return math.sqrt(
        math.pow(a["posX"] - b["posX"],2) +
        math.pow(a["posY"] - b["posY"],2) +
        math.pow(a["posZ"] - b["posZ"],2)
    )
