A minimal wrapper for running cutadapt (http://cutadapt.readthedocs.io/en/stable/) in batch mode.
Made for the Monckton Group at University of Glasgow, so there may be specific behaviour in this program for the way in which we label our MiSeq data.
I honestly can't remember.

Install
=======

    python setup.py install
    or
    pip install batchadapt

Usage
=====
Example usage:

    $ batchadapt [-h/--help] [-v] [-i INPUT] [-o OUTPUT] [-fwfp AAAAA] [-rvfp GGGGG] [-e 0] [-ov 10]

Arguments
=========

Run batchadapt with the '--help' argument for detailed explanations of what each argument does.