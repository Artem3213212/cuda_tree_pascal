TreeHelper for Pascal lexer.
Requires plugin CudaTree to work.

Based on Python library PyPascalTokenizer.

Can parse and show these Pascal entities:
- standalone functions/procedures
- class methods
- classes
- classes, nested into another classes (nesting level can be 2 or more)
- records
- interfaces
- var/const declarations, global and local in funcs/methods
- properties
- uses (both interface/implementation, shown under single node)
- resourcestrings
- anonymous functions
- procedural types


Author: Artem Gavrilov (@Artem3213212 at GitHub)
License: MIT
