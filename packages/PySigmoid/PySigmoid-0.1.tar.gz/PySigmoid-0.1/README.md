# `PySigmoid`

> A Python implementation of [Posits] and Quires with linear algebra applications. Posits were
proposed by [John Gustafson]. The sigmoid in PySigmoid is motivated by the [application of Posits in 8-bit nerual networks]. Gustafson introduced this number format as a replacement for the IEEE 754 floating point which has many issues.

# Issues with IEEE Floats
1. **Wasted Bit Patterns** - 32-bit IEEE floating point has around sixteen million ways to represent Not-A-Number
(NaN) while 64-bit floating point has nine quadrillion. A NaN is an exception value for invalid operations such as division by zero.
2. **Mathematically Incorrect** - The format specifies two zeroes - a negative and positive zero - which have different behaviors.
3. **Overflows to ± inf and underflows to 0** - Overflowing to ± inf increases the relative error by an infinite factor, while underflowing to 0 loses sign information.
4. **Complicated Circuitry** - One of the reasons why IEEE floating points have complicated circuitry is because
the standard defines support for denormalized numbers. Denormalized floating point numbers have a hidden bit of 0 instead of 1.
5. **No Gradual Overflow and Fixed Accuracy** - If accuracy is defined as the number of significand bits, IEEE
floating point have fixed accuracy for all numbers except denormalized numbers because the number of signficand
digits is fixed. Denormalized numbers are characterized by a decreased number of significand digits when the value approaches zero as a result of having a zero hidden bit. Denormalized numbers fill the underflow gap (i.e.
the gap between zero and the least non-zero values). The counterpart for gradual underflow is gradual overflow
which does not exist in IEEE floating points.

# Advantages of Posits
1. **Economical** - No bit patterns are redundant. There is one representation for infinity denoted as ± inf and zero.
All other bit patterns are valid distinct non-zero real numbers. ± inf serves as a replacement for NaN.
2. **Mathematical Elegant** - There is only one representation for zero.
3. **Gradual Underflow and Overflow** - The number of significand digits are not fixed in posits. In fact, a greater magnitude exponent, automatically reduces the number of significand digits which allows for both gradual overflow and underflow.
4. **Simpler Circuitry** - There are no denormalized numbers. The hidden bit is always 1.
5. **Tapered Accuracy** - Tapered accuracy is when values with small exponent have more digits of accuracy and values with large exponents have less digits of accuracy. This concept was first introduced by Morris (1971) in his paper ”Tapered Floating Point: A New Floating-Point Representation”.

[John Gustafson]: https://en.wikipedia.org/wiki/John_Gustafson_(scientist)
[application of Posits in 8-bit nerual networks]: https://github.com/interplanetary-robot/SigmoidNumbers

# References and Resources

- https://posithub.org/docs/Posits4.pdf - a detailed article on Posits
- http://web.stanford.edu/class/ee380/Abstracts/170201.html - official paper of Posits
- http://posithub.org/ - information and news about posits and universal numbers

# Mission
I want to make this a really useable software implementation of Posits. In particular, I want it to be useful in linear algebra where floating point computations are everywhere. It is still a work in progress and has a still a long way to go.

# License

Licensed under MIT License