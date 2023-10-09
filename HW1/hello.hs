greeting = "Hello, world!" 

-- 1.
-- if length x > length y 
largest x y = if length x >= length y then x else y

-- 2. 
reflect :: Integer -> Integer
reflect 0 = 0
reflect num
    | num < 0 = (-1) + reflect num+1
    | num > 0 = 1 + reflect num-1

{-
the problem with Barey's code is that when the number is 0, the reflect function will constantly 
either increae or deccrease but there is no guard for when the function call needs to stop.
In either case, no guard will apply when the number increases or decreases to a certain point and 
so the function will just keep going on forever.

The function was not decrementing number since there as no parentheses in the function parameters. 
Thus, the function would recursively call reflect(num + 1) but never actually reach the base case.
-} 

--3. 
-- a. 
-- needed to place a bounds on the range for x otherwise it will execute unlimitedly
all_factors :: Integer -> [Integer]
all_factors y = [ x | x <- [1..y], y `mod` x == 0]


-- b. 
perfect_numbers :: [Integer]
perfect_numbers = [ z | z <- [1..], sum (init (all_factors z))== z]

-- 4. 



-- 5. 