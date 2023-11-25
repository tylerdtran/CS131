import copy
from enum import Enum

from brewparse import parse_program
from env_v2 import EnvironmentManager
from intbase import InterpreterBase, ErrorType
from type_valuev2 import Type, Value, create_value, get_printable, Lambda


class ExecStatus(Enum):
    CONTINUE = 1
    RETURN = 2


# Main interpreter class
class Interpreter(InterpreterBase):
    # constants
    NIL_VALUE = create_value(InterpreterBase.NIL_DEF)
    TRUE_VALUE = create_value(InterpreterBase.TRUE_DEF)
    BIN_OPS = {"+", "-", "*", "/", "==", "!=", ">", ">=", "<", "<=", "||", "&&"}

    # methods
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output
        self.__setup_ops()

    # run a program that's provided in a string
    # usese the provided Parser found in brewparse.py to parse the program
    # into an abstract syntax tree (ast)
    def run(self, program):
        ast = parse_program(program)
        self.__set_up_function_table(ast)
        self.env = EnvironmentManager()
        main_func = self.__get_func_by_name("main", 0)
        self.__run_statements(main_func.get("statements"))

    def __set_up_function_table(self, ast):
        self.func_name_to_ast = {}
        for func_def in ast.get("functions"):
            func_name = func_def.get("name")
            num_params = len(func_def.get("args"))
            if func_name not in self.func_name_to_ast:
                self.func_name_to_ast[func_name] = {}
            self.func_name_to_ast[func_name][num_params] = func_def

    def __get_func_by_name(self, name, num_params):
        if name not in self.func_name_to_ast:
            super().error(ErrorType.NAME_ERROR, f"Function {name} not found")
        candidate_funcs = self.func_name_to_ast[name]
        if num_params not in candidate_funcs:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Function {name} taking {num_params} params not found",
            )
        return candidate_funcs[num_params]

    def __run_statements(self, statements):
        self.env.push()
        # print(statements)
        for statement in statements:
            if self.trace_output:
                print(statement)
            status = ExecStatus.CONTINUE
            if statement.elem_type == InterpreterBase.FCALL_DEF:
                self.__call_func(statement)
            elif statement.elem_type == "=":
                self.__assign(statement)
            elif statement.elem_type == InterpreterBase.RETURN_DEF:
                status, return_val = self.__do_return(statement)
            elif statement.elem_type == Interpreter.IF_DEF:
                status, return_val = self.__do_if(statement)
            elif statement.elem_type == Interpreter.WHILE_DEF:
                status, return_val = self.__do_while(statement)

            if status == ExecStatus.RETURN:
                self.env.pop()
                return (status, return_val)

        self.env.pop()
        return (ExecStatus.CONTINUE, Interpreter.NIL_VALUE)

    def __call_func(self, call_node):
        is_lambda = False

        func_name = call_node.get("name")
        if func_name == "print":
            return self.__call_print(call_node)
        if func_name == "inputi":
            return self.__call_input(call_node)
        if func_name == "inputs":
            return self.__call_input(call_node)
        
        # print(call_node)
        actual_args = call_node.get("args") # same as carey, actual argument parameters 
        # print(actual_args)
        var_name = call_node.get("name") # here we are trying to retrieve the function name 
        # print(var_name, "FOO") 
        func_node = self.env.get(var_name) # val is retrieving this value from the environment, if it returns none,
        # print(type(func_node))
        # we see that there is a val, and it contains a function node assigned to a.  
        if func_node is None: # this will be none if there's no function in the function table
            # this sector will only be called if the function is not assigned to a variable.  
            func_ast = self.__get_func_by_name(func_name, len(actual_args)) # if we have no further value in val, then we can assume that the function is not assigned to a variable
            formal_args = func_ast.get("args")
        elif func_node and not isinstance(func_node, Value): # if the function is not a value, then it is a function
            func_name = func_node.get("name")
            func_ast = self.__get_func_by_name(func_name, len(actual_args))
            formal_args = func_ast.get("args")
        elif func_node: # if the function is a value, then we need to check if it is a function or a lambda
       # if the function is not found in the local environment, look a level deeper
            if func_node.type() == Type.LAMBDA:
                is_lambda = True
                func_ast = func_node.value().ast
                formal_args = func_ast.get("args")
            elif func_node.type() == Type.FUNCTION:  # Assuming FUNC_DEF is another type defined in your Type Enum
                func_name = func_node.value.get("name")
                func_ast = self.__get_func_by_name(func_name, len(actual_args))
                formal_args = func_ast.get("args")
            elif func_node.type() == Type.NIL:  # Assuming FUNC_DEF is another type defined in your Type Enum
                func_name = func_node.value
                func_ast = self.__get_func_by_name(func_name, len(actual_args))
                formal_args = func_ast.get("args")
            else:
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Expected func_node to be an instance of Value",
                )
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Expected func_node to be an instance of Value!",
            )

        if len(actual_args) != len(formal_args):
            super().error(
                ErrorType.TYPE_ERROR,
                f"Function {func_ast.get('name')} with {len(actual_args)} args not found",
            )
        # func = self.__get_func_by_name(call_node.get("name"), len(call_node.get("args")))
        # is_lambda = isinstance(func, Lambda)
        # print(func_node.value().ast, "FUNC NODE VALUE")
        if is_lambda: 
            self.env.push_with_env(func_node.value().env)
        else: 
            self.env.push()

        ref_dict = {}
        for formal_ast, actual_ast in zip(formal_args, actual_args):
            arg_name = formal_ast.get("name")
            if formal_ast.elem_type == InterpreterBase.REFARG_DEF:
                var_name = actual_ast.get("name")
                var_ref = self.env.get(var_name)
                if var_ref is None:
                    super().error(ErrorType.NAME_ERROR, f"Variable {var_name} not found")
                self.env.create(arg_name, var_ref)
                ref_dict[arg_name] = var_name  # store the mapping between the reference and the variable it points to
            else:
                result = copy.deepcopy(self.__eval_expr(actual_ast))
                self.env.create(arg_name, result)

        _, return_val = self.__run_statements(func_ast.get("statements"))

        for ref_name, var_name in ref_dict.items():  # update the values of the variables that the references point to
            ref_val = self.env.get(ref_name)
            if ref_val is not None:
                self.env.set(var_name, ref_val)

        self.env.pop()  # discard the function's environment

        return return_val



    def __call_print(self, call_ast):
        output = ""
        for arg in call_ast.get("args"):
            result = self.__eval_expr(arg)  # result is a Value object
            if result == Interpreter.NIL_VALUE:
                result = Value(Type.NIL, None)
            output = output + get_printable(result)
        super().output(output)
        return Interpreter.NIL_VALUE

    def __call_input(self, call_ast):
        args = call_ast.get("args")
        if args is not None and len(args) == 1:
            result = self.__eval_expr(args[0])
            super().output(get_printable(result))
        elif args is not None and len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR, "No inputi() function that takes > 1 parameter"
            )
        inp = super().get_input()
        if call_ast.get("name") == "inputi":
            return Value(Type.INT, int(inp))
        if call_ast.get("name") == "inputs":
            return Value(Type.STRING, inp)

    def __assign(self, assign_ast): 
        var_name = assign_ast.get("name")
        value_obj = self.__eval_expr(assign_ast.get("expression"))
        existing_var = self.env.get(var_name) 
        # print(existing_var, "EXISTING VAR")
        if existing_var is not None: # it won't be none if there is a function 
            # If it does, update its value
            if isinstance(value_obj, Value): # need to check whether or not it is a function
                # print(existing_var.value)
                existing_var.value = value_obj.value
            else: 
                existing_var.value = value_obj # if it is a function, we need to update the value of the function

        else:
            # If it doesn't, create a new variable
            self.env.create(var_name, value_obj)

    def __eval_expr(self, expr_ast):
        if expr_ast.elem_type == InterpreterBase.NIL_DEF:
            # print("getting as nil")
            return Interpreter.NIL_VALUE
        if expr_ast.elem_type == InterpreterBase.INT_DEF:
            return Value(Type.INT, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.STRING_DEF:
            # print("getting as str")
            return Value(Type.STRING, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.BOOL_DEF:
            return Value(Type.BOOL, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.LAMBDA_DEF:
            env_copy = copy.deepcopy(self.env)
            flattened_env = env_copy.flatten()
            lambda_obj = Lambda(flattened_env, expr_ast)

            # Return a new Value object that holds the Lambda object
            return Value(Type.LAMBDA, lambda_obj)
        if expr_ast.elem_type == InterpreterBase.VAR_DEF:
            var_name = expr_ast.get("name")
            print(var_name, "VAR NAME") 
            func_node = self.env.get(var_name) 
            print(func_node, "FUNC NODE")
            if func_node is None: # if it isn't found, don't freak out yet, it might be a function in the function table
                # print("It made it here") 
                # print(var_name)
                if var_name not in self.func_name_to_ast:
                    super().error(ErrorType.NAME_ERROR, f"Variable {var_name} not found")
                result = self.func_name_to_ast[var_name]
                key = list(result.keys())[0]
                if len(result) != 1:
                    super().error(ErrorType.NAME_ERROR, f"More than one function of type:{var_name} attempting to be assigned")
                func_node = self.__get_func_by_name(var_name, key)
                # except: 
                #     super().error(ErrorType.NAME_ERROR, f"Variable function {var_name} not found")
            return func_node
        if expr_ast.elem_type == InterpreterBase.FCALL_DEF:
            return self.__call_func(expr_ast)
        if expr_ast.elem_type in Interpreter.BIN_OPS:
            return self.__eval_op(expr_ast)
        if expr_ast.elem_type == Interpreter.NEG_DEF:
            return self.__eval_unary(expr_ast, Type.INT, lambda x: -1 * x)
        if expr_ast.elem_type == Interpreter.NOT_DEF:
            return self.__eval_unary(expr_ast, Type.BOOL, lambda x: not x)

    def __eval_op(self, arith_ast):
        left_value_obj = self.__eval_expr(arith_ast.get("op1"))
        right_value_obj = self.__eval_expr(arith_ast.get("op2"))

        # print(left_value_obj)
        # print(right_value_obj)
        # Use of any comparison operator other than == and != on a variable holding a function/closure must result in an error of ErrorType.TYPE_ERROR.
        # print("It made it here")
        if arith_ast.elem_type in ("==", "!="):
        # Handle function comparison
            if not isinstance(left_value_obj, Value):
                if left_value_obj == Interpreter.NIL_VALUE or left_value_obj.elem_type == "func":
                    if arith_ast.elem_type == "==":
                        if left_value_obj == right_value_obj: 
                            return Value(Type.BOOL, True)
                        return Value(Type.BOOL, False)
                    else:  # arith_ast.elem_type == "!="
                        if left_value_obj != right_value_obj:
                            return Value(Type.BOOL, True)
                        return Value(Type.BOOL, False)
            elif not isinstance(right_value_obj, Value):
                if right_value_obj == Interpreter.NIL_VALUE or right_value_obj.elem_type == "func":
                    if arith_ast.elem_type == "==":
                        if left_value_obj == right_value_obj: 
                            return Value(Type.BOOL, True)
                        return Value(Type.BOOL, False)
                    else:
                        if left_value_obj != right_value_obj:
                            return Value(Type.BOOL, True)
                        return Value(Type.BOOL, False)

        # # at this point if either of them are not values, we can assume that they are functions
        if not isinstance(left_value_obj, Value) or not isinstance(right_value_obj, Value):
            super().error(
                ErrorType.TYPE_ERROR,
                f"Cannot perform operation on function",
            )

        
        # ========= DEBUG =========
        # Coerce boolean to integer for arithmetic operations
        if arith_ast.elem_type in ['+', '-', '*', '/']:
            if left_value_obj.type() == Type.BOOL:
                left_value_obj = Value(Type.INT, 1 if left_value_obj.value() == True else 0)
            if right_value_obj.type() == Type.BOOL:
                right_value_obj = Value(Type.INT, 1 if right_value_obj.value() == True else 0)
        
        if arith_ast.elem_type in ("==", "!=", "&&", "||"):
            if left_value_obj.type() == Type.INT: 
                left_value_obj = Value(Type.BOOL, True if left_value_obj.value() != 0 else False)
            if right_value_obj.type() == Type.INT:
                right_value_obj = Value(Type.BOOL, True if right_value_obj.value() != 0 else False)
        # ========= DEBUG =========


        # print(left_value_obj.value(), right_value_obj.value())

        if not self.__compatible_types(
            arith_ast.elem_type, left_value_obj, right_value_obj
        ):
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible types for {arith_ast.elem_type} operation",
            )
        
        if arith_ast.elem_type not in self.op_to_lambda[left_value_obj.type()]:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible operator {arith_ast.elem_type} for type {left_value_obj.type()}",
            )
        f = self.op_to_lambda[left_value_obj.type()][arith_ast.elem_type]
        return f(left_value_obj, right_value_obj)
        

    def __compatible_types(self, oper, obj1, obj2):
        # DOCUMENT: allow comparisons ==/!= of anything against anything
        if oper in ["==", "!="]:
            return True
        return obj1.type() == obj2.type()

    def __eval_unary(self, arith_ast, t, f):
        value_obj = self.__eval_expr(arith_ast.get("op1"))
        # Unary might be wrong tho: negative vs. ! if it is ! then we convert int to bool
        if not isinstance(value_obj, Value):
            super().error(
                ErrorType.TYPE_ERROR,
                f"Cannot perform unary operation on function",
            )

        if value_obj.type() == Type.INT and arith_ast.elem_type == Interpreter.NOT_DEF:
            value_obj = Value(Type.BOOL, True if value_obj.value() != 0 else False)
        if value_obj.type() != t:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible type for {arith_ast.elem_type} operation",
            )
        return Value(t, f(value_obj.value()))

    def __setup_ops(self):
        self.op_to_lambda = {}
        # set up operations on integers
        self.op_to_lambda[Type.INT] = {}
        self.op_to_lambda[Type.INT]["+"] = lambda x, y: Value(
            x.type(), x.value() + y.value()
        )
        self.op_to_lambda[Type.INT]["-"] = lambda x, y: Value(
            x.type(), x.value() - y.value()
        )
        self.op_to_lambda[Type.INT]["*"] = lambda x, y: Value(
            x.type(), x.value() * y.value()
        )
        self.op_to_lambda[Type.INT]["/"] = lambda x, y: Value(
            x.type(), x.value() // y.value()
        )
        self.op_to_lambda[Type.INT]["=="] = lambda x, y: Value(
            Type.BOOL, x.type() == y.type() and x.value() == y.value()
        )
        self.op_to_lambda[Type.INT]["!="] = lambda x, y: Value(
            Type.BOOL, x.type() != y.type() or x.value() != y.value()
        )
        self.op_to_lambda[Type.INT]["<"] = lambda x, y: Value(
            Type.BOOL, x.value() < y.value()
        )
        self.op_to_lambda[Type.INT]["<="] = lambda x, y: Value(
            Type.BOOL, x.value() <= y.value()
        )
        self.op_to_lambda[Type.INT][">"] = lambda x, y: Value(
            Type.BOOL, x.value() > y.value()
        )
        self.op_to_lambda[Type.INT][">="] = lambda x, y: Value(
            Type.BOOL, x.value() >= y.value()
        )
        #  set up operations on strings
        self.op_to_lambda[Type.STRING] = {}
        self.op_to_lambda[Type.STRING]["+"] = lambda x, y: Value(
            x.type(), x.value() + y.value()
        )
        self.op_to_lambda[Type.STRING]["=="] = lambda x, y: Value(
            Type.BOOL, x.value() == y.value()
        )
        self.op_to_lambda[Type.STRING]["!="] = lambda x, y: Value(
            Type.BOOL, x.value() != y.value()
        )
        #  set up operations on bools
        self.op_to_lambda[Type.BOOL] = {}
        self.op_to_lambda[Type.BOOL]["&&"] = lambda x, y: Value(
            x.type(), x.value() and y.value()
        )
        self.op_to_lambda[Type.BOOL]["||"] = lambda x, y: Value(
            x.type(), x.value() or y.value()
        )
        self.op_to_lambda[Type.BOOL]["=="] = lambda x, y: Value(
            Type.BOOL, x.type() == y.type() and x.value() == y.value()
        )
        self.op_to_lambda[Type.BOOL]["!="] = lambda x, y: Value(
            Type.BOOL, x.type() != y.type() or x.value() != y.value()
        )

        #  set up operations on nil
        self.op_to_lambda[Type.NIL] = {}
        self.op_to_lambda[Type.NIL]["=="] = lambda x, y: Value(
            Type.BOOL, x.type() == y.type() and x.value() == y.value()
        )
        self.op_to_lambda[Type.NIL]["!="] = lambda x, y: Value(
            Type.BOOL, x.type() != y.type() or x.value() != y.value()
        )

        #  set up operations on lambdas
        self.op_to_lambda[Type.LAMBDA] = {}
        self.op_to_lambda[Type.LAMBDA]["=="] = lambda x, y: Value(
            Type.BOOL, x.type() == y.type() and x.value() == y.value()
        )
        self.op_to_lambda[Type.LAMBDA]["!="] = lambda x, y: Value(
            Type.BOOL, x.type() != y.type() or x.value() != y.value()
        )

    def __do_if(self, if_ast):
        cond_ast = if_ast.get("condition")
        result = self.__eval_expr(cond_ast)

        if result.type() == Type.INT:
            result = Value(Type.BOOL, True if result.value() != 0 else False)

        if result.type() != Type.BOOL:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible type for if condition",
            )
        if result.value():
            statements = if_ast.get("statements")
            status, return_val = self.__run_statements(statements)
            return (status, return_val)
        else:
            else_statements = if_ast.get("else_statements")
            if else_statements is not None:
                status, return_val = self.__run_statements(else_statements)
                return (status, return_val)

        return (ExecStatus.CONTINUE, Interpreter.NIL_VALUE)

    def __do_while(self, while_ast):
        cond_ast = while_ast.get("condition")
        run_while = Interpreter.TRUE_VALUE
        while run_while.value():
            run_while = self.__eval_expr(cond_ast)
            if run_while.type() == Type.INT:
                run_while = Value(Type.BOOL, True if run_while.value() != 0 else False)
            if run_while.type() != Type.BOOL:
                super().error(
                    ErrorType.TYPE_ERROR,
                    "Incompatible type for while condition",
                )
            if run_while.value():
                statements = while_ast.get("statements")
                status, return_val = self.__run_statements(statements)
                if status == ExecStatus.RETURN:
                    return status, return_val

        return (ExecStatus.CONTINUE, Interpreter.NIL_VALUE)

    def __do_return(self, return_ast):
        expr_ast = return_ast.get("expression")
        if expr_ast is None:
            return (ExecStatus.RETURN, Interpreter.NIL_VALUE)
        value_obj = copy.deepcopy(self.__eval_expr(expr_ast))
        return (ExecStatus.RETURN, value_obj)



