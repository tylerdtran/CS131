### 1. 
a. foo :: [Int] -> [Int]
b. y :: [[char]] -> [[char]]
c. m :: [(String, [String])]
SOLUTION: m :: [(Bool, String)]
d. z ::  [t1] -> [t1] -> []
SOLUTION: z :: [t1] -> [[t1]] -> [t1]
If the accumulator is already a list, then the actual list it traverses has to be a list of lists
e. foo :: [t1] -> []
SOLUTION: 
[t1] -> [t2]


### 2. 
If a language doesn't support closures, it is not possible for the language to support currying or partial function application. Both of these functional programming concepts, rely on the ability to capture another variable as part of a closure. And thus, a closure is important for the function of currying and partial function application. Making it impossible to support either function without it. 

### 3.
a.)
data Graph = Node Integer [Graph] 

b.) 
Node 42 [Node 5 []]

c.) 
The time-complexity is likely O(nlogn) as at worst the height of the graph could be O(logn) and there are n nodes. So at worst, there could be O(nlogn) nodes to traverse in order to add a node to the front of an existing graph

SOLUTION: Since we are chaining it to the front, there is no need to alter the graph in any way and thus the time complexity to add it to the front is O(1).

d.) 
```Haskell
sum_of_graph :: Graph -> Integer
sum_of_graph [] = 0 
sum_of_graph (Node val next_node) = val + sum_of_graph(next_node)
```

SOLUTION: 
```Haskell
sum_of_graph :: Graph -> Integer
sum_of_graph [] = 0 
sum_of_graph (Node val next_node) = val + sum (map sum_of_graph next_node)
```
Perform the addition of the actual node passed in as well as sum up all of the children using the map function and then recursively call it onto the next node.

### 4. 
get_every_nth :: Int -> [a] -> [a]
<!-- get_every_nth n lst = filter (\n -> ) lst  -->
get_every_nth n lst = foldl (\acc a -> if n != 0 then get_every_nth n-1 tail lst else acc ++ [a] get_every_nth n tail lst) [] lst


### 5. 
inf_list = [ x^k | k <-[1...] ]
inf_list = [ \x -> z^x | z<- [1..]]



### 6. 
a.
Joke7 
Joke3 
Joke4
SOLUTION:
Joke6 
Joke3 
Joke4

b.
Joke6 
Joke2 
A shallow copy makes a copy of the top-level object but the contents inside are just references to the previous object that was "copied". Thus, it makes a copy of c1 is still referenced but all of the other mutations don't affect com. The c2 still stays the same in since at some point any mutation besides to c1 or c2 indirectly like the c[0] reference isn't going to affect com. 



### 7. 
a. CORRECT
Integer can be a subtype of float. If they can represent the same values, the Float datatype properly supports all of the operations that the Integer supports and thus, Integer can be a subtype of Float. 


b. CORRECT
In this language, Float cannot be a subtype of integer because if integer were the supertype, then all of the operations for integer must be supported in float but in this case, Float is not supporting all of the operations that integer supports. 

c. INCORRECT
If Float were to support the exponentiation operator, then Integer could still be a subtype of Float since the operations of Integer would still be supported in the operations of Float. 

Meanwhile, the Float still cannot be a subtype of Integer since Integer wouldn't be able to support all of the types that float can support. 

SOLUTION: 
Neither. The Integer can no longer support all of the operations of Tsuper (Float) since Float now has the exponentiation operator. 



### 8. 
a.
We can tell that Siddarth is statically typed. This is because the type of the variable y doesn't change throughout the lifetime of the program execution. Even when it is reassigned a float, to maintain the Int data type for the variable y, the program converts the float data type into an Int. 

b. 
Conversion is being performed in this code as It is a switch between primitive types Float -> Int on line 3. A narrowing is occurring in the conversion as we are losing information when going from an Int to a Float. 

c. 
The program output would be: 
10 
3.5 
3.5

d. It is impossible to tell since changing the assignment from y = 3.5 to y = 3 ensures now that the reassignment of the variables are now reassigning the same type as the 10 earlier. Thus, since there is no change in value type in the assignment there is no behavior left to tell us whether we are of static or dynamic typing. 