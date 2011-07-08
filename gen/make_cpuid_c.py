#!/usr/bin/env python
#
# Copyright 2011 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from xml.dom import minidom

HEADER_TEMPL = """\
/*this file is auto_generated by volk_register.py*/

#include <volk/volk_cpu.h>
#include <volk/volk_config_fixed.h>

struct VOLK_CPU volk_cpu;

#if defined(__i386__) || (__x86_64__)

//implement get cpuid for gcc compilers using a copy of cpuid.h
#if defined(__GNUC__)
#include <gcc_x86_cpuid.h>
#define cpuid_x86(op, r) __get_cpuid(op, r+0, r+1, r+2, r+3)

//implement get cpuid for MSVC compilers using __cpuid intrinsic
#elif defined(_MSC_VER)
#include <intrin.h>
#define cpuid(op, r) __cpuid(r, op)

#else
#error "A get cpuid for volk is not available on this compiler..."
#endif

static inline unsigned int cpuid_eax(unsigned int op) {
    unsigned int regs[4];
    cpuid_x86 (op, regs);
    return regs[0];
}

static inline unsigned int cpuid_ebx(unsigned int op) {
    unsigned int regs[4];
    cpuid_x86 (op, regs);
    return regs[1];
}

static inline unsigned int cpuid_ecx(unsigned int op) {
    unsigned int regs[4];
    cpuid_x86 (op, regs);
    return regs[2];
}

static inline unsigned int cpuid_edx(unsigned int op) {
    unsigned int regs[4];
    cpuid_x86 (op, regs);
    return regs[3];
}
#endif

"""

def make_cpuid_c(dom) :
    tempstring = HEADER_TEMPL;
    
    for domarch in dom:
        if str(domarch.attributes["type"].value) == "x86":
            if "no_test" in domarch.attributes.keys():
                no_test = str(domarch.attributes["no_test"].value);
                if no_test == "true":
                    no_test = True;
                else:
                    no_test = False;
            else:
                no_test = False;
            arch = str(domarch.attributes["name"].value);
            op = domarch.getElementsByTagName("op");
            if op:
                op = str(op[0].firstChild.data);
            reg = domarch.getElementsByTagName("reg");
            if reg:
                reg = str(reg[0].firstChild.data);
            shift = domarch.getElementsByTagName("shift");
            if shift:
                shift = str(shift[0].firstChild.data);
            val = domarch.getElementsByTagName("val");
            if val:
                val = str(val[0].firstChild.data);
            
            if no_test:
                tempstring = tempstring + """\
int i_can_has_%s () {
#if defined(__i386__) || (__x86_64__)
    return 1;
#else
    return 0;
#endif
}
                
""" % (arch)
                
            elif op == "1":
                tempstring = tempstring + """\
int i_can_has_%s () {
#if defined(__i386__) || (__x86_64__)
    unsigned int e%sx = cpuid_e%sx (%s);
    return ((e%sx >> %s) & 1) == %s;
#else
    return 0;
#endif
}

""" % (arch, reg, reg, op, reg, shift, val)

            elif op == "0x80000001":
                tempstring = tempstring + """\
int i_can_has_%s () {
#if defined(__i386__) || (__x86_64__)
    unsigned int extended_fct_count = cpuid_eax(0x80000000);
    if (extended_fct_count < 0x80000001)
        return %s^1;
    unsigned int extended_features = cpuid_e%sx (%s);
    return ((extended_features >> %s) & 1) == %s;
#else
    return 0;
#endif
}

""" % (arch, val, reg, op, shift, val)
        
        elif str(domarch.attributes["type"].value) == "powerpc":
            arch = str(domarch.attributes["name"].value);
            tempstring = tempstring + """\
int i_can_has_%s () {
#ifdef __PPC__
    return 1;
#else
    return 0;
#endif
}

""" % (arch)
        
        elif str(domarch.attributes["type"].value) == "all":
            arch = str(domarch.attributes["name"].value);
            tempstring = tempstring + """\
int i_can_has_%s () {
    return 1;
}

""" % (arch)
        else:
            arch = str(domarch.attributes["name"].value);
            tempstring = tempstring + """\
int i_can_has_%s () {
    return 0;
}

""" % (arch)
    
    tempstring = tempstring + "void volk_cpu_init() {\n";
    for domarch in dom:
        arch = str(domarch.attributes["name"].value);
        tempstring = tempstring + "    volk_cpu.has_" + arch + " = &i_can_has_" + arch + ";\n"
    tempstring = tempstring + "}\n\n"

    tempstring = tempstring + "unsigned int volk_get_lvarch() {\n";
    tempstring = tempstring + "    unsigned int retval = 0;\n"
    tempstring = tempstring + "    volk_cpu_init();\n"
    for domarch in dom:
        arch = str(domarch.attributes["name"].value);
        tempstring = tempstring + "    retval += volk_cpu.has_" + arch + "() << LV_" + arch.swapcase() + ";\n"
    tempstring = tempstring + "    return retval;\n"
    tempstring = tempstring + "}\n\n"

    return tempstring;

    
            
        

                
                