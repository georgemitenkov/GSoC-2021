# Why we need a byte type in LLVM IR? 

## Load type-punning in LLVM

LLVM IR has various optimizations to make the code more efficient while
preserving its correctness. The optimization that we focus on in this post
(and which turns out to be semantically incorrect!) is a compiler-introduced
load type-punning when optimizing calls to [`memcpy`][memcpy-example],
[`memmove`][memmove-example], [`memset`][memset-example], and
[`memcmp`][memcmp-example]. In this post, we primarily focus on `memcpy`
optimization since the rest of the functions are optimized in the same way.
However, for interested readers we added links to Compiler Explorer that show
optimizations for all functions.

A call to `memcpy` with 1, 2, 4 or 8 bytes copied is optimized by `instcombine`
into a load/store pair, as shown below:

```llvm
; Before
call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 1 %a, i8* align 1 %b, i64 8, i1 false)

; After running -instcombine
%b_ptr = bitcast i8* %b to i64*
%a_ptr = bitcast i8* %a to i64*
%b_val = load i64, i64* %b_ptr, align 1
store i64 %b_val, i64* %a_ptr, align 1
```

TODO:
- Copying a struct with padding makes values poison
- We treat the memory as integers, why this is bad?
- Miscompilation example
- Copying a pointer in 8 chunks?

[memcpy-example]: https://llvm.godbolt.org/z/jfhYbq3qq
[memmove-example]: https://llvm.godbolt.org/z/cofW6cW1o
[memset-example]: https://llvm.godbolt.org/z/W9e5MEYs3
[memcmp-example]: https://llvm.godbolt.org/z/er3zdPdxj
[type-punning]: https://blog.regehr.org/archives/959