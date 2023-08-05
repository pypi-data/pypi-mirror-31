# PyNucamino

![CI Status](https://travis-ci.org/hcv-shared/pynucamino.svg?branch=master)

### Python bindings for <code><a href="https://github.com/hivdb/nucamino">nucamino</a></code>

## Installation

`pip install pynucamino` should work on MacOS, Windows, and Linux
systems. The package includes the `nucamino` binaries, so you don't
need to install anything else.


## Usage

```python
>>> import pynucamino
>>> pynucamino.Nucamino.profiles()
["hcv1a", "hcv1b", "hcv2", "hcv3", "hcv4", "hcv5", "hcv6", "hiv1b"]
>>> test_sequence = """> Test Sequence
... GATTACA"""
>>> pynucamino.align(test_sequence, "hcv1a", ["NS3"])
...
# Alignment Results
>>> pynucamino.align_file("input_filename.fasta", "hcv1a", ["NS5B"])
...
# Alignment Results
>>> alignment = pynucamino.Nucamino(test_seq, profile="hcv1a", genes=["NS3"])
>>> alignment.result
...
# Alignment Results
>>> alignment.proc
...
# subprocess.CompletedProcess 
```

Use `pynucamino.align` or `pynucamino.align_file` to align a FASTA
formatted collection of sequences in a string or a file, repsectively.
For more fine-grained control, the `pynucamino.Nucamino` class has
`result` property containing the alignment results and a `proc`
property that contains details on exactly how `nucamino` was called.

Use the built-in `help` function for more information on each class
and function.


## Security Warning

This library is probably vulnerable
to
[command injection](https://www.owasp.org/index.php/Command_Injection)
when run with malicious inputs. If you care at all about the security
of your system, you shouldn't use this library unless you trust
whoever is setting the parameters.

In practice, this means that setting up a web-server that runs this
library using input from anonymous users on the public internet might
get your systme hacked. The intended use case is writing internal
scripts that are run with pre-determined parameters; this case is
perfectly safe.


## Resources

- [Nucamino GitHub repo](https://github.com/hivdb/nucamino)
- [Nucamino Paper](https://www.ncbi.nlm.nih.gov/pubmed/28249562)
