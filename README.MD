# HUFFMAN ENCODER
This code provides an implementation of a Huffman encoder in C++. The program takes an input file and encodes its contents using the Huffman coding technique to produce an encoded binary file. The program supports two modes of operation: native threads and Fastflow.

## Usage
First of all put text files in _txt/_

For running the parallel version:
```bash
make
./encoder "text.txt" "number of threads" "mode (0: native threads, 1: FF)"
```

You can also run the sequential version
```bash
./sequential_encoder "text.txt"
```

The output will be in the form of _text_encoded.bin_ inside _bin/_.

It's also possible to decode the file. The file should be in _bin/_
```bash
./decoder "text_encoded.bin"
```

The output will be in the form of _text_decoded.txt_ inside _dec/_.