# Fixing fundamental issues in LLVM IR: Introducing a byte type to solve type-punning

This repository contains a summary of my Google Summer of Code 2021 experinece
with the LLVM Compiler Infrastructure (as well as some of the current & future
work).

  - [How this repository is organised](#how-this-repository-is-organised)
  - [Motivation](#motivation)
  - [Aims](#aims)
  - [Current Results](#current-results)
  - [Contributions](#contributions)
  - [Links](#links)
  - [Future Work](#future-work)
  - [Acknowledgement](#acknowledgement)

## How this repository is organised

Since the changes I made are fundamental to LLVM, I had to work in my own fork
of LLVM's trunk. All *ready* commits can be found in my
[development branch][gsoc-2021-dev]. Note that these commits have not been
reviewed by the members of the LLVM community yet and thus may be altered in the
future.

This repository contains some of the scripts I used to automatically fix test
failures and collect IR/assembly diffs. Moreover, it has draft versions of blog
posts that I (together with my mentors) plan to publish to LLVM's blog. I hope
that these posts will be useful to make a point that LLVM needs a byte type, as
well as that people new to LLVM and who are unable to find up-to-date
tutorials/resources elsewhere can use them.

*Note: The aim of this document is to provide a **summary** of my GSoC experience, and
not to describe implementation or design details nor the semantics of a byte type and
a `bytecast` - that is the purpose
of the blog posts.*

## Motivation

It is common for compilers, and LLVM in particular, to transform calls to
`memcpy`,`memmove`, `memcmp` and `memset` to a number of integer loads/stores of
the corresponding bit width. After, load/store instructions can be optimized
further. However, there are certain problems with this type punning approach.

Firstly, semantics of these functions specify that the memory is
copied/compared/set as-is in bytes, including the padding bits if necessary. On
the other hand, in LLVM IR padding is always poison, and loading poison bits
makes the whole loaded value to be poison as well. If the call to `memcpy` or
similar function is substituted with an integer load/store pair, then it is
possible that the copied value turns into poison after the transformation
(e.g. https://alive2.llvm.org/ce/z/xoCTpH). This problem also affects other C++
functions that may be lowered to calls to aforementioned functions and
subsequently to integer load/store pairs (e.g.`uninitialised_copy`).

The second problem comes from the fact that `unsigned char*`, used in `memcpy`
and other functions' definitions, can alias with any pointer. Hence,
substituting a call to `memcpy` of a pointer with an integer load/store pair
may fool the compiler not to see the escape of the pointer, thus breaking the
alias analysis and the soundness of further optimizations.

The underlying problem is the fact that LLVM IR lowers `unsigned char` or
similarly the recently introduced `std::byte` to `i8`. While both C and C++
define these types as handles to the raw bytes of objects, LLVM IR does not
have a similar type. This means that compiler-introduced type punning can
break the alias analysis and miss the escaped pointer, as was reported in one
of the bug reports [here][bug].

## Aims

In my proposal I have originally outlined the following aims for the project:

- Introduce a byte type to LLVM ecosystem.

- Introduce a `bytecast` instruction to LLVM ecosystem.

- Make sure that the new LLVM IR can be converted to bitcode and back.

- Implement a lowering of a byte type and `bytecast` to SelectionDAG.

- Fix code generation in  Clang to produce a byte type for `char` and
`unsigned char`.

- Implement new optimizations for `memcpy`,`memmove`, `memcmp` and `memset` to
use bytes instead of integers.

- Make sure that everyting works correclty at `O0` - `O3`.

- Analyze performance regressions, fix broken optimizations, implement new
optimizations.

## Current Results

By the end of my Google Summer of Code project, I have achieved the
following results:

- Both the byte type and `bytecast` instruction where introduced to LLVM IR.
I implemented a basic lowering for them in SelectionDAG (byte is mapped to an
integer, and `bytecast` is a no-op), and adapted the code generation in Clang
to produce bytes for `unsigned char`/`char` and casts where necessary.

- The wrong type-punning optimizations of `memcpy`,`memmove`, `memcmp` and
`memset` were fixed. Moreover, I fixed all necessary optimizations to make
sure that C/C++ programs can be compiled at any optimization level correctly.

- Performance regressions on the [SPECrate2017][spec2017] benchmark suite were
analysed and fixed. The only program with pending regression (out of 10
programs) is `xalancbmk`. The table below summarises performance regressions,
where regression is calculated as:

```
Regression = [(OldValue - NewValue) / NewValue] x 100%
```

| Program          | Compile-time regression, % | Execution-time regression, % | Object file size regression, % |
| ---------------- |---------------------------:|-----------------------------:|-------------------------------:|
| 500.perlbench_r. | 0.38%                      | -0.88%                       | -0.98%                         |
| 502.gcc_r.       | 0.37%                      | 0.02%                        | -2.23%                         |
| 505.mcf_r.       | -5.64%                     | -0.17%                       | -0.19%                         |
| 520.omnetpp_r.   | -0.08%                     | -0.46%                       | -1.01%                         |
| 523.xalancbmk_r. | 0.10%                      | -4.83%                       | -0.17%                         |
| 525.x264_r.      | 0.22%                      | -0.40%                       | -0.01%                         |
| 531.deepsjeng_r. | 0.56%                      | 0.26%                        | -0.01%                         |
| 541.leela_r.     | 0.02%                      | -0.01%                       | -0.01%                         |
| 557.xz_r.        | 0.19%                      | -0.91%                       | 1.84%                          |

## Contributions

Below is the list of commits that I have made during the project. I decided to
group them logically into 4 groups: LLVM IR changes, Clang changes, changes in
optimizations and the rest of changes.

1. **Clang**

   Commits:

   - [[Clang][IR][1] Lowering of char/uchar to byte](https://github.com/georgemitenkov/llvm-project/commit/7dce2343fb89d54b716dd72d6ed3b2a89c3394f7)
   - [[Clang] Fixed FP -> char cast](https://github.com/georgemitenkov/llvm-project/commit/3faf64b23b7ea4d584e469302b7e45f421150405)
   - [[Clang] Fixed character visitor when src type is a byte](https://github.com/georgemitenkov/llvm-project/commit/d176a99c502594235d5d850baee9c0c2f5751955)

2. **LLVM IR**

   Commits:

   - [[IR][ByteType] Introduced a byte type to LLVM IR](https://github.com/georgemitenkov/llvm-project/commit/58372f5905dcebf6a4e85f06d5ba3b6acce2918b)
   - [[IR][ByteCast] Introduced a bytecast instruction to LLVM IR](https://github.com/georgemitenkov/llvm-project/commit/5a742de75c6912326a273bb1b349effd02e3209d)
   - [[IR][Transforms] Library calls build routines and optimizations](https://github.com/georgemitenkov/llvm-project/commit/96922e6c1a0aa2bad32944d42ef968099023d554)
   - [[IR] Added a byte type guard when comparing with null](https://github.com/georgemitenkov/llvm-project/commit/166c37b68a15adcff029b29c76ec092a0cb42f42)

3. **Optimizations**

   Commits:

   - [[IR][Mem* fixes][1] Initial lowering for mem* calls](https://github.com/georgemitenkov/llvm-project/commit/772c813d28b8c4376638f4015ebf70e1cb8a257c)
   - [[GVN][SROA] Fixes for O2 level](https://github.com/georgemitenkov/llvm-project/commit/84d89ff9c5f638a43436d06eaac2aa173065db12)
   - [[IR] Implemented bytecast (bitcast x) -> x](https://github.com/georgemitenkov/llvm-project/commit/1df8c74fa086674a84c2f350debe80f1e9496a44)
   - [[Transforms] Fixed store value bitcast in InstCombine](https://github.com/georgemitenkov/llvm-project/commit/658822ea97ef2398cfb63248141392e32f87537e)
   - [[Transforms] Made bytecast vectorizable](https://github.com/georgemitenkov/llvm-project/commit/c1a3c4dc4a3acef1e657cc506b13ff34be98e341)
   - [[Transforms][SLP] Added bytecast support](https://github.com/georgemitenkov/llvm-project/commit/165cc3483480187670ac1938d0da37677ccb45fd)
   - [[Analysis][TTI] Fixed cost analysis for inlining](https://github.com/georgemitenkov/llvm-project/commit/bc953002999b8d28ece14e7fdab7b47546c572ba)
   - [[Transforms][LoopIdiom] Added conversion for bytes to memset](https://github.com/georgemitenkov/llvm-project/commit/4d840a1a7fc3d09883e5a5d2f65c611b5f0098a6)

3. **Other**

   Commits:

   - [[OpenMP][IR] Fixes for OpenMP codegen and tests](https://github.com/georgemitenkov/llvm-project/commit/b8ae29a5fa9c0b4e33c7c974dc47384fef823307) (*Note that changes in this commit will be reverted in the future when both byte and integer strings are be allowed!*)

## Links

The original proposal can be found [here][proposal]. The initial RFC for a byte
type is avaliable [here][rfc].

During my project, I was also keeping a document where I tracked what has been
done, what challenges I have encountered, and my further plans. It is availiable
[here][progress-tracking].

To keep track of performance numbers, I made a [spreadsheet][benchmarks] where
I evaluated performance differences at differentt stages of the project.

## Future Work

I am going to continue working on this project. I plan the folowing
contributions nexts, listed by priority:

### 1. Making my changes compatible with old LLVM versions

   Currently, old versions of LLVM and the version with a byte type are not
   compatible. The primary reason for this is that a string in my version is
   *always* a `b8` array, whereas in old LLVM version it is an array of `i8`.
   This makes impossible to parse global variables, defined as:

   ```llvm
   ; New LLVM
   @var = global constant [6 x b8] c"Hello\00"

   ; Old LLVM
   @var = global constant [6 x i8] c"Hello\00"
   ```

   The solution to this problem is to allow two types of strings: byte and
   integer ones. At the same time, Clang would produce a byte type string
   only for C and C++ frontends. For example, LLVM IR above could become:

   ```llvm
   ; New LLVM
   @var = global constant [6 x b8] b"Hello\00"

   ; Old LLVM
   @var = global constant [6 x i8] c"Hello\00"
   ```

   Moreover, `const` strings are read-only, and hence a pointer cannot
   escape through them. Therefore these could be modelled as an array of `i8`
   values. The drawback of this approach is non-uniformity of what can represent
   a string.

### 2. Fixing all Clang and IR tests

   Clang has numerous test failures due to new code generation for `char` and
   `unsigned char`. These include simple test failures like checking for an `i8`
   instead of `b8`, but also have much more complicated cases which are hard to
   fix automatically:

   - Some target-specific intrinsics also use `char` in their type signature. We
   need to ensure type compatibility.

   - Currently all tests invloving `i8` strings are wrong. Addresing 1 would
   help to avoid that issue, adding byte strings only where needed.

   - Some tests require insertion of `bytecast`/`bitcast` pairs: this makes
   rewriting FileCheck directives harder.

### 3. Solving performance issues of `xalancbmk` program

   `xalancbmk` is the last program from SPEC CPU benchmark suite that has
   *unacceptable* regression in execution time of approximately 4-5%.
   Interestingly, the regression first appeared when vectorization for
   `bytecast`s was enabled. My last hypothesis was that `-loop-idiom` pass did
   not recognise a sequence of stores as a `memset`. As a result, `memset` call
   was not created and the code was vectorized instead - leading to perfromance
   regression. However, the fix did not improve the execution time. I plan to
   investigate the causes of the regression further and bring it to 0% like I
   did for other programs.

### 4. Blog posts

   I am going to write a series of blog posts covering my work, why
   LLVM needs a byte type and my experience. These posts are intended to
   demistify how we can add a byte to LLVM IR, while keeping changes minimal and
   preserving the correctness. Also, they aim to serve as an example that
   fundamental changes in LLVM IR are possible and should not be rejected by the
   community just because "it is too much work". In addition to describing the
   necessary changes, these blog posts should serve as a valuable resource for
   junior LLVM developers and contributors (like me!) - describing the API, how
   to debug LLVM and identify the sources of performance regressions, and how
   certain optimizations work.

### 5. Further optimisations

   While the results of benchmarking seem promising, there are still a number
   of optimizations we can implement. For example:

   1. **Propagating `bytecast`s through `phi` nodes**

      To help Scalar Evolution, we can propagate `bytecast`s through `phi`
      nodes. This would then allow us to apply a `bytecast`, then to find
      recurrences for an integer value, and finally bitcast the result back. The
      most obvious use case is a `bytecast` in a loop, which we want to hoist
      to the header if possible. For example, consider the following C  code:

      ```c
      void foo(char* c, int n) {
        *c = 0;
        for (int i = 0; i < n; ++i)
          *c += 3;
      }
      ```

      The old lowering of `char` to `i8` would produce the follwing optimized IR
      for this function:

      ```llvm
      ; Code optimized to `*c = 3 * n;`
      define void @foo(i8* nocapture %c, i32 %n) {
      entry:
        %cmp = icmp sgt i32 %n, 0
        %0 = trunc i32 %n to i8
        %1 = mul i8 %0, 3
        %storemerge = select i1 %cmp, i8 %1, i8 0
        store i8 %storemerge, i8* %c, align 1
        ret void
      }
      ```

      However, the byte version of this program would produce a diffrent IR,
      with optimizations blocked at the stage of calulating SCEVs of induction
      values.

      ```llvm
      define void @foo(b8* %c, i32 %n) {
      entry:
        store b8 bitcast (i8 0 to b8), b8* %c, align 1
        %cmp3 = icmp slt i32 0, %n
        br i1 %cmp3, label %for.body.lr.ph, label %for.end

      for.body.lr.ph:
        %c.promoted = load b8, b8* %c, align 1
        br label %for.body

      for.body:
        %i.04 = phi i32 [ 0, %for.body.lr.ph ], [ %inc, %for.inc ]

        ; SCEV does not see this recurrence because of the bytecast!
        %0 = phi b8 [ %c.promoted, %for.body.lr.ph ], [ %1, %for.inc ]
        %conv = bytecast b8 %0 to i8
        %add = add i8 %conv, 3
        %1 = bitcast i8 %add to b8

        br label %for.inc

      for.inc:
        %inc = add nuw nsw i32 %i.04, 1
        %cmp = icmp slt i32 %inc, %n
        br i1 %cmp, label %for.body, label %for.cond.for.end_crit_edge, !llvm.loop !6

      for.cond.for.end_crit_edge:
        %.lcssa = phi b8 [ %1, %for.inc ]
        store b8 %.lcssa, b8* %c, align 1
        br label %for.end

      for.end:
        ret void
      }
      ```

      The solution to this is to hoist `bytecast` to the header, so that the
      loop body operates on integer values:

      ```llvm
      ; ...
      for.body.lr.ph:
        %c.promoted = load b8, b8* %c, align 1
        %c.bytecast = bytecast b8 %c.promoted to i8
        br label %for.body

      for.body:
        ; Now the loop body operates on integers only!
        %0 = phi i8 [ %c.bytecast, %for.body.lr.ph ], [ %add, %for.inc ]
        %i.04 = phi i32 [ 0, %for.body.lr.ph ], [ %inc, %for.inc ]
        %add = add i8 %0, 3
        br label %for.inc

      for.inc:
        ; ...

      for.cond.for.end_crit_edge:
        %.lcssa = phi i8 [ %add, %for.inc ]
        %byte = bitcast i8 %.lcssa to b8
        store b8 %byte, b8* %c, align 1
      ```

      I have already implemented this optimization, but due to some test
      failures had to revert the commit. I plan to investigate what has
      caused the problem in the future.

   2. **Combining `bytecast`s**

      Multiple `bytecast`s of the same byte within the same basic block can be
      combined together. This can make IR more readable.

      ```llvm
      ; Before
      %b = load b8, b8* %ptr
      %i1 = bytecast b8 %b to i8
      %i2 = bytecast b8 %b to i8
      use(%i1)
      use(%i2)

      ; After  
      %b = load b8, b8* %ptr
      %i = bytecast b8 %b to i8
      use(%i)
      use(%i)
      ``` 

### 6. Changing Alive2 to recognise a byte type

   [Alive2][alive2] does not recognise bytes yet. Adding a byte type to its
   type system will help to enforce the usefulness of this work. 

## Acknowledgement

I would like to thank my mentors Nuno Lopes and Juneyoung Lee for their guidance
and support throughout the project. I have learnt a lot about Clang's code
generation, developed a deeper understanding of LLVM IR semantics, and studied
different optimizations, including but not limited to inlining, GVN, SROA,
various loop transformations (LoopIdiom, LoopRotate, LICM, etc.) and SLP
vectorization.

I would like to thank the members of Seoul National University and Chung-Kil Hur
in particular for giving me an access to an ARM machine, so that I can run tests
and SPEC CPU benchmarks.

Special thanks to all LLVM community members for their advice and comments.

[alive2]: https://github.com/AliveToolkit/alive2
[bug]: https://bugs.llvm.org/show_bug.cgi?id=37469
[benchmarks]: https://docs.google.com/spreadsheets/d/1TyflQR0NTF2EUw4WERu2Di2od20sI1PIyXXEVbxrmBs/edit?usp=sharing
[gsoc-2021-dev]: https://github.com/georgemitenkov/llvm-project/commits/gsoc2021-dev
[progress-tracking]: https://docs.google.com/document/d/1mUaF3D9vEz0HWlsJa6a5vHbJm7y-idKLIq1or5oExqE/edit?usp=sharing
[proposal]: https://docs.google.com/document/d/1C6WLgoqoDJCTTSFGK01X8sR2sEccXV5JMabvTHlpOGE/edit?usp=sharing
[rfc]: https://lists.llvm.org/pipermail/llvm-dev/2021-June/150883.html
[spec2017]: https://www.spec.org/cpu2017/results/
