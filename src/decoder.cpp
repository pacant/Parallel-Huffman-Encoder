#include <iostream>
#include <fstream>
#include <bitset>
#include <sstream>
#include <unordered_map>
#include "utimer.hpp"

using namespace std;

int get_padding_bits(const string &sequence)
{
    string header = sequence.substr(sequence.length() - 8, 8);
    bitset<8> padding_bits(header);
    return padding_bits.to_ulong();
}

string get_bits(const string &input_file)
{
    ifstream input("enc/" + input_file, ios::binary);
    if (!input)
    {
        cerr << "Failed to open the input file." << std::endl;
        exit(1);
    }

    ostringstream bitStream;
    char byte;

    while (input.get(byte))
    {
        bitStream << bitset<8>(byte);
    }

    return bitStream.str();
}

unordered_map<string, char> read_encoding_table()
{
    ifstream input("txt/decoding_table.txt");
    if (!input)
    {
        cerr << "Failed to open the encoding table file." << endl;
        exit(1);
    }

    unordered_map<string, char> encoding_table;

    string line;
    while (getline(input, line))
    {
        size_t delimiterPos = line.find(':');
        if (delimiterPos != string::npos)
        {
            string code = line.substr(delimiterPos + 1);
            code.erase(0, code.find_first_not_of(' ')); // Remove leading spaces
            code.erase(code.find_last_not_of(' ') + 1); // Remove trailing spaces

            char character = line[0];
            encoding_table[code] = character;
        }
    }
    return encoding_table;
}
string decode_sequence(const int num_padding_bits, const string &sequence, const unordered_map<string, char> &encoding_table)
{
    string text;
    string code;

    for (char bit : sequence)
    {
        code += bit;

        if (encoding_table.count(code) > 0)
        {
            char c = encoding_table.at(code);
            text += c;
            code.clear();
        }
    }
    return text;
}

void decode(const string &input_file, const string &output_file)
{
    string sequence = get_bits(input_file);

    int num_padding_bits = get_padding_bits(sequence);

    sequence = sequence.substr(0, sequence.size() - 8 - num_padding_bits);

    unordered_map<string, char> encoding_table = read_encoding_table();

    string text = decode_sequence(num_padding_bits, sequence, encoding_table);
    ofstream output("dec/" + output_file, ios::binary);
    if (!output)
    {
        cerr << "Failed to open the output file." << endl;
        exit(1);
    }

    output << text;
}

int main(int argc, char *argv[])
{
    if (argc < 1)
    {
        cerr << "Usage: " << argv[0] << " input_file" << endl;
        exit(1);
    }
    {
        utimer dec("Decoding");

        string input_file = argv[1];                                     // input file
        size_t pos = input_file.find_last_of("_");                       // removing extention
        string output_file = input_file.substr(0, pos) + "_decoded.txt"; // generated output file name

        decode(input_file, output_file);

        cout << "Decoded file created in dec/: " << output_file << endl; // "output.txt
    }

    return 0;
}