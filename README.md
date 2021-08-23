# Fixing fundamental issues in LLVM IR: Introducing a byte type to solve type-punning

This repository contains a summary of my Google Summer of Code 2021 experinece
with the LLVM Compiler Infrastructure (as well as some of the current & future work).

  - [How this repoisoty is organised](#how-this-repoisoty-is-organised)
  - [Motivation](#motivation)
  - [Aims](#aims)
  - [Current Results](#current-results)
  - [Contributions](#contributions)
  - [Acknowledgement](#acknowledgement)

## How this repoisoty is organised

Since the changes I made are fundamental to LLVM, I had to work in my own fork of LLVM's
trunk. All *ready* commits can be found in the [gsoc-2021-dev branch](gsoc-2021-dev branch).
Note that these commits have not been reviewed by the members of the LLVM community yet
and thus may be changed in the future slightly.

This repository contains some of the scripts I used to automatically fix test failures and
collect IR and asembly diffs. Moreover, it contains draft versions of blog post that I
together with my mentors plan to publish to LLVM's blog. I hope that the posts will not be
only useful to make a point that LLVM needs a byte type, but also to people new to LLVM
and who are unable to find up-to-date tutorials/resources elsewhere.

## Motivation

## Aims

## Current Results

## Contributions

## Acknowledgement

I would like to thank my mentors Nuno Lopes and Juneyoung Lee for their
guidance and support along the project. I have learnt a lot about Clang's code
generation, LLVM's ecosystem and various optimizations: inlining, GVN/SROA, loop
transformations and SLP vectorization.

Also, I would like to thank Chung-Kil Hur for giving an access to ARM machine to 
run tests and benchmarks.

Special thanks to all LLVM community members for their advice and comments.

[gsoc-2021-dev branch]: https://github.com/georgemitenkov/llvm-project/commits/gsoc2021-dev
