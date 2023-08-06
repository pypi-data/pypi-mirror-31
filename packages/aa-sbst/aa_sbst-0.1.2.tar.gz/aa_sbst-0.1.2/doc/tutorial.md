# Quick tutorial for aa_sbst (self-balancing binary search tree implementation for Python)

## How to embed

There are three ways to embed this functionality into your project:
1. Get this module by `pip install aa_sbst` and then import into your module by `import aa_sbst`.
2. Directly download [aa_sbst.py](/aa_sbst.py) file and adopt it into your project.
3. In some cases you might prefer simply copy-paste the implementation into your source code. Feel free doing this. Just find comments "*# -------------- Start copy-paste from here*" and "*# -------------- Finish copy-paste here*", and take the lines between them.

## How to use

Actually, you do not need to bother about tree nodes. You simply create tree, and then add values (whatever they would be) and get them from the tree.

If you embedded this functionality using thw way 1 or 2 described above, first of all import this module:
```python
import aa_sbst
```
Then create the tree object:
```python
my_tree = aa_sbst.sbst()
```
We just created uninitializes tree with default arranging function.

### Basic functions (`add`, `addfrom`, `min`, `max`, `forward_from`, `backward_from`, and `remove`)

Let's add some values:
```python
my_tree.add(1)
my_tree.add(3)
my_tree.add(-2)
my_tree.add(10)
```
Also you can add values from an iterable object:
```python
my_tree.addfrom(i**3 for i in range(2, 6))
```
Now we are ready to look for values in the tree. Let's find maximal value that is not greater then, for example, 20:
```python
my_tree.max(20)
```
Result:
```
10
```
Lookin for the minimal value that is not less then 27:
```python
my_tree.min(27)
```
Result:
```
27
```
Lookin for the minimal value that is greater then 27 (`inclusive` parameter set to `False`):
```python
my_tree.min(27, False)
```
Result:
```
64
```
Methods `forward_from` and `backward_from` useful for getting sequences from the tree, and they can be used just for lookin at the values stored in the tree:
```python
print(*[v for v in my_tree.forward_from()])
```
Result:
```
-2 1 3 8 10 27 64 125
```
We did not specified starting value so all the values are printed. Let specify a starting value, for example, 10:
```python
print(*[v for v in my_tree.forward_from(10)])
```
Result:
```
10 27 64 125
```
Or 11 (not present in the tree) for starting value:
```python
print(*[v for v in my_tree.forward_from(11)])
```
Result:
```
27 64 125
```
If you need to excude starting value from the iteration, set `False` for parameter `inclusive`:
```python
print(*[v for v in my_tree.forward_from(10, False)])
```
Result:
```
27 64 125
```
To set upper limit for `forward_from`, use parameter `stop` and, if needed, `stop_incl`:
```python
print(*[v for v in my_tree.forward_from(10, False, stop=100)])
```
Result:
```
27 64
```

**_Important:_** Including/excluding options for starting and stopping values by default are *True for start* and *False for stop*. Like start and stop for `range` object.

`backward_from` works like `forward_from`, but enumerates values backward from start to stop:
```python
print(*[v for v in my_tree.backward_from(100, stop=10)])
```
Result:
```
64 27
```
Removing values from the tree:
```python
print(*[v for v in my_tree.forward_from()])
my_tree.remove(8)
print(*[v for v in my_tree.forward_from()])
```
Result:
```
-2 1 3 8 10 27 64 125
-2 1 3 10 27 64 125
```

**_Important notice:_** This implementation holds all the inserted duplicates:
```python
print(*[v for v in my_tree.forward_from()])
my_tree.add(10)
print(*[v for v in my_tree.forward_from()])
```
Result:
```
-2 1 3 10 27 64 125
-2 1 3 10 10 27 64 125
```

### Using custom comparison functions

By default tree arranges values in their "natural" order. If this behavior is not useful, you can define your own comparison function and specify it at the tree's instantiation:
```python
def my_cmp_func(v1, v2):
    # Very strange order - natural order, but even numbers first
    if v1 % 2 < v2 % 2:
        return -1   # '-1' means 'v1 < v2'
    elif v1 % 2 > v2 % 2:
        return 1    # '1' means 'v1 > v2'
    else:
        # If v1 and v2 are both even or both odd, use default comparison
        return aa_sbst._sbst_simple_comparison(v1, v2)

# Create tree with non-default comparison:
even_odd_tree = aa_sbst.sbst(my_cmp_func)
# Populate tree from range [-5, 6):
even_odd_tree.addfrom(range(-5, 6))
# Let's take a look:
print(*[v for v in even_odd_tree.forward_from()])
```
Result:
```
-4 -2 0 2 4 -5 -3 -1 1 3 5
```
If your tree is an index for some objects, you might prefer to simply tell what the fields should be used for comparison. The `make_cmp_fn_by_key` function privides this service.

Let's create tree that holds 'employee' named tuples with fields 'id', 'name', and 'salary'. Data in tree will be arranged by salary and then by names:
```python
import collections
t_empl = collections.namedtuple('employee', 'id, name, salary')
empl_idx = aa_sbst.sbst(aa_sbst.make_cmp_fn_by_key(lambda v: (v.salary, v.name)))
empl_idx.add(t_empl(1, 'John', 1000))
empl_idx.add(t_empl(2, 'Alice', 1000))
empl_idx.add(t_empl(3, 'Paul', 900))
empl_idx.add(t_empl(4, 'Bob', 1100))
empl_idx.add(t_empl(5, 'Celine', 1050))
# Let's see:
print(*[v for v in empl_idx.forward_from()], sep='\n')
```
Result:
```
employee(id=3, name='Paul', salary=900)
employee(id=2, name='Alice', salary=1000)
employee(id=1, name='John', salary=1000)
employee(id=5, name='Celine', salary=1050)
employee(id=4, name='Bob', salary=1100)
```
Let's find all the records with salary >= 1001:
```python
print(*[v for v in empl_idx.forward_from(t_empl(1, '', 1001))], sep='\n')
```
Result:
```
employee(id=5, name='Celine', salary=1050)
employee(id=4, name='Bob', salary=1100)
```

### How to get tree-like representation

We will get tree-like representation of 'empl_idx' from previous example:
```python
for n in empl_idx.nodes_list():
    lvl = 0
    c = n
    while c:
        c = c.parent
        lvl += 1
    print('    '*(lvl-1) + ('/' if n.direction == 'L' \
           else ('\\' if n.direction == 'R' else '')) + str(n.getval()))
```
Result:
```
    /employee(id=3, name='Paul', salary=900)
employee(id=2, name='Alice', salary=1000)
        /employee(id=1, name='John', salary=1000)
    \employee(id=5, name='Celine', salary=1050)
        \employee(id=4, name='Bob', salary=1100)
```
