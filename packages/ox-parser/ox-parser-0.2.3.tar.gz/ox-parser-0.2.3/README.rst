Ox is simple "compiler of compilers" framework based on the excellent PLY_
library.

.. _PLY: http://www.dabeaz.com/ply/


Why Ox?
=======

PLY is a great library which is a reasonably efficient pure Python
implementation of Yacc/Bison. We think, however, its API is a little bit awkward
and does a lot of strange magic under the hood. Ox wraps main PLY functionality
into a more functional and straightforward API that aims to be more explicit while
still being easier to use.

PLY was designed to be a Python replacement for Yacc/Bison and does not offer
any functionality to work as a general framework for building compilers. Ox
is a minimalistic framework and provides a few extra bells and whistles (but
it will never be nowhere near a Python replacement for, say, LLVM).

Ox is mature enough to be useful for production code, but just like PLY, it was
created as a tool for a introductory compilers course. One explicit pedagogical
goal of Ox is to make the boundaries of the different compilation phases very
explicit and easily pluggable into each other. This approach is good for
teaching, but it does not lead to the most efficient or robust
implementations of real compilers. Ox, as most compiler generators, is good for
quick experimentation but it is limited in terms of performance and, more
importantly, Ox parsers generally fail to provide nice error messages for
syntax errors.
 
 
What about the name?
====================

PLY is a Pythonic implementation/interpretation of Yacc. The most widespread
Yacc implementation is of course GNU Bison. We decided to keep the bovine 
theme alive and call it Ox.


Concepts
========
 
Compilation is usually broken in a few steps:

1) Tokenization/lexical analysis: a string of source code is broken into a 
   list of tokens. Ox lexers are any function that receives a string of source
   code and return a list (or any iterable) of tokens.
2) Parsing: the list of tokens is converted into a syntax tree. In Ox, the parser
   is derived from a grammar in BNF form. It receives a list of tokens and
   outputs an arbitrary parse tree.
3) Semantic analysis: the parse tree is scanned for semantic errors (e.g. 
   invalid variable names, invalid type signatures, etc). The parse tree may
   be converted to different representations in this process.
4) Code optimization: many optimizations are applied in order to generate 
   efficient internal representations. This is highly dependent on the target
   language and runtime and it tends to be the largest part of a real compiler.
5) Code generation: the intermediate representation is used to emit code in the
   target language. The target language is often a low level language such as
   assembly or machine code. Nothing prevents us from emmiting Python or
   Javascript, however.

Ox is mostly concerned with steps 1 and 2. The library has very limited support
steps 3 onwards, but in general they tend to be very application specific and
a general tool such as Ox can offer little help.

Usage
=====

Ox can build a lexer function by simply providing a list of token names
associated with their corresponding regular expressions:

.. code-block:: python

    import ox
    
    lexer = ox.make_lexer([
        ('NUMBER', r'\d+(\.\d*)?'),
        ('PLUS', r'\+'),
        ('MINUS', r'\-'),
        ('MUL', r'\*'),
        ('DIV', r'\/'),
    ])


This declares a tokenizer function that receives a string of source code and
returns a list of tokens:
 
>>> lexer('21 + 21')
[NUMBER('21'), PLUS('+'), NUMBER('21')]
 
The next step, of course, is to pass this list of tokens to a parser in order to 
generate the parse tree. We can easily declare a parser in Ox from a mapping 
of grammar rules to handler functions.

Each handler function receives a number of inputs from its corresponding
grammar rule and return an AST node. In the example bellow, we return tuples
to build our AST as a LISP-like S-expressions.

.. code-block:: python

    binop = lambda x, op, y: (op, x, y)
    identity = lambda x: x
    
Now the rules:

.. code-block:: python

    parser = ox.make_parser([
        ('expr : expr PLUS term', binop),
        ('expr : expr MINUS term', binop),
        ('expr : term', identity),
        ('term : term MUL atom', binop),
        ('term : term DIV atom', binop),
        ('term : atom', identity),
        ('atom : NUMBER', float),
    ])

The parser takes a list of tokens and convert it to an AST:

>>> parser(lexer('2 + 2 * 20'))
('+', 2.0, ('*', 2.0, 20.0))


The AST makes it easy to analyze and evaluate an expression. We can
write a simple evaluator as follows:

.. code-block:: python

    import operator as op

    operations = {'+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv}
    
    def eval(node):
        if isinstance(node, tuple):
            head, *tail = node
            func = operations[head]
            args = (eval(x) for x in tail)
            return func(*args)
        else:
            return node


The eval function receives an AST, but we can easily compose it with the other
functions in order to accept string inputs. (Ox functions understand sidekick's 
pipeline operators. The arrow operator ``>>`` composes two functions by passing
the output of each function to the function in the pipeline following the arrow
direction).

>>> eval_input = lexer >> parser >> eval
>>> eval_input('2 + 2 * 20')
42.0

We can call this function in a loop to have a nice calculator written with only
a few lines of Python code!

.. code-block:: python

    def eval_loop():
        expr = input('expr: ')
        print('result:', eval_input(expr))