def main(): 
    ### NEED TO SET THE LAMBDA VARIABLE ENVIRONMENT, NEED TO FIX THE WAY I QUERY FOR VARIABLES 
    # element not callable 
    # BUG NEED TO FIX
    # program_source = """func foo() {
    #                             print(y);   /* generates an ErrorType.NAME_ERROR */
    #                             }

    #                             func bar() {
    #                             y = 10;
    #                             x = foo;    /* y is not captured by this assignment */
    #                             }

    #                             func main() {
    #                             x = nil;
    #                             bar();
    #                             x();
    #                             }"""
    # bad scope 
    # supposed to give a name error 
    # program_source = """func foo() {
    #                             print(y);  
    #                             print(b); 
    #                             }

    #                             func bar() {
    #                             y = 10;
    #                             b = 100;
    #                             x = foo;
    #                             }

    #                             func main() {
    #                             x = 100;
    #                             bar();
    #                             x();
    #                             }"""

    # program_source = """    func main() {
    #                             x = 10;
    #                             increment = lambda(ref x) { x = x + 1; return x; };
    #                             y = increment(x); 
    #                             print(x);  
    #                             print(y);  
    #                         }"""
    # doesn't work because function f isn't a function
    # program_source = """func main() {
    #                         f = 5;

    #                         f(20); 
    #                         }"""
    # # REF5
    program_source = """func bar() {
                                print("in bar");
                                }

                                func foo(ref x) {
                                    x = 10;
                                    x = bar;
                                }

                                func main() {

                                    x = nil;
                                    foo(x);
                                    x();
                                }"""
    # func 3
    # program_source = """func main() {
    #                                 x = nil;
    #                                 x();
    #                                 }"""

    #                                 /* should return TypeError */"""
    ## Supposed to throw a name error
    # program_source = """func bar() {
    #                                 print("in bar");
    #                                 }

    #                                 func foo(ref x) {
    #                                     x = bar;
    #                                     x = 10;
    #                                 }

    #                                 func main() {
    #                                     x = nil;
    #                                     foo(x);
    #                                     x();
    #                                 }
    #                             """
                             

    
    interpreter = Interpreter()
    interpreter.run(program_source)

if __name__ == "__main__":
    main()