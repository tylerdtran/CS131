from intbase import InterpreterBase
from brewparse import parse_program
from intbase import ErrorType

# inherits from the InterpreterBase class
class Interpreter(InterpreterBase): 
    def __init__(self, console_output=True, inp=None, trace_output=False): 
        super().__init__(console_output, inp)   # call InterpreterBase's constructor
        

    # must implement at least the constructor and the run method 
    def run(self, program):
        parsed_program = parse_program(program)
        # get the main function node
        self.variable_name_to_value = {}
        main_function_node = self.find_main_function(parsed_program)
        # run the main function node
        self.run_func(main_function_node)
    
    # Helper function for starting the execution for main
    def find_main_function(self, program_node): 
        """
        This function should retrieve and return the main function node. Which in it of itself is a function node
        """
        if program_node.elem_type == "program" and program_node.dict['functions'][0].dict['name'] == "main":
            return program_node.dict['functions'][0] # passes down a function node that the program node had in its dictionary
        # need to check if it's main as well 
        else:
            super().error(ErrorType.NAME_ERROR,"No main() function was found")
        
        
    # Helper function for starting the execution for main
    # a function to run the functions
    def run_func(self, func_node): 
        if func_node.elem_type == "func": 
            for statement in func_node.dict['statements']: 
                self.run_statement(statement)
        else: 
            super().error(ErrorType.NAME_ERROR,"Not a proper function node")
        # pass

    # a function to run the statements 
    def run_statement(self, statement_node): 
        if statement_node.elem_type == "=":       # assignment 
            self.do_assignment(statement_node)
        elif statement_node.elem_type == "fcall": # function call 
            self.do_func_call(statement_node)
        else:
            super().error(ErrorType.NAME_ERROR,"Invalid statement node")
    
    # a function to perform the assignments 
    def do_assignment(self, statement_node): 
        # this statement node returns "="
        # check if it is a variable node or a value node or an expression node
        # if it is an expression node of a binary operation 
        # if assignment_node.elem_type == '+' or assignment_node.elem_type == '-': 
        target_var_name = statement_node.dict['name']
        # source_node = self.get_expression_node(statement_node.dict['expression'])# this could be either the evaluated expression node, a variable node, or a value node
        if self.is_expression(statement_node.dict['expression']): 
            source_node = self.get_expression_node(statement_node)
            resulting_value = self.evaluate_expression(source_node)
        elif self.is_value_node(statement_node.dict['expression']):
            resulting_value = self.get_value_node(statement_node.dict['expression'])
        elif self.is_variable_node(statement_node.dict['expression']):
            resulting_value = self.get_value_of_variable_node(statement_node.dict['expression'])
        else:
            super().error(ErrorType.NAME_ERROR,"Invalid source node")
        self.variable_name_to_value[target_var_name] = resulting_value
    
    # the function call evaluation could be a statement node or an expression node of 'fcall' type because they both have the same dictionary value 'args'
    def do_func_call(self, statement_node): 
        # a list of zero or more expression nodes, variable nodes, or value nodes
        if statement_node.elem_type == "fcall":
            if statement_node.dict['name'] == "print":
                output_string = ''
                for i in statement_node.dict['args']: 
                    x = i
                    if self.is_expression(x): 
                        x = self.evaluate_expression(i)
                    elif self.is_value_node(x): 
                        x = self.get_value_node(i)
                    elif self.is_variable_node(x):
                        x = self.get_value_of_variable_node(i)
                    output_string += str(x) # no spaces
                super().output(output_string)
            elif statement_node.dict['name'] == "inputi":
                if len(statement_node.dict['args']) > 1:
                    super().error(ErrorType.NAME_ERROR,"Invalid number of arguments")
                elif len(statement_node.dict['args']) == 1: 
                    super().output(self.get_value_node(statement_node.dict['args'][0]))
                input_string = int(super().get_input())
                # successfully takes the input
                # self.variable_name_to_value[statement_node.dict['args'][0]] = int(input_string)
                return input_string
            else: 
               super().error(ErrorType.NAME_ERROR,"Invalid function name") 
        else: 
            super().error(ErrorType.NAME_ERROR,"statement node is not of type fcall")

        
    ############################### Expressions ########################################
    # a function to evaluate the expressions 
    def evaluate_expression(self, expression_node): 
        # if it is an expression in the first place
        # function call
        # also contains a list of zero or more expression nodes, variable nodes, or value nodes
        if self.is_expression(expression_node):
            if expression_node.elem_type == "fcall":
                if expression_node.dict['name'] != "inputi": 
                    super().error(ErrorType.NAME_ERROR, "Can only assign an inputi function to the right")
                return self.do_func_call(expression_node)
                # print(expression_node)
                # return self.do_func_call(expression_node) # passses all of the other input test cases: test_input1, test_input2, test_input3
                # return self.do_func_call(expression_node) # this code allows test_input to work but not any other input test case
        # binary operator 
        # two keys op1 and op2
            elif expression_node.elem_type == "+" or expression_node.elem_type == "-": 
                return self.evaluate_binary_operation(expression_node.dict['op1'], expression_node.dict['op2'], expression_node.elem_type)

            else: 
                super().error(ErrorType.NAME_ERROR,"Expression action failed")
        else: 
            super().error(ErrorType.NAME_ERROR,"Not a valid expression node")
        
    def evaluate_binary_operation(self, op1, op2, operator):
        operation_result, valid_operand1, valid_operand2 = 0, 0, 0
        if self.is_expression(op1): 
            valid_operand1 = self.evaluate_expression(op1)
        elif self.is_value_node(op1): 
            valid_operand1 = self.get_value_node(op1)
        elif self.is_variable_node(op1):
            valid_operand1 = self.get_value_of_variable_node(op1)
        else: 
            super().error(ErrorType.TYPE_ERROR,"Invalid 1st operand")
        
        if self.is_expression(op2): 
            valid_operand2 = self.evaluate_expression(op2)
        elif self.is_value_node(op2): 
            valid_operand2 = self.get_value_node(op2)
        elif self.is_variable_node(op2):
            valid_operand2 = self.get_value_of_variable_node(op2)
        else: 
            super().error(ErrorType.TYPE_ERROR,"Invalid 2nd operand")   
        
        # print(type(valid_operand1), type(valid_operand2))

        if type(valid_operand1) != type(valid_operand2): 
            super().error(ErrorType.TYPE_ERROR, "Invalid types between operands")

        if operator == "+":
            try: 
                operation_result = valid_operand1 + valid_operand2
            except: 
                super().error(ErrorType.TYPE_ERROR,"Invalid operation") 
        elif operator == "-":
            try: 
                operation_result = valid_operand1 - valid_operand2
            except: 
                super().error(ErrorType.TYPE_ERROR,"Invalid operation") 
        else: 
            super().error(ErrorType.TYPE_ERROR,"Invalid operator")
        
        return operation_result
    
    # Still need to do actual variable assignment???
    
    # a set of functions to get the expression node

    def get_expression_node(self, statement_node): 
        if statement_node == "+" or statement_node == "-" or statement_node == "fcall": 
            return statement_node['expression']
        ## TEMPORARY ## ADDING RETURN FOR VARIABLE NODES OR VALUE NODES
        elif statement_node.elem_type == "=": 
            return statement_node.dict['expression']
        else: 
            super().error(ErrorType.NAME_ERROR,"Invalid expression node")

    def get_value_node(self, value_node): 
        # value node
        if value_node.elem_type == "int" or value_node.elem_type == "string":
            return value_node.dict['val']
        else:  
            # raise Exception("Error: Not a value node")
            # super().error(ErrorType.NAME_ERROR,"Invalid value node")
            super().error(ErrorType.NAME_ERROR,"Invalid value node")
            
    def get_value_of_variable_node(self, variable_node): 
        # variable node
        if variable_node.elem_type == "var": 
            # print(self.variable_name_to_value[variable_node.dict['name']])
            # if self.variable_name_to_value[variable_node.dict['name']]: # this accounts for if the variable exists in the first place, otherwise return an error
            try: 
                value = self.variable_name_to_value[variable_node.dict['name']]
            # return variable_node.dict['name']
                if value: 
                    return value
            except:
                super().error(ErrorType.NAME_ERROR, f"Variable {variable_node.dict['name']} has not been defined")
        else: 
            super().error(ErrorType.NAME_ERROR,"Invalid variable node")

    ###### Helper functions to check the type of the node ######
    def is_expression(self, expression_node): 
        if expression_node.elem_type == "+" or expression_node.elem_type == "-" or expression_node.elem_type == "fcall": 
            return True
        else: 
            return False
        
    def is_value_node(self, value_node): 
        if value_node.elem_type == "int" or value_node.elem_type == "string":
            return True
        else: 
            return False
        

    def is_variable_node(self, variable_node):
        if variable_node.elem_type == "var": 
            return True
        else: 
            return False

    
def main():
# all programs will be provided to your interpreter as a list of # python strings, just as shown here.
    program_source = """func main() {
                            a = inputi("this", "is a test");  
                            }
    """
    # program_source = """func main() {
    #                         x = inputi("enter a num:");
    #                         print(x);
    # }"""
    # program_source = """func main() {
    #                         foo = inputi("enter first #: ") + inputi("enter second #: ");
    #                         print(foo);
    # }"""



    
  # this is how you use our parser to parse a valid Brewin program into
  # an AST:
    interpreter = Interpreter()
    interpreter.run(program_source)

if __name__ == "__main__":
    main()

