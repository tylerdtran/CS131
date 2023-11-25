
### 1. 
data List = Node Int List | Nil deriving Show

a.) 
delete :: List -> Int -> List 

b.) 
```Haskell
delete Nil _ = Nil 
delete (Node val next) n 
    | val == n = delete next n 
    | otherwise = Node val (delete next n) -- otherwise keep it and check if the next one is deleteable because next will represent the entire Node 
```
-- Essentially it generates a whole new tree and only keeps the node if it isn't next. 
c.) 
3 since you need to regenerate 17, 5, 10,

SOLUTION: 
Based on how pattern matching works here, all new nodes need to be recreated in this linked list data structure. 

### 3. 
a.) 
This occurs because C++ is weakly typed. so such undefined behavior doesn't necessarily guaranteed that all operations are invoked on objects/values of appropriate type. In printStuff we are casting the void pointer as a char pointer which might not have any semantic meaning in the context of our program. 


b.) 
printStuff's implementation appears to use a cast. It appears that when we assign the char pointer to void, we are essentially have the compiler interpret the void pointer as a char pointer but not actually having it convert it into a different variable type. 

### 4.
a.) INCORRECT
If it is statically typed, I believe that it will print an error since statically typed languages don't allow for the reassignment of a different variable type. Throughout the variable's lifetime. If we attempt to run our program, the compiler will give us an error for trying to assign the variable originally with a floating pointer value to an int. 

SOLUTION: 
Here the type float is actually being assigned based on type inference. When an integer 42 is assigned to it later, the statically typed language will cast the value as a float in order to preserve the float's type., it doesn't throw an error because it can be represented from int -> float. If it were a float to a string it would through a compile error. 

42.0 
v's type: Float 

b.) #CORRECT 
If it is dynamically typed, I think that the program will properly run and print: 
42 
v's type: Int
Types can change at Runtime

c.) INCORRECT
I would expect a type coercion to occur for neither language, because here we aren't trying to take a value and reinterpret its type, rather we are trying to change the type of the variable itself. Thus, no type coercion is occurring in this program. 

SOLUTION: 
If the language were statically typed, we can expect the language to perform type coercion 

d.) CORRECT
It is using type inference to determine the type of v variable v when it is defined, since it is floating pointer number assigned and so it can infer that the variable v is of type float. 

### 5.

Based on definition of a subtype in class: 
Every element belonging to the set of values of type Tsub is also a member of the set of values of type Tsuper 
Requirement #2: All operations (e.g. +, -, *, /) that you can use on a value of type Tsuper must also work properly on a value of type Tsub. 

I believe that an int is not a subtype of JuliaNumber because you can't perform all of the operations that int does with JuliaNumber. If you can have aribtrary-precision arithmetic, you can't perform the modulus operation which is able to be performed if the types are ints. Thus, based on the definition, we can't perform all operations that the supertype, JuliaNumber, can perform. 

Meanwhile, the float is a subtype of JuliaNumber because you can represent everything in JuliaNumber that you can with a float and perform all of the same operations that a float can perform. 


### 7. 
a.) Python being lexically scoped means that here, the only variables in scope with line 4 are x which was passed as a parameter in the 3rd line g(x). 

SOLUTION:
Shadowing does take place, on line 3 & 4, since the x variable from line 3 shadows the x variable in line 1, thus the x variable in the g(x) function is the only one in scope. 

Thus, in the particular instance of line 4
The variables that are in scope are (a), the variable x on line 3, and the function (f), and print 


b.) 
local: a = x is a local variable 
enclosing: g(x) function is enclosing as it is enclosed by f(x)
global: ???
built-in: print 

SOLUTION: 

local: x is the local variable here  
enclosing: a is a variable from an enclosing scope
global: f(x)
built-in: print 

c.) For the variable in line 2, the x = a is out of scope when the function enters the g(x) block but the variable itself is still alive, since the function f hasn't returned g yet. 

SOLUTION: 
Another solution was what i thought about earlier, how x d i are out of scope in line 10 but still alive. when d is called. 


d.) No shadowing is occurring since Python is lexically scoped.

SOLUTION: 
Shadowing does take place, on line 3 & 4, since the x variable from line 3 shadows the x variable in line 1, thus the x variable in the g(x) function is the only one in scope. 



### 8. 
```Haskell
substr :: String -> String -> Bool
substr _ [] = True 
substr str1 str2 = foldl (\acc x -> if head str1 == head str2 then substr tail str1 tail str2 else substr str1 tail str2) [] str2 
```

```Haskell
substr :: String -> String -> Bool
substr [] _ = True 
substr _ [] = False 
substr str1 str2 = startsWith str1 str2 || substr str1 (tail str2)

startsWith :: String -> String -> Bool 
startsWith [] _ = True 
startsWith _ [] = False
startsWith (x:xs) (y:ys)
    | x == y = startsWith xs ys 
    | otherwise = False 
```
Essentially we created a helper function and then checked within the helper function if the characters matched, if it did, we continued on with startsWith, if it did not, we returned false and recursively called substr. If it did match, you could recursively call startsWith to check if the next two characters matched up, you would keep doing this until we either matched up the characters or didn't and then returend false. 



### 9. 
a.) 

 
iii., viii. 

i., vii., iv. 

ii., v. 

vi. 


b.) 

SOLUTION: 
1 pfa 
((b -> c) -> d) -> e -> f

2pfa 
-> e -> f

Every pfa removes a parameter, 1st one here was just a, second one here was a function ((b -> c) -> d) 

c.) 

SOLUTION: 

g = curried_2f(f) 

Trying to find something semantically equivalent to f(x, y)

So we would then call g(x)(y), if it were curried and we wanted to pass in both parameters. 


d.)
def f(x, y, z): 
    return x + y + z

```def curried_f(): 
    def f(x):
        def g(y): 
            def h(z): 
                return x + y + z
            return h
        return g
    return f
```
