# Introducing a byte type to LLVM IR to solve load type-punning

This year I participated in the Google Summer of Code (GSoC), working with Nuno
Lopes and Juneyoung Lee on fixing fundamental issues in LLVM. My project was
about making compiler-introduced load type-punning correct and fixing associated
bugs that are reported by [Alive2 dashboard][alive2-dashboard].

While our [proposal][proposal] was accepted for GSoC, our [RFC][rfc] on the
mailing list was received somewhat negatively. All replies we received had a
number of points in common, listed below:

   1. Proposed semantics seemed obscure and the explanation of the underlying
   issue of load type-punning was unclear.

   2. Introducing a new type to LLVM IR seemed like a significant amount of work
   and some believed it to be unfeasable.

   3. It was pointed out that the load type-punning issue is only relevant to C,
   C++ or Rust, and changing Clang and LLVM IR just for these 3 frontends is not
   worth the effort.

Despite receiving such a strong "No" from many LLVM contributors, we proceeded
with implementing a prototype. Our aim was to introduce a new type to LLVM, fix
any optimization issues/bugs and analyse the performance regression. By the end
of GSoC, we think that our results are very promising and can be used as a strong
evidence in favour of a byte type being part of LLVM IR.

To clarify semantics of a byte type, and to demistify a common disbelief that the
proposed changes break everything or not needed at all, we decided to write a
series of blog posts, describing our work. The posts cover motivation for the
byte type in detail, highlight the necessary changes in the API and the codebase,
and present performance numbers. Moreover, these posts try to serve an
educational purpose. During my GSoC, I encountered a lack of documentation
and explanation for certain optimizations and APIs. To help other newcomers and
junior LLVM developers like me, I humbly decided to cover certain aspects of the
optimization algorithms I had to study (or to be more precise go through the code
line by line) and some of the LLVM functionality I used.

We hope that these posts will help us to make the LLVM community aware of the
load type-punning issue, help people who want to start contributing to LLVM, and
most importantly that at some point in the future LLVM IR would have a byte type.

[alive2-dashboard]: https://web.ist.utl.pt/nuno.lopes/alive2/
[proposal]: https://docs.google.com/document/d/1C6WLgoqoDJCTTSFGK01X8sR2sEccXV5JMabvTHlpOGE/edit?usp=sharing
[rfc]: https://lists.llvm.org/pipermail/llvm-dev/2021-June/150883.html
