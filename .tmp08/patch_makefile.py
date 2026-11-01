#!/usr/bin/env python3
"""Module 08: static talloc link + overridable loader -m32 flag."""
import sys

PATH = "/home/builder/void_rawhide_work/proot_engine/src/GNUmakefile"

with open(PATH, "r", encoding="utf-8") as fh:
    text = fh.read()

if "TALLOC_STATIC_LIB" in text:
    sys.exit("already patched")

# 1. Static talloc for the Android build.
old = "LDFLAGS  += -ltalloc -Wl,-z,noexecstack\n"
new = (
    "# Module 08: the Android build links the talloc archive compiled in\n"
    "# module 02 so the finished rootfs never needs libtalloc.so.2 at run\n"
    "# time.  Host builds keep the historical -ltalloc.\n"
    "ifdef TALLOC_STATIC_LIB\n"
    "  LDFLAGS += $(TALLOC_STATIC_LIB)\n"
    "else\n"
    "  LDFLAGS += -ltalloc\n"
    "endif\n"
    "LDFLAGS  += -Wl,-z,noexecstack\n"
)
if text.count(old) != 1:
    sys.exit("anchor 1 not found once")
text = text.replace(old, new)

# 2. The 32-bit loader flag must be decoupled from the variable suffix:
#    the NDK has no -m32 switch, its 32-bit targets use a dedicated
#    driver, while native builds keep the historical -m32.
old = (
    "define define_from_arch.h\n"
    "$2$1 := $(shell $(CC) $1 -E -dM -DNO_LIBC_HEADER $(SRC)/arch.h | grep -w $2 | cut -f 3 -d ' ')\n"
    "endef\n"
)
new = (
    "# Module 08: the compiler flag for the 32-bit loader is decoupled\n"
    "# from the variable suffix.  Native builds keep -m32; the Android\n"
    "# NDK 32-bit driver is selected by CC instead and leaves it empty.\n"
    "LOADER_FLAG-m32 ?= -m32\n"
    "\n"
    "define define_from_arch.h\n"
    "$2$1 := $(shell $(CC) $(LOADER_FLAG$1) -E -dM -DNO_LIBC_HEADER $(SRC)/arch.h | grep -w $2 | cut -f 3 -d ' ')\n"
    "endef\n"
)
if text.count(old) != 1:
    sys.exit("anchor 2 not found once")
text = text.replace(old, new)

old = (
    "loader/loader$1.o: loader/loader.c\n"
    "\t@mkdir -p $$(dir $$@)\n"
    "\t$$(COMPILE) $1 $$(LOADER_CFLAGS$1)\n"
    "\n"
    "loader/assembly$1.o: loader/assembly.S\n"
    "\t@mkdir -p $$(dir $$@)\n"
    "\t$$(COMPILE) $1 $$(LOADER_CFLAGS$1)\n"
)
new = (
    "loader/loader$1.o: loader/loader.c\n"
    "\t@mkdir -p $$(dir $$@)\n"
    "\t$$(COMPILE) $(LOADER_FLAG$1) $$(LOADER_CFLAGS$1)\n"
    "\n"
    "loader/assembly$1.o: loader/assembly.S\n"
    "\t@mkdir -p $$(dir $$@)\n"
    "\t$$(COMPILE) $(LOADER_FLAG$1) $$(LOADER_CFLAGS$1)\n"
)
if text.count(old) != 1:
    sys.exit("anchor 3 not found once")
text = text.replace(old, new)

with open(PATH, "w", encoding="utf-8") as fh:
    fh.write(text)

print("patched GNUmakefile")
