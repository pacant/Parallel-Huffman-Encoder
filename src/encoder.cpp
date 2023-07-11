#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include "huffman_encoder.hpp"
#include "utimer.hpp"
#include "fastflow_encoder.hpp"

using namespace std;

int main(int argc, char *argv[])
{
    if (argc < 4)
    {
        cerr << "Usage: " << argv[0] << "input_file num_threads mode(0: native, 1: ff)" << endl;
        exit(1);
    }

    string input_file = argv[1];
    size_t pos = input_file.find_last_of(".");                       // remove extention
    string output_file = input_file.substr(0, pos) + "_encoded.bin"; // output file name

    bool mode = atoi(argv[3]);

    int num_threads = atoi(argv[2]);

    if (num_threads < 1)
    {
        cerr << "Invalid number of threads: " << num_threads << endl;
        exit(1);
    }

    string text;
    string line;
    {
        utimer parallel("Reading file");
        ifstream input("txt/" + input_file);
        if (!input.is_open())
        {
            cerr << "Failed to open input file: " << input_file << endl;
            exit(1);
        }

        if (num_threads < 1)
        {
            cerr << "Invalid number of threads: " << num_threads << endl;
            exit(1);
        }

        while (getline(input, line))
        {
            text += line;
        }
    }

    vector<int> char_frequencies;           // map between characters and their frequencies (position is the ASCII code of the char)
    HuffmanNode *root;                      // root of the Huffman tree
    vector<string> encoding_table(256, ""); // map between characters and their encoding

    // count the frequencies of each character in the input file
    if (!mode) // NATIVE THREADS
    {
        {
            utimer parallel("Native thread counting");
            // Count the frequencies of each character in the input file with mapReduce
            char_frequencies = count_frequencies(
                text,
                num_threads);
        }
    }
    else // FASTFLOW
    {
        utimer ff("Fastflow counting");
        // Count the frequencies of each character in the input file with fastflow
        char_frequencies = count_frequencies_ff(text, num_threads);
    }

    // **** SEQUENTIAL CODE, COMMON FOR BOTH IMPLEMENTATION ****
    {
        utimer parallel("Building tree (seq)");
        // Build the Huffman tree from the frequencies table returning the root
        root = build_tree(char_frequencies);

        // Build the encoding table starting from the root
        build_encoding_table(root, "", encoding_table);

        // Write the encoding table to the output file decoding_table.txt
        write_encoding_table(encoding_table);
    }

    // **** ****

    string output_buffer;
    string out;

    // Encoding the file (huff and ascii)
    if (!mode) // NATIVE THREADS
    {

        output_buffer = encode_file(text, num_threads, encoding_table);

        out = ascii_file(output_buffer, num_threads);
    }

    else // FASTFLOW
    {

        output_buffer = encode_file_ff(text, num_threads, encoding_table);

        out = ascii_file_ff(output_buffer, num_threads);
    }

    // ### sequential writing of the file ###
    {
        utimer sequential("Writing file");
        ofstream output("enc/" + output_file, ios::binary);
        if (!output.is_open())
        {
            cerr << "Failed to open output file: " << endl;
            exit(1);
        }

        output.write(out.data(), out.size());
    }

    cout << "Encoded file created in enc/: " << output_file << endl;

    return 0;
}
