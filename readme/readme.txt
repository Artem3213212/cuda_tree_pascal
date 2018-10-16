TreeHelper for Pascal lexer.
Requires plugin CudaTree to work.

Based on Python library PyPascalTokenizer.
Can parse and show these Pascal entities:

- standalone functions/procedures
- class methods
- classes (and objects)
- class operators
- nested classes (nesting level: 1 or more)
- nested functions (nesting level: 1 or more)
- interfaces
- var/const declarations, global and local (in funcs/methods)
- properties
- uses (both interface/implementation, shown under single node)
- resourcestrings
- anonymous functions, methods
- type declarations (enums/arrays/records/etc)
- generics (mode: Delphi, ObjFpc)
- nested classes in generics

It was tested on:
- several FreePascal units (FPJson, RegExpr etc)
- private 3K lines project, with anonym functions with nested usual functions


Author: Artem Gavrilov (@Artem3213212 at GitHub)
License: MIT
