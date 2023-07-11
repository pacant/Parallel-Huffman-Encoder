CXX = g++
CXXFLAGS = -std=c++20 -O3
PTHREAD = -pthread
FF_FLAGS = -DTRACE_FASTFLOW

SRCDIR = src
INCDIR = headers
OBJDIR = obj

INCFLAGS = -I $(INCDIR)

all: encoder sequential_encoder decoder 

encoder: $(OBJDIR)/encoder.o $(OBJDIR)/huffman_encoder.o $(OBJDIR)/utimer.o $(OBJDIR)/fastflow_encoder.o
	$(CXX) $(CXXFLAGS) $(PTHREAD) $(INCFLAGS) $^ -o $@

sequential_encoder: $(OBJDIR)/sequential_encoder.o  $(OBJDIR)/utimer.o 
	$(CXX) $(CXXFLAGS) $(INCFLAGS) $^ -o $@

decoder: $(OBJDIR)/decoder.o $(OBJDIR)/utimer.o
	$(CXX) $(CXXFLAGS) $(INCFLAGS) $^ -o $@

$(OBJDIR)/huffman_encoder.o : $(SRCDIR)/huffman_encoder.cpp
	$(CXX) $(CXXFLAGS) $(PTHREAD) $(INCFLAGS) -c $< -o $@ 
$(OBJDIR)/utimer.o : $(SRCDIR)/utimer.cpp
	$(CXX) $(CXXFLAGS) $(INCFLAGS) -c $< -o $@

$(OBJDIR)/decoder.o : $(SRCDIR)/decoder.cpp
	$(CXX) $(CXXFLAGS) $(INCFLAGS) -c $< -o $@

$(OBJDIR)/encoder.o : $(SRCDIR)/encoder.cpp
	$(CXX) $(CXXFLAGS)  $(INCFLAGS) -c $< -o $@

$(OBJDIR)/sequential_encoder.o : $(SRCDIR)/sequential_encoder.cpp 
	$(CXX) $(CXXFLAGS)  $(INCFLAGS) -c $< -o $@

$(OBJDIR)/fastflow_encoder.o : $(SRCDIR)/fastflow_encoder.cpp 
	$(CXX) $(CXXFLAGS)  $(FF_FLAGS) $(PTHREAD) $(INCFLAGS) -c $< -o $@ 

$(OBJDIR)/utils.o : $(SRCDIR)/utils.cpp
	$(CXX) $(CXXFLAGS)  $(INCFLAGS) -c $< -o $@

clean:
	rm -rf $(OBJDIR)/* encoder sequential_encoder decoder

.PHONY: all clean
