## Pure Python implementation of self-balancing binary search tree (SBST)

There is no implemenation of SBST in Standard Python Library, and I found it quite inconvenient and a little bit disappointing.

This is a compact, portable (no dependencies) and extremely easy-to-use implementation of self-balancing binary search tree. This particular type of trees (so called AA-tree) is described here: https://en.wikipedia.org/wiki/AA_tree

**Features:**
1. You can use this module through `import` instruction or simply copy-paste the implementation into your source code, and be happy.
2. While instantiating `sbst` object you can specify your own comparison function or use default simple comparison.
3. You can add values to tree one-by-one using function `add`, or fill it from some iterable object (function `addfrom`). Either initialization in constructor is possible.
4. The tree stores all duplicates. This feature is vital if the tree is an index for in-memory table.
5. This SBST gives you two basic search operations:
   - `min` - returns minimal value that is not less (if `inclusive` parameter is True) or greater (inclusive=False) than specified limit.
   - `max` - returns maximal value that is not greater (if `inclusive` parameter is True) or less (inclusive=False) than specified limit.
   If you have not specified limit, functions return respectively minimal or maximal value in the tree.
6. Function `forward_from` returns generator that yields sorted sequence of values starting from a specified value. Function `backward_from` yields reverse-sorted sequence down from a specified value. These functions have `inclusive` option too. If starting value is not specified, these functions yield respectively sorted or reverse-sorted sequences of all values in the tree. If tree modified while iterating (some values inserted, some removed, tree rebalanced), sequence will be yielded in right predictable way.
7. If comparison function treats values as equal, they will be yielded by `forward_from` and `backward_from` generators in the insertion order.
8. Do not store _None_ values into tree. Even if your comparison function can process them, you will not be able to search them because None value will be treated as 'not specified'.
9. If mutable objects inserted into the tree are changed, their sequence in tree may become irrelevant. So after value mutation it is a good idea to remove it from tree and add again.
10. Methods `add` and `remove` are not thread-safe. Be careful.

Tutorial is included in the source code.
