#ifndef HUFFMAN_DECODER_H
#define HUFFMAN_DECODER_H

#include <string>
#include <unordered_map>

std::string get_bits(const std::string &input_file);

std::unordered_map<std::string, char> read_encoding_table(const std::string &encoding_table_file);

std::string decode_sequence(const std::string &sequence, const std::unordered_map<std::string, char> &encoding_table);

void decode(const std::string &input_file, const std::string &encoding_table_file);

#endif
