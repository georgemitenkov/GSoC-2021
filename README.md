# Fixing fundamental issues in LLVM IR: Introducing a byte type to solve type-punning

This repository contains a summary of my Google Summer of Code 2021 experinece
with the LLVM Compiler Infrastructure (as well as some of the current & future
work).

  - [How this repoisoty is organised](#how-this-repoisoty-is-organised)
  - [Motivation](#motivation)
  - [Aims](#aims)
  - [Current Results](#current-results)
  - [Contributions](#contributions)
  - [Links](#links)
  - [Acknowledgement](#acknowledgement)

## How this repoisoty is organised

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

## Motivation

## Aims

## Current Results

## Contributions

Below is the list of commits that I have made during the project. I decided to
group them logically into 3 groups: LLVM IR changes, Clang changes, and
changes in optimizations.

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

   - [[OpenMP][IR] Fixes for OpenMP codegen and tests](https://github.com/georgemitenkov/llvm-project/commit/b8ae29a5fa9c0b4e33c7c974dc47384fef823307)(*Note that changes in this commit will be reverted in the future when both byte and integer strings are be allowed!*)

## Links

The original proposal can be found [here][proposal]. The initial RFC for a byte
type is avaliable [here][rfc].

During my project, I was also keeping a document where I tracked what has been
done, what challenges I have encountered, and my further plans. It is availiable
[here][progress-tracking].

To keep track of performance numbers, I made a [spreadsheet][benchmarks] where
I evaluated performance differences at differentt stages of the project.

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

[benchmarks]: https://docs.google.com/spreadsheets/d/1TyflQR0NTF2EUw4WERu2Di2od20sI1PIyXXEVbxrmBs/edit?usp=sharing
[gsoc-2021-dev]: https://github.com/georgemitenkov/llvm-project/commits/gsoc2021-dev
[progress-tracking]: https://docs.google.com/document/d/1mUaF3D9vEz0HWlsJa6a5vHbJm7y-idKLIq1or5oExqE/edit?usp=sharing
[proposal]: https://docs.google.com/document/d/1C6WLgoqoDJCTTSFGK01X8sR2sEccXV5JMabvTHlpOGE/edit?usp=sharing
[rfc]: https://lists.llvm.org/pipermail/llvm-dev/2021-June/150883.html
