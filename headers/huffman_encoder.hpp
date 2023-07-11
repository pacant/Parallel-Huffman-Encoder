#ifndef HUFFMAN_ENCODER_HPP
#define HUFFMAN_ENCODER_HPP

#include <string>
#include <vector>
#include <unordered_map>
#include <functional>

using namespace std;

struct HuffmanNode;

HuffmanNode *build_tree(vector<int> char_frequencies);
void build_encoding_table(const HuffmanNode *node, const string &code,
                          vector<string> &encoding_table);
string ascii_file(const string &output_buffer, int num_threads);
void write_encoding_table(const vector<string> &encoding_table);
vector<int> count_frequencies(string input, int nw);
string encode_file(const string &input_buffer, int num_threads, const vector<string> &encoding_table);
void add_padding(string &output_buffer);

#endif
