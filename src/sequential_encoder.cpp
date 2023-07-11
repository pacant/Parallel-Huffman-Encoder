#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <unordered_map>
#include <queue>
#include <bitset>
#include "utimer.hpp"
#include "utils.hpp"

using namespace std;

// Node for the Huffman tree
struct HuffmanNode
{
    char data;
    int frequency;
    HuffmanNode *left;
    HuffmanNode *right;

    HuffmanNode(char data, int frequency) : data(data), frequency(frequency), left(nullptr), right(nullptr) {} // Leaf node
    HuffmanNode(int frequency) : data('\0'), frequency(frequency), left(nullptr), right(nullptr) {}            // Internal node

    ~HuffmanNode()
    {
        delete left;
        delete right;
    }
};

// auxiliary function for the priority queue, to order the nodes by frequency (from lowest to highest)
struct CompareFrequency
{
    bool operator()(HuffmanNode *a, HuffmanNode *b) const
    {
        return a->frequency > b->frequency;
    }
};

// Read the input file and count character frequencies
void count_frequencies(const string &input_buffer, vector<int> &char_frequencies)
{
    // Count character frequencies
    for (int i = 0; i < input_buffer.size(); i++)
    {
        char_frequencies[input_buffer[i]]++;
    }
}

// Build the Huffman tree returning the root
HuffmanNode *build_tree(vector<int> &char_frequencies)
{
    // Create a priority queue from lowest to highest frequency, this is an auxiliary data structure for extracting the two nodes with the lowest frequency
    priority_queue<HuffmanNode *, vector<HuffmanNode *>, CompareFrequency> pq;

    // Add each character and its frequency to the queue as a Huffman node
    for (int i = 0; i < 256; i++)
    {
        if (char_frequencies[i] == 0)
            continue;
        pq.push(new HuffmanNode(char(i), char_frequencies[i]));
    }

    // Build the tree, combining the two nodes with the lowest frequency until there is only one node left (the root)
    while (pq.size() > 1)
    {
        HuffmanNode *left = pq.top();
        pq.pop();
        HuffmanNode *right = pq.top();
        pq.pop();
        HuffmanNode *parent = new HuffmanNode(left->frequency + right->frequency);
        parent->left = left;
        parent->right = right;
        pq.push(parent);
    }

    return pq.top();
}

// Build the encoding table recursively. Starting from the root, go left and add a 0 to the code, go right and add a 1 to the code. When you reach a leaf, add the code to the encoding table.
void build_encoding_table(const HuffmanNode *node, vector<string> &encoding_table, const string &code = "")
{
    if (node->left == nullptr && node->right == nullptr) // leaf
    {
        encoding_table[node->data] = code;
        return;
    }
    build_encoding_table(node->left, encoding_table, code + "0");
    build_encoding_table(node->right, encoding_table, code + "1");
}

// Write the encoding table to the output file
void write_encoding_table(vector<string> &encoding_table)
{
    ofstream output("txt/decoding_table.txt");
    if (!output.is_open())
    {
        cerr << "Failed to open output file: " << endl;
        exit(1);
    }
    // Write each entry in the encoding table
    for (int i = 0; i < 256; i++)
    {
        if (encoding_table[i].size() != 0)
        {
            output << char(i) << ": " << encoding_table[i] << "\n";
        }
    }
}
string ascii_file(const string &output_buffer, const string &output_file)
{

    string temp_buffer; // Buffer for holding bytes to write to the output file

    temp_buffer.reserve(output_buffer.size() / 8); // Reserve space in the buffer (no inizialized memory is allocated, only the space is reserved)

    for (int i = 0; i < output_buffer.size(); i += 8)
    {
        temp_buffer += bits_to_char(output_buffer.substr(i, 8)); // Convert the 8 bits to a byte
    }

    return temp_buffer;
}
// Encode the input file using the encoding table
string encode_file(const string &input_buffer, vector<string> &encoding_table)
{
    // Encode the input chunk using the encoding table
    string output_buffer;

    for (char ch : input_buffer)
    {
        output_buffer += encoding_table[ch];
    }

    add_padding(output_buffer);
    // Convert bits to bytes and write to the output file

    return output_buffer;
}
void encode(const string &input_buffer, const string &output_file)
{
    // read the input file and count character frequencies

    vector<string> encoding_table(256, ""); // encoding table, for each character stores the corresponding bit string
    vector<int> char_frequencies(256, 0);   // map between characters and their frequencies
    HuffmanNode *root;

    {
        utimer parallel_count("Sequential counting");
        count_frequencies(input_buffer, char_frequencies);
    }

    {
        utimer parallel_build("Sequential building");
        // build the Huffman tree
        root = build_tree(char_frequencies);

        // build the encoding table
        build_encoding_table(root, encoding_table);

        // Write the encoding table to the output file
        write_encoding_table(encoding_table);
    }
    string output_buffer;
    string out;
    // Encode the input file using the encoding table
    {
        utimer parallel_enc("Sequential encoding");
        output_buffer = encode_file(input_buffer, encoding_table);
    }
    {
        utimer parallel_enc("Sequential ASCII translation");
        out = ascii_file(output_buffer, output_file);
    }

    {
        utimer sequential("Sequential writing file");
        ofstream output("enc/" + output_file, ios::binary);
        if (!output.is_open())
        {
            cerr << "Failed to open output file: " << endl;
            exit(1);
        }
        output.write(out.data(), out.size());
    }
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        cerr << "Usage: " << argv[0] << " input_file" << endl;
        exit(1);
    }

    string input_file = argv[1];
    size_t pos = input_file.find_last_of(".");
    string output_file = input_file.substr(0, pos) + "_encoded.bin";

    string text;
    string line;
    {
        utimer parallel_read("Sequential reading");
        ifstream input("txt/" + input_file);
        if (!input.is_open())
        {
            cerr << "Failed to open input file: " << input_file << endl;
            exit(1);
        }

        while (getline(input, line))
        {
            text += line;
        }
    }
    encode(text, output_file);

    cout << "Encoded file created in: " << output_file << endl;

    return 0;
}

// i thread devono dividere il file in chunk e poi ognuno deve codificare il proprio chunk, però ovviamente in maniera ordinata