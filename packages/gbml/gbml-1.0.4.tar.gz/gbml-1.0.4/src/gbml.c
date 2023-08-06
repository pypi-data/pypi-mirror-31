//
//   Copyright 2015, The Materials Project
//

#include <Python.h>
#include <numpy/arrayobject.h>
#include "predict.h"

// package:     gbml
// module:      core
// function:    predict
// python call: gbml.core.predict()

static char core_docstring[] =
    "This module provides an interface to the core GBM-Locfit C functions.";
static char predict_docstring[] =
    "This module makes GBM-Locfit predictions.";

// gbml_predict function declaration
static PyObject *gbml_predict(PyObject *self, PyObject *args);

// method definition
static PyMethodDef predictModule_methods[] = { 
    {"predict", gbml_predict, METH_VARARGS, predict_docstring},
    {NULL, NULL, 0, NULL} };

// init function definition
PyMODINIT_FUNC initcore(void)
{
  Py_InitModule3("core", predictModule_methods, core_docstring);

  // Required for numpy
  import_array();
}

// gbml_predict function definition
static PyObject *gbml_predict(PyObject *self, PyObject *args)
{
  char *filename;
  int nPredictions;
  PyArrayObject *descriptorsArray;
  PyArrayObject *predictionsArray;

  // Parse input tuple
  if (!PyArg_ParseTuple(args, "siO!O!", &filename, &nPredictions, &PyArray_Type, &descriptorsArray,
      &PyArray_Type, &predictionsArray)) return NULL;

  // Get C pointer to descriptors
  double *descriptors = (double *) PyArray_DATA(descriptorsArray);
  double *predictions = (double *) PyArray_DATA(predictionsArray);

  // Call external C function
  int flag = predict(filename, nPredictions, descriptors, predictions);

  if (flag)
    return NULL;
  else
    Py_RETURN_NONE;
}
