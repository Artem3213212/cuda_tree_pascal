TreeHelper for Pascal lexer.
Requires plugin CudaTree to work.

Based on Python library PyPascalTokenizer.
Can parse and show these Pascal entities:

- standalone functions/procedures
- type declarations: enums, arrays, records, sets etc
- classes (and "object"s)
- class methods
- class operators
- nested classes (nesting level: 1 or more)
- nested functions (nesting level: 1 or more)
- interfaces
- var/const declarations, global and local (in funcs/methods)
- properties
- uses-sections (both interface/implementation, shown under single node)
- resourcestrings
- anonymous functions, methods
- generics (mode: Delphi, ObjFpc)
- nested classes in generics
- keyword "reference" (from Delphi)

It was tested on:
- several FreePascal units (FPJson, RegExpr etc)
- private 3K lines project, with anonym functions with nested usual functions


Author: Artem Gavrilov (@Artem3213212 at GitHub)
License: MIT
