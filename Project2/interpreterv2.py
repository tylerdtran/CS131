from intbase import InterpreterBase
from type_valuev1 import Type, Value, create_value, get_printable
from brewparse import parse_program
from intbase import ErrorType
from copy import deepcopy

# inherits from the InterpreterBase class
class Interpreter(InterpreterBase): 
    NIL_VALUE = create_value(InterpreterBase.NIL_DEF)

    def __init__(self, console_output=True, inp=None, trace_output=False): 
        super().__init__(console_output, inp)   # call InterpreterBase's constructor
    
    def run(self, program):
        parsed_program = parse_program(program)
        self.set_up_function_table(parsed_program)
        self.variable_name_to_value = {} # this environment is for the main function
        self.variable_stack = [self.variable_name_to_value]
        main_function_node = self.find_main_function()
        self.run_func(main_function_node)
    
    def find_main_function(self): 
        if ("main", 0) in self.func_name_to_ast:
            return self.func_name_to_ast[("main", 0)]
        super().error(ErrorType.NAME_ERROR, "No main() function was found")

    def set_up_function_table(self, parsed_program):  # new one
        self.func_name_to_ast = {}
        for func_def in parsed_program.get("functions"):
            self.func_name_to_ast[(func_def.get("name"), len(func_def.get('args')))] = func_def# add a function definition node into the dictionary list

    def get_func_by_name(self, name): 
        if name not in self.func_name_to_ast:
            super().error(ErrorType.NAME_ERROR, f"Function {name} not found")
        return self.func_name_to_ast[name]
        
    def run_func(self, func_node): 
        if func_node.elem_type == "func": 
            for statement in func_node.dict['statements']: 
                val, return_bool = self.run_statement(statement)
                if return_bool:
                    return val
            self.variable_stack.pop() # need to pop it everytime it exits the function
            return Interpreter.NIL_VALUE
        else: 
            super().error(ErrorType.NAME_ERROR,"Not a proper function node")
        

    def run_statement(self, statement_node): 
        if statement_node.elem_type == "=": # assignment 
            self.do_assignment(statement_node)
        elif statement_node.elem_type == "fcall": # function call 
            self.do_func_call(statement_node)
        elif statement_node.elem_type == "if": 
            
            val = self.check_condition_type(statement_node.dict['condition'])
            
            new_variables = {}
            self.variable_stack.append(new_variables)
            if val:  
                for statement in statement_node.dict['statements']: 
                    val, return_bool = self.run_statement(statement)
                    if return_bool == True: 
                        self.variable_stack.pop() # need to pop it everytime it exits the if statement
                        return val, return_bool 

            elif statement_node.get('else_statements'): # if else statements exist
                for statement in statement_node.dict['else_statements']: 
                    val, return_bool = self.run_statement(statement)
                    if return_bool == True: 
                        self.variable_stack.pop()# need to pop it everytime it exits the if statement
                        return val, return_bool

            self.variable_stack.pop() # need to pop it everytime it exits the if statement

        elif statement_node.elem_type == "while": 
            value = self.check_condition_type(statement_node.dict['condition'])   

            new_variables = {}
            self.variable_stack.append(new_variables)
            while (value):
                for statement in statement_node.dict['statements']: 
                    val, return_bool = self.run_statement(statement)
                    if return_bool == True: 
                        self.variable_stack.pop() # need to pop it everytime it exits the while statement
                        return val, return_bool
                value = self.check_condition_type(statement_node.dict['condition'])
            self.variable_stack.pop() # need to pop it everytime it exits the while statement
                
        elif statement_node.elem_type == "return": 
            if statement_node.dict['expression'] is None: 
                return Interpreter.NIL_VALUE, True
            else: # didn't need a deep copy here
                return self.check_three_types(statement_node.dict['expression']), True
        return Interpreter.NIL_VALUE, False
    
    def check_condition_type(self, condition_node):
        if self.is_expression(condition_node): 
            expr = self.evaluate_expression(condition_node)
            return expr if type(expr) == bool else super().error(ErrorType.TYPE_ERROR, "Not a proper condition statement")
        elif self.is_value_node(condition_node): 
            val = self.get_value_node(condition_node)
            return val if type(val) == bool else super().error(ErrorType.TYPE_ERROR, "Not a proper condition statement")
        elif self.is_variable_node(condition_node):
            var = self.get_value_of_variable_node(condition_node)
            return var if type(var) == bool else super().error(ErrorType.TYPE_ERROR, "Not a proper condition statement")
        else: 
            super().error(ErrorType.TYPE_ERROR, "Not a proper condition statement")

    def do_assignment(self, statement_node): 
        target_var_name = statement_node.dict['name']
        expression_val = statement_node.dict['expression']
        if self.is_expression(expression_val): 
            source_node = self.get_expression_node(statement_node)
            resulting_value = self.evaluate_expression(source_node)
        elif self.is_value_node(expression_val):
            resulting_value = self.get_value_node(expression_val)
        elif self.is_variable_node(expression_val):
            resulting_value = self.get_value_of_variable_node(expression_val)
        else:
            super().error(ErrorType.NAME_ERROR,"Invalid source node")
        
        found_in_parent = False
        for variables in self.variable_stack[::-1]:
            if target_var_name in variables:
                variables[target_var_name] = resulting_value
                found_in_parent = True
                break
        if not found_in_parent:
            self.variable_stack[-1][target_var_name] = resulting_value
    
    def do_func_call(self, call_node): 
        func_name = call_node.get("name")
        val = func_name, len(call_node.get('args'))
        if func_name == "print":
            output_string = ''
            for i in call_node.dict['args']: 
                x = self.check_three_types(i)
                if type(x) == bool:
                    x = str(x).lower()
                output_string += str(x)
            super().output(output_string)
            return Interpreter.NIL_VALUE

        elif func_name == "inputi":
            if len(call_node.dict['args']) > 1:
                super().error(ErrorType.NAME_ERROR,"Invalid number of arguments")
            elif len(call_node.dict['args']) == 1: 
                super().output(self.get_value_node(call_node.dict['args'][0]))
            input_string = super().get_input()
            return int(input_string)
        elif func_name == "inputs": 
            if len(call_node.dict['args']) > 1:
                super().error(ErrorType.NAME_ERROR,"Invalid number of arguments")
            elif len(call_node.dict['args']) == 1: 
                super().output(self.get_value_node(call_node.dict['args'][0]))
            input_string = super().get_input()
            return input_string
        elif (val) in self.func_name_to_ast: 
            func_def = self.get_func_by_name(val)
            func_params_vals = call_node.get('args') # original number values in args 
            return self.call_func_def(func_def, func_params_vals) 
        else: 
            super().error(ErrorType.NAME_ERROR, f"Function {func_name} not found")


    def call_func_def(self, func_def, func_params_vals): 
        parameters = [param.get('name') for param in func_def.get('args')]
        arguments = [self.check_three_types(func_params_vals[arg]) for arg in range(len(func_params_vals))]
        zipped = zip(parameters, arguments)
        func_argument_nodes = {key: value for key, value in zipped}
        self.variable_stack.append(func_argument_nodes)
        for statement in func_def.get("statements"): 
            val, returned = self.run_statement(statement)
            if returned:
                self.variable_stack.pop() # need to pop it everytime it exits the function, this solved the fibonnaci recursion
                return val
        self.variable_stack.pop() # need to pop it everytime it exits the function
        return Interpreter.NIL_VALUE 
        
    ############################### Expressions ########################################
    # a function to evaluate the expressions 
    def evaluate_expression(self, expression_node): 
        if self.is_expression(expression_node):
            if expression_node.elem_type == "fcall":
                return self.do_func_call(expression_node)
            elif expression_node.elem_type in ("neg","!"): # unary operation
                return self.evaluate_unary_operation(expression_node.dict['op1'], expression_node.elem_type)
            elif expression_node.elem_type in ("+", "-", "*", "/"): # binary arithmetic operation
                return self.evaluate_binary_arithmetic_operation(expression_node.dict['op1'], expression_node.dict['op2'], expression_node.elem_type)
            elif expression_node.elem_type in ("==", "<", ">", "<=", ">=", "!=", "&&", "||"): # binary comparison operation
                return self.evaluate_binary_comparison_operation(expression_node.dict['op1'], expression_node.dict['op2'], expression_node.elem_type)
            else: 
                super().error(ErrorType.NAME_ERROR,"Expression action failed")
        else: 
            super().error(ErrorType.NAME_ERROR,"Not a valid expression node")
    
    def operation_type(self, op): 
        if self.is_expression(op): 
            valid_operand = self.evaluate_expression(op)
        elif self.is_value_node(op): 
            valid_operand = self.get_value_node(op)
        elif self.is_variable_node(op):
            valid_operand = self.get_value_of_variable_node(op)
        else: 
            super().error(ErrorType.TYPE_ERROR,"Invalid operand") 
        return valid_operand
    
    def check_three_types(self, node): 
        if self.is_expression(node): 
            return self.evaluate_expression(node)
        elif self.is_value_node(node): 
            return self.get_value_node(node)
        elif self.is_variable_node(node):
            return self.get_value_of_variable_node(node)
        else: 
            super().error(ErrorType.TYPE_ERROR,"Invalid node type")

    def evaluate_unary_operation(self, op1, operator):
        operation_result, valid_operand1 = 0, self.operation_type(op1)
        if operator == "neg" and type(valid_operand1) == int:
            operation_result = -1 * valid_operand1
        elif operator == "!" and type(valid_operand1) == bool: 
            operation_result = not valid_operand1
        else: 
            super().error(ErrorType.TYPE_ERROR, "Not operator used on non-boolean types")
        
        return operation_result
        
    def evaluate_binary_arithmetic_operation(self, op1, op2, operator):
        operation_result, valid_operand1, valid_operand2 = 0, self.operation_type(op1), self.operation_type(op2)
        
        if type(valid_operand1) != type(valid_operand2): 
            super().error(ErrorType.TYPE_ERROR, "Invalid types between operands")
        
        if (type(valid_operand1) and type(valid_operand2)) == str and operator == "+":
            operation_result = valid_operand1 + valid_operand2 
        elif (type(valid_operand1) and type(valid_operand2)) == str:
            super().error(ErrorType.TYPE_ERROR, "String operation doing something other than concatenate")
        else:         
            match operator:
                case "+":
                    operation_result = valid_operand1 + valid_operand2
                case "-":
                    operation_result = valid_operand1 - valid_operand2
                case "*":
                    operation_result = valid_operand1 * valid_operand2
                case "/":
                    operation_result = valid_operand1 // valid_operand2
                case _:
                    super().error(ErrorType.TYPE_ERROR, "Invalid operator")
                    # operation_result = None  # or some other default value
        return operation_result
    
    def evaluate_binary_comparison_operation(self, op1, op2, operator): 
        operation_result, valid_operand1, valid_operand2 = None, self.operation_type(op1), self.operation_type(op2)
        
        if (type(valid_operand1) and type(valid_operand2)) == str: 
            if operator == "==": 
                operation_result = valid_operand1 == valid_operand2
            elif operator == "!=":
                operation_result = valid_operand1 != valid_operand2
            else: 
                super().error(ErrorType.TYPE_ERROR, "Incorrect boolean string operator")
        elif type(valid_operand1) != type(valid_operand2) and operator == "==": 
            return False
        elif type(valid_operand1) != type(valid_operand2) and operator == "!=":  
            return True
        elif (type(valid_operand1) and type(valid_operand2)) == bool and operator in ("<", ">", "<=", ">="):
            super().error(ErrorType.TYPE_ERROR, "boolean values cannot be compared with any other comparison operator")
        elif operator in ("||", "&&") and (type(valid_operand1) != bool and type(valid_operand2) != bool) :
            super().error(ErrorType.TYPE_ERROR, "logical binary operators can only operate on booleans")
        elif type(valid_operand1) != type(valid_operand2):
            super().error(ErrorType.TYPE_ERROR, "illegal to compare values of different types with any other comparison operator")
        else:
            match operator:
                case "<":
                    operation_result = valid_operand1 < valid_operand2
                case ">":
                    operation_result = valid_operand1 > valid_operand2
                case ">=":
                    operation_result = valid_operand1 >= valid_operand2
                case "<=":
                    operation_result = valid_operand1 <= valid_operand2
                case "==":
                    operation_result = valid_operand1 == valid_operand2
                case "!=":
                    operation_result = valid_operand1 != valid_operand2
                case "||":
                    operation_result = valid_operand1 or valid_operand2
                case "&&":
                    operation_result = valid_operand1 and valid_operand2
                case _:
                    super().error(ErrorType.TYPE_ERROR, "Invalid operator")
        
        return operation_result   


    def get_expression_node(self, statement_node): 
        if statement_node.elem_type in ('fcall', '=', '+', '-', '*', '/','==', '<', '<=', '>', '>=', '!=', 'neg', '!'):
            return statement_node.dict['expression'] 
        else: 
            super().error(ErrorType.NAME_ERROR,"Invalid expression node")

    def get_value_node(self, value_node): 
        if self.is_value_node(value_node):
            if value_node.elem_type == "nil":
                return Interpreter.NIL_VALUE
            else:
                return value_node.dict['val']
        else:  
            super().error(ErrorType.NAME_ERROR,"Invalid value node")
            
    def get_value_of_variable_node(self, variable_node): 
        if self.is_variable_node(variable_node):
            for dictionary in self.variable_stack[::-1]:
                if variable_node.get('name') in dictionary.keys() and dictionary[variable_node.get('name')] is not None:
                    return dictionary[variable_node.get('name')]
        
        super().error(ErrorType.NAME_ERROR,"Invalid variable node")

    def is_expression(self, expression_node): 
        if expression_node.elem_type in ('fcall', '=', '+', '-', '*', '/','==', '<', '<=', '>', '>=', '!=', '||', '&&', 'neg', '!'):
            return True
        return False

    def is_value_node(self, value_node): 
        if value_node.elem_type in ("int", "string", "bool", "nil"):
            return True
        return False

    def is_variable_node(self, variable_node):
        if variable_node.elem_type == "var": 
            return True
        return False

    
def main():
    program_source = """
                            func main() {
                            print(fib(5));
                            }

                            func fib(n) {
                            if (n < 3) {
                            return 1;
                            } else {
                            return fib(n-2) + fib(n-1);
                            }
                            }
                        """

    
  # this is how you use our parser to parse a valid Brewin program into
  # an AST:
    interpreter = Interpreter()
    interpreter.run(program_source)

if __name__ == "__main__":
    main()