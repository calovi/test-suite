##===- Makefile.spec ---------------------------------------*- Makefile -*-===##
#
# This makefile contains information for building SPEC as an external test.
#
##===----------------------------------------------------------------------===##

include $(LEVEL)/Makefile.config

# RUN_TYPE - Either ref, test, or train.  May be specified on the command line.
RUN_TYPE  := test

## Information the test should have provided...
ifndef STDOUT_FILENAME
STDOUT_FILENAME := standard.out
endif
ifndef LDFLAGS
LDFLAGS = -lm
endif

# Get the current directory, the name of the benchmark, and the current
# subdirectory of the SPEC directory we are in (ie, CINT2000/164.gzip)
#
CURRENT_DIR := $(shell cd .; pwd)
BENCH_NAME  := $(subst $(shell cd ..   ; pwd),,$(CURRENT_DIR))
SPEC_SUBDIR := $(subst $(shell cd ../..; pwd),,$(CURRENT_DIR))

# Remove any leading /'s from the paths
BENCH_NAME  := $(patsubst /%,%,$(BENCH_NAME))
SPEC_SUBDIR := $(patsubst /%,%,$(SPEC_SUBDIR))

SPEC_BENCH_DIR := $(SPEC_ROOT)/$(SPEC_SUBDIR)

PROG := $(BENCH_NAME)
Source := $(wildcard $(SPEC_BENCH_DIR)/src/*.c)

# Disable the default Output/%.out-* targets...
PROGRAMS_HAVE_CUSTOM_RUN_RULES := 1
SourceDir := $(SPEC_BENCH_DIR)/src/

include $(LEVEL)/test/Programs/MultiSource/Makefile.multisrc

# Pseudo target to build just the bytecode file.
bytecode: Output/$(PROG).llvm.bc

LCCFLAGS := -DSPEC_CPU2000 -O2
CFLAGS := -DSPEC_CPU2000 -O2

SPEC_SANDBOX := $(LEVEL)/test/Programs/External/SPEC/Sandbox.sh

# Information about testing the program...
REF_IN_DIR  := $(SPEC_BENCH_DIR)/data/$(RUN_TYPE)/input/
REF_OUT_DIR := $(SPEC_BENCH_DIR)/data/$(RUN_TYPE)/output/
LOCAL_OUTPUTS := $(notdir $(wildcard $(REF_OUT_DIR)/*))


# Specify how to generate output from the SPEC programs.  Basically we just run
# the program in a sandbox (a special directory we create), then we cat all of
# the outputs together.

$(PROGRAMS_TO_TEST:%=Output/%.out-nat): \
Output/%.out-nat: Output/%.native
	$(SPEC_SANDBOX) nat-$(RUN_TYPE) $@ $(REF_IN_DIR) \
             ../../$(RUNSAFELY) $(STDOUT_FILENAME) ../../$< $(RUN_OPTIONS)
	-(cd Output/nat-$(RUN_TYPE); cat $(LOCAL_OUTPUTS)) > $@

$(PROGRAMS_TO_TEST:%=Output/%.out-lli): \
Output/%.out-lli: Output/%.llvm.bc $(LLI)
	$(SPEC_SANDBOX) lli-$(RUN_TYPE) $@ $(REF_IN_DIR) \
             ../../$(RUNSAFELY) $(STDOUT_FILENAME) $(LLI) $(LLI_OPTS) ../../$< $(RUN_OPTIONS)
	-(cd Output/lli-$(RUN_TYPE); cat $(LOCAL_OUTPUTS)) > $@

$(PROGRAMS_TO_TEST:%=Output/%.out-jit): \
Output/%.out-jit: Output/%.llvm.bc $(LLI)
	$(SPEC_SANDBOX) jit-$(RUN_TYPE) $@ $(REF_IN_DIR) \
             ../../$(RUNSAFELY) $(STDOUT_FILENAME) $(LLI) $(JIT_OPTS) ../../$< $(RUN_OPTIONS)
	-(cd Output/jit-$(RUN_TYPE); cat $(LOCAL_OUTPUTS)) > $@

$(PROGRAMS_TO_TEST:%=Output/%.out-llc): \
Output/%.out-llc: Output/%.llc
	$(SPEC_SANDBOX) llc-$(RUN_TYPE) $@ $(REF_IN_DIR) \
             ../../$(RUNSAFELY) $(STDOUT_FILENAME) ../../$< $(RUN_OPTIONS)
	-(cd Output/llc-$(RUN_TYPE); cat $(LOCAL_OUTPUTS)) > $@

$(PROGRAMS_TO_TEST:%=Output/%.out-cbe): \
Output/%.out-cbe: Output/%.cbe
	$(SPEC_SANDBOX) cbe-$(RUN_TYPE) $@ $(REF_IN_DIR) \
             ../../$(RUNSAFELY) $(STDOUT_FILENAME) ../../$< $(RUN_OPTIONS)
	-(cd Output/cbe-$(RUN_TYPE); cat $(LOCAL_OUTPUTS)) > $@
