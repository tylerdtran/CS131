get_every_nth :: Int -> [a] -> [a]
-- get_every_nth _ [] = []
-- get_every_nth n lst = foldl (\acc a -> if n /= 0 then get_every_nth (n - 1) (tail lst) else acc ++ [a]) [] lst

-- get_every_nth :: Int -> [a] -> [a]
get_every_nth n lst = foldr (\(i, x) acc -> if i `mod` n == 0 then x : acc else acc) [] (zip [1..] lst)
-- if it is actually the nth number, the modulus should return 0, and thus, we can add it to the list, otherwise we just move on and don't concatenate