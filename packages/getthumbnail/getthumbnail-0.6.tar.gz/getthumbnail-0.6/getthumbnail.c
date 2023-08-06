/* -*- C++ -*-
 * File: dcraw_half.c
 * Copyright 2008-2016 LibRaw LLC (info@libraw.org)
 * Created: Sat Mar  8 , 2008
 *
 * LibRaw  C API sample:  emulates "dcraw  -h"
 *
LibRaw is free software; you can redistribute it and/or modify
it under the terms of the one of two licenses as you choose:
1. GNU LESSER GENERAL PUBLIC LICENSE version 2.1
   (See file LICENSE.LGPL provided in LibRaw distribution archive for details).
2. COMMON DEVELOPMENT AND DISTRIBUTION LICENSE (CDDL) Version 1.0
   (See file LICENSE.CDDL provided in LibRaw distribution archive for details).
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

#include "libraw/libraw.h"
#include "Python.h"


static PyObject * getthumbnail(PyObject *self, PyObject *args)
{
  const char *path;
  const char *savepath;

  if(!PyArg_ParseTuple(args, "ss", &path, &savepath))
    return NULL;

  libraw_data_t *iprc = libraw_init(0);

  if (!iprc)
  {
    fprintf(stderr, "Cannot create libraw handle\n");
    exit(1);
  }

  iprc->params.half_size = 1; /* dcraw -h */

  char outfn[1024];
  libraw_open_file(iprc, path);

  printf("Processing %s (%s %s)\n", path, iprc->idata.make, iprc->idata.model);
  libraw_unpack_thumb(iprc);

  strcpy(outfn, savepath);
  printf("Writing to %s\n", outfn);

  libraw_dcraw_thumb_writer(iprc, outfn);
  libraw_close(iprc);
  return Py_None;
}

static char getthumbnail_docs[] = 
  "getthumbnail(path, savepath): Extract the thumbnail from path and save it to savepath";

static PyMethodDef getthumbnail_funcs[] = {
  {"getthumbnail", (PyCFunction)getthumbnail, METH_VARARGS, getthumbnail_docs},
  {NULL}
};

static struct PyModuleDef getthumbnailmodule = {
  PyModuleDef_HEAD_INIT,
  "getthumbnail",
  NULL,
  -1,
  getthumbnail_funcs
};

PyMODINIT_FUNC PyInit_getthumbnail(void) {
  return PyModule_Create(&getthumbnailmodule);
}
