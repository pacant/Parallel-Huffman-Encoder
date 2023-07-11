#ifndef FASTFLOW_ENCODER_HPP
#define FASTFLOW_ENCODER_HPP

#include <string>
#include <vector>
#include <unordered_map>

using namespace std;

string encode_file_ff(const string &input_buffer, int num_threads, const vector<string> &encoding_table);
vector<int> count_frequencies_ff(const string &input_buffer, int num_threads);
string ascii_file_ff(const string &input_buffer, int num_threads);

#endif