import copy

from enum import Enum
from intbase import InterpreterBase, ErrorType



# Enumerated type for our different language data types
class Type(Enum):
    INT = 1
    BOOL = 2
    STRING = 3
    CLOSURE = 4
    NIL = 5
    OBJECT = 6


class Closure:
    def __init__(self, func_ast, env):
        # self.captured_env = copy.deepcopy(env)
        # print("env: ", env)
        if env is None:
            self.captured_env = {}
        else: 
            self.captured_env = {}
            for var, value in env.__iter__():
                if isinstance(value, Value) and value.t in (Type.OBJECT, Type.CLOSURE):
                    self.captured_env[var] = value
                else:
                    self.captured_env[var] = copy.deepcopy(value)
        self.func_ast = func_ast
        self.type = Type.CLOSURE

class Object: 
    def __init__(self):
        self.fields = {}
        self.type = Type.OBJECT
        self.proto = None

    def value(self):
        return self
    
    # def type(self): 
    #     return self.type

    def get_field(self, name):
        if name in self.fields and self.fields[name] is not None:
                return self.fields[name]
        elif self.proto is not None: 
            # print("proto: ", self.proto.value().get_field(name))
            return self.proto.get_field(name)
        else:
            return None
    # def get_field(self, name):  
    #     current_obj = self 
    #     # while current_obj.proto is not None and current_obj.proto.value() is not None:
    #     while current_obj.proto is not None :
    #         if name in current_obj.fields and current_obj.fields[name] is not None:
    #             return current_obj.fields[name]
    #         # current_obj = current_obj.proto.value()
    #         if current_obj.proto is not None:
    #             current_obj = current_obj.proto.value()
    #     return None
            # val = prototype.fields.get(name)
            # if val is not None:
            #     prototype = prototype.proto
            #     return val
            # else: 
            #     return None

    # def get_field(self, name):
    #     if self.fields.get(name) is None:
    #         prototype = self.proto
    #         while prototype is not None:
    #             val = prototype.fields.get(name)
    #             if val is not None:
    #                 prototype = prototype.proto
    #                 return val
    #             else: 
    #                 return None
    #     else:
    #         return self.fields.get(name)

    def set_field(self, name, value):
        if name == 'proto':
            self.proto = value.value()
        else:
            self.fields[name] = value
    
    

# Represents a value, which has a type and its value
class Value:
    def __init__(self, t, v=None):
        self.t = t
        self.v = v

    def value(self):
        return self.v

    def type(self):
        return self.t

    def set(self, other):
        self.t = other.t
        self.v = other.v


# def create_value(val):
#     if val == InterpreterBase.TRUE_DEF:
#         return Value(Type.BOOL, True)
#     elif val == InterpreterBase.FALSE_DEF:
#         return Value(Type.BOOL, False)
#     elif isinstance(val, str):
#         return Value(Type.STRING, val)
#     elif isinstance(val, int):
#         return Value(Type.INT, val)
#     elif val == InterpreterBase.NIL_DEF:
#         return Value(Type.NIL, None)
#     else:
#         raise ValueError("Unknown value type")
def create_value(val):
    if val == InterpreterBase.TRUE_DEF:
        return Value(Type.BOOL, True)
    elif val == InterpreterBase.FALSE_DEF:
        return Value(Type.BOOL, False)
    elif isinstance(val, int):
        return Value(Type.INT, val)
    elif val == InterpreterBase.NIL_DEF:
        return Value(Type.NIL, None)
    elif isinstance(val, str):
        return Value(Type.STRING, val)
    else:
        raise ValueError("Unknown value type")
    
def get_printable(val):
    if val.type() == Type.INT:
        return str(val.value())
    if val.type() == Type.STRING:
        return val.value()
    if val.type() == Type.BOOL:
        if val.value() is True:
            return "true"
        return "false"
    return None
