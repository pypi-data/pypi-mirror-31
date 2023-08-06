/*
* BSD 3-Clause License
*
* Copyright (c) 2017-2018, plures
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*
* 1. Redistributions of source code must retain the above copyright notice,
*    this list of conditions and the following disclaimer.
*
* 2. Redistributions in binary form must reproduce the above copyright notice,
*    this list of conditions and the following disclaimer in the documentation
*    and/or other materials provided with the distribution.
*
* 3. Neither the name of the copyright holder nor the names of its
*    contributors may be used to endorse or promote products derived from
*    this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
* FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/


#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>
#include "ndtypes.h"
#include "xnd.h"
#include "gumath.h"


static int
sum_inner_dimensions(const xnd_t stack[], int nargs, int outer_dims)
{
    int sum = 0, n;
    int i;

    for (i = 0; i < nargs; i++) {
        const ndt_t *t = stack[i].type;
        n = t->ndim - outer_dims;
        sum += n == 0 ? 1 : n;
    }

    return sum;
}

int
gm_apply(const gm_kernel_t *kernel, xnd_t stack[], int outer_dims,
         ndt_context_t *ctx)
{
    const int nargs = (int)kernel->set->sig->Function.nargs;

    switch (kernel->tag) {
    case Strided: {
        const int sum_inner = sum_inner_dimensions(stack, nargs, outer_dims);
        const int dims_size = outer_dims + sum_inner;
        const int steps_size = nargs * outer_dims + sum_inner;
        ALLOCA(char *, args, nargs);
        ALLOCA(intptr_t, dimensions, dims_size);
        ALLOCA(intptr_t, steps, steps_size);

        if (gm_np_convert_xnd(args, nargs,
                              dimensions, dims_size,
                              steps, steps_size,
                              stack, outer_dims, ctx) < 0) {
            return -1;
        }

        return gm_np_map(kernel->set->Strided, args, nargs,
                         dimensions, steps, NULL, outer_dims);
    }
    case Xnd: {
        return gm_xnd_map(kernel->set->Xnd, stack, nargs, outer_dims,
                          kernel->set->vectorize, ctx);
    }

    default: {
        ndt_err_format(ctx, NDT_NotImplementedError, "apply not implemented");
        return -1;
      }
    }
}

static gm_kernel_t
select_kernel(const ndt_apply_spec_t *spec, const gm_kernel_set_t *set,
              ndt_context_t *ctx)
{
    gm_kernel_t kernel = {Xnd, NULL};

    kernel.set = set;

    switch (spec->tag) {
    case C:
        if (set->C != NULL) {
            kernel.tag = C;
            return kernel;
        }
        goto TryStrided;

    case Fortran:
        if (set->Fortran != NULL) {
            kernel.tag = Fortran;
            return kernel;
        }
        /* fall through */

    case Strided: TryStrided:
        if (set->Strided != NULL) {
            kernel.tag = Strided;
            return kernel;
        }
        /* fall through */

    case Xnd:
        if (set->Xnd != NULL) {
            kernel.tag = Xnd;
            return kernel;
        }
    }

    kernel.set = NULL;
    ndt_err_format(ctx, NDT_RuntimeError, "could not find specialized kernel");
    return kernel;
}

/* Look up a multimethod by name and select a kernel. */
gm_kernel_t
gm_select(ndt_apply_spec_t *spec, const gm_tbl_t *tbl, const char *name,
          const ndt_t *in_types[], int nin, const xnd_t args[],
          ndt_context_t *ctx)
{
    gm_kernel_t empty_kernel = {Xnd, NULL};
    const gm_func_t *f;
    int i;

    f = gm_tbl_find(tbl, name, ctx);
    if (f == NULL) {
        return empty_kernel;
    }

    for (i = 0; i < f->nkernels; i++) {
        const gm_kernel_set_t *set = &f->kernels[i];
        if (ndt_typecheck(spec, set->sig, in_types, nin, set->constraint, args,
                          ctx) < 0) {
            ndt_err_clear(ctx);
            continue;
        }
        return select_kernel(spec, set, ctx);
    }

    ndt_err_format(ctx, NDT_TypeError, "could not find kernel");
    return empty_kernel;
}
