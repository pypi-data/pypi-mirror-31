
/* Depot module using dictionary interface */
/* Author: Yoshitaka Hirano, after dbmmodule.c */

#include "Python.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "depot.h"

typedef struct {
        char *dptr;
        int   dsize;
      } datum;

typedef struct {
    PyObject_HEAD
    DEPOT *depot;
} depotobject;

static PyTypeObject Depottype;

#define is_depotobject(v) ((v)->ob_type == &Depottype)
#define check_depotobject_open(v) if ((v)->depot == NULL) \
               { PyErr_SetString(DepotError, "DEPOT object has already been closed"); \
                 return NULL; }

static PyObject *DepotError;

static PyObject *
new_depot_object(char *file, int flags, int size)
{
    depotobject *dp;

    dp = PyObject_New(depotobject, &Depottype);
    if (dp == NULL)
        return NULL;
    if (!(dp->depot = dpopen(file, flags, size))) {
        PyErr_SetString(DepotError, dperrmsg(dpecode));
        Py_DECREF(dp);
        return NULL;
    }
    return (PyObject *)dp;
}

/* Methods */

void
_depot_close(depotobject* self)
{
    if (self->depot) {
        dpclose(self->depot);
        self->depot = NULL;
    }
}

static void
depot_dealloc(depotobject* self)
{
    _depot_close(self);
    PyObject_Del(self);
}

static int
depot_length(depotobject *dp)
{
    if (dp->depot == NULL) {
        PyErr_SetString(DepotError, "DEPOT object has already been closed");
        return -1;
    }
    return dprnum(dp->depot);
}

static PyObject *
depot_subscript(depotobject *dp, register PyObject *key)
{
    datum drec, krec;
    int tmp_size;
    PyObject *ret;

    if (!PyArg_Parse(key, "s#", &krec.dptr, &tmp_size)) {
        PyErr_SetString(PyExc_TypeError,
                        "depot mappings have string indices only");
        return NULL;
    }

    krec.dsize = tmp_size;
    check_depotobject_open(dp);
    drec.dptr = dpget(dp->depot, krec.dptr, krec.dsize, 0, -1, &tmp_size);
    drec.dsize = tmp_size;
    if (!drec.dptr) {
        if (dpecode == DP_ENOITEM) {
            PyErr_SetString(PyExc_KeyError,
                            PyString_AS_STRING((PyStringObject *)key));
        } else {
            PyErr_SetString(DepotError, dperrmsg(dpecode));
        }
        return NULL;
    }

    ret = PyString_FromStringAndSize(drec.dptr, drec.dsize);
    free(drec.dptr);
    return ret;
}

static int
depot_ass_sub(depotobject *dp, PyObject *v, PyObject *w)
{
    datum krec, drec;
    int tmp_size;

    if (!PyArg_Parse(v, "s#", &krec.dptr, &tmp_size)) {
        PyErr_SetString(PyExc_TypeError,
                        "depot mappings have string indices only");
        return -1;
    }
    krec.dsize = tmp_size;
    if (dp->depot == NULL) {
        PyErr_SetString(DepotError, "DEPOT object has already been closed");
        return -1;
    }
    if (w == NULL) {
        if (dpout(dp->depot, krec.dptr, krec.dsize) == 0) {
            if (dpecode == DP_ENOITEM) {
                PyErr_SetString(PyExc_KeyError,
                                PyString_AS_STRING((PyStringObject *)v));
            } else {
                PyErr_SetString(DepotError, dperrmsg(dpecode));
            }
            return -1;
        }
    } else {
        if (!PyArg_Parse(w, "s#", &drec.dptr, &tmp_size)) {
            PyErr_SetString(PyExc_TypeError,
                            "depot mappings have string elements only");
            return -1;
        }
        drec.dsize = tmp_size;
        if (dpput(dp->depot, krec.dptr, krec.dsize, drec.dptr, drec.dsize, DP_DOVER) == 0) {
            PyErr_SetString(DepotError, dperrmsg(dpecode));
            return -1;
        }
    }
    return 0;
}

static PyMappingMethods depot_as_mapping = {
    (inquiry)depot_length,          /*mp_length*/
    (binaryfunc)depot_subscript,    /*mp_subscript*/
    (objobjargproc)depot_ass_sub,   /*mp_ass_subscript*/
};

static PyObject *
depot__close(register depotobject *dp, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":close"))
        return NULL;
    _depot_close(dp);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
depot_keys(register depotobject *dp, PyObject *args)
{
    register PyObject *v, *item;
    datum key;
    int err, tmp_size;

    if (!PyArg_ParseTuple(args, ":keys"))
        return NULL;
    check_depotobject_open(dp);
    v = PyList_New(0);
    if (v == NULL)
        return NULL;

    /* Init Iterator */
    if(!dpiterinit(dp->depot)) {
        PyErr_SetString(DepotError, dperrmsg(dpecode));
    }

    /* Scan Iterator */
    while((key.dptr = dpiternext(dp->depot, &tmp_size)) != NULL) {
        key.dsize = tmp_size;
        item = PyString_FromStringAndSize(key.dptr, key.dsize);
        free(key.dptr);
        if (item == NULL) {
            Py_DECREF(v);
            return NULL;
        }
        err = PyList_Append(v, item);
        Py_DECREF(item);
        if (err != 0) {
            Py_DECREF(v);
            return NULL;
        }
    }
    return v;
}

static PyObject *
depot_has_key(register depotobject *dp, PyObject *args)
{
    datum key;
    int val;
    int tmp_size;

    if (!PyArg_ParseTuple(args, "s#:has_key", &key.dptr, &tmp_size))
        return NULL;
    key.dsize = tmp_size;
    check_depotobject_open(dp);
    val = dpvsiz(dp->depot, key.dptr, key.dsize);
    if (val == -1) {
        if (dpecode == DP_ENOITEM) {
            Py_INCREF(Py_False);
            return Py_False;
        } else {
            PyErr_SetString(DepotError, dperrmsg(dpecode));
            return NULL;
        }
    } else {
        Py_INCREF(Py_True);
        return Py_True;
    }
}

static PyObject *
depot_get(register depotobject *dp, PyObject *args)
{
    datum key, val;
    PyObject *defvalue = Py_None, *ret;
    int tmp_size;

    if (!PyArg_ParseTuple(args, "s#|O:get",
                              &key.dptr, &tmp_size, &defvalue))
        return NULL;
    key.dsize = tmp_size;
    check_depotobject_open(dp);
    val.dptr = dpget(dp->depot, key.dptr, key.dsize, 0, -1, &tmp_size);
    val.dsize = tmp_size;
    if (val.dptr != NULL) {
        ret = PyString_FromStringAndSize(val.dptr, val.dsize);
        free(val.dptr);
    } else {
        Py_INCREF(defvalue);
        ret = defvalue;
    }

    return ret;
}

static PyObject *
depot_setdefault(register depotobject *dp, PyObject *args)
{
    datum key, val;
    PyObject *defvalue = NULL;
    int tmp_size;

    if (!PyArg_ParseTuple(args, "s#|S:setdefault",
                          &key.dptr, &tmp_size, &defvalue))
        return NULL;
    key.dsize = tmp_size;
    check_depotobject_open(dp);
    val.dptr = dpget(dp->depot, key.dptr, key.dsize, 0, -1, &tmp_size);
    val.dsize = tmp_size;
    if (val.dptr != NULL) {
        PyObject *ret;
        ret = PyString_FromStringAndSize(val.dptr, val.dsize);
        free(val.dptr);
        return ret;
    }

    if (defvalue == NULL) {
        defvalue = PyString_FromStringAndSize(NULL, 0);
        if (defvalue == NULL)
            return NULL;
    } else {
        Py_INCREF(defvalue);
    }

    val.dptr = PyString_AS_STRING(defvalue);
    val.dsize = PyString_GET_SIZE(defvalue);
    if (!dpput(dp->depot, key.dptr, key.dsize, val.dptr, val.dsize, DP_DOVER)) {
        PyErr_SetString(DepotError, dperrmsg(dpecode));
        return NULL;
    }
    return defvalue;
}

extern PyTypeObject PyDepotIterKey_Type;   /* Forward */
extern PyTypeObject PyDepotIterItem_Type;  /* Forward */
extern PyTypeObject PyDepotIterValue_Type; /* Forward */
static PyObject *depotiter_new(depotobject *, PyTypeObject *);

static PyObject *
depot_iterkeys(depotobject *dp)
{
    return depotiter_new(dp, &PyDepotIterKey_Type);
}

static PyObject *
depot_iteritems(depotobject *dp)
{
    return depotiter_new(dp, &PyDepotIterItem_Type);
}

static PyObject *
depot_itervalues(depotobject *dp)
{
    return depotiter_new(dp, &PyDepotIterValue_Type);
}


static PyMethodDef depot_methods[] = {
    {"close", (PyCFunction)depot__close, METH_VARARGS,
     "close()\nClose the database."},
    {"keys", (PyCFunction)depot_keys, METH_VARARGS,
     "keys() -> list\nReturn a list of all keys in the database."},
    {"has_key", (PyCFunction)depot_has_key, METH_VARARGS,
     "has_key(key} -> boolean\nReturn true if key is in the database."},
    {"get", (PyCFunction)depot_get, METH_VARARGS,
     "get(key[, default]) -> value\n"
     "Return the value for key if present, otherwise default."},
    {"setdefault", (PyCFunction)depot_setdefault, METH_VARARGS,
     "setdefault(key[, default]) -> value\n"
     "Return the value for key if present, otherwise default.  If key\n"
     "is not in the database, it is inserted with default as the value."},
    {"iterkeys", (PyCFunction)depot_iterkeys, METH_NOARGS,
     "D.iterkeys() -> an iterator over the keys of D"},
    {"iteritems", (PyCFunction)depot_iteritems, METH_NOARGS,
     "D.iteritems() -> an iterator over the (key, value) items of D"},
    {"itervalues", (PyCFunction)depot_itervalues, METH_NOARGS,
     "D.itervalues() -> an iterator over the values of D"},
    {NULL, NULL} /* sentinel */
};

static PyObject *
depot_getattr(depotobject *dp, char *name)
{
    return Py_FindMethod(depot_methods, (PyObject *)dp, name);
}

static PyTypeObject Depottype = {
    PyObject_HEAD_INIT(NULL)
    0,
    "depot.depot",
    sizeof(depotobject),
    0,
    (destructor)depot_dealloc,  /*tp_dealloc*/
    0,                          /*tp_print*/
    (getattrfunc)depot_getattr, /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_compare*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number*/
    0,                          /*tp_as_sequence*/
    &depot_as_mapping,          /*tp_as_mapping*/
};

/* ----------------------------------------------------------------- */
/* Depot iterator                                                    */
/* ----------------------------------------------------------------- */

typedef struct {
    PyObject_HEAD
    depotobject *depot;        /* Set to NULL when iterator is exhausted */
    PyObject* di_result; /* reusable result tuple for iteritems */
} depotiterobject;

static PyObject *
depotiter_new(depotobject *dp, PyTypeObject *itertype)
{
    depotiterobject *di;
    di = PyObject_New(depotiterobject, itertype);
    if (di == NULL)
        return NULL;
    Py_INCREF(dp);
    di->depot = dp;
    dpiterinit(dp->depot);

    if (itertype == &PyDepotIterItem_Type) {
        di->di_result = PyTuple_Pack(2, Py_None, Py_None);
        if (di->di_result == NULL) {
            Py_DECREF(di);
            return NULL;
        }
    } else {
        di->di_result = NULL;
    }
    return (PyObject *)di;
}

static void
depotiter_dealloc(depotiterobject *di)
{
    Py_XDECREF(di->depot);
    Py_XDECREF(di->di_result);
    PyObject_Del(di);
}

static PySequenceMethods depotiter_as_sequence = {
    0, /* sq_concat */
};


static PyObject *depotiter_iternextkey(depotiterobject *di)
{
    datum key;
    depotobject *d = di->depot;
    int tmp_size;
    PyObject *ret;

    if (d == NULL)
        return NULL;
    assert(is_depotobject(d));

    if (!(key.dptr = dpiternext(d->depot, &tmp_size))) {
        if (dpecode != DP_ENOITEM) {
            PyErr_SetString(DepotError, dperrmsg(dpecode));
        }
        Py_DECREF(d);
        di->depot = NULL;
        return NULL;
    }
    key.dsize = tmp_size;

    ret = PyString_FromStringAndSize(key.dptr, key.dsize);
    free(key.dptr);

    return ret;
}

static PyObject *depotiter_iternextitem(depotiterobject *di)
{
    datum key, val;
    PyObject *pykey, *pyval, *result = di->di_result;
    int tmp_size;
    depotobject *d = di->depot;

    if (d == NULL)
        return NULL;
    assert(is_depotobject(d));

    if (!(key.dptr = dpiternext(d->depot, &tmp_size))) {
        if (dpecode != DP_ENOITEM) {
            PyErr_SetString(DepotError, dperrmsg(dpecode));
        }
        goto fail;
    }
    key.dsize = tmp_size;
    pykey = PyString_FromStringAndSize(key.dptr, key.dsize);

    if (!(val.dptr = dpget(d->depot, key.dptr, key.dsize, 0, -1, &tmp_size))) {
        PyErr_SetString(DepotError, dperrmsg(dpecode));
        free(key.dptr);
        Py_DECREF(pykey);
        goto fail;
    }
    val.dsize = tmp_size;
    pyval = PyString_FromStringAndSize(val.dptr, val.dsize);
    free(key.dptr);
    free(val.dptr);

    if (result->ob_refcnt == 1) {
        Py_INCREF(result);
        Py_DECREF(PyTuple_GET_ITEM(result, 0));
        Py_DECREF(PyTuple_GET_ITEM(result, 1));
    } else {
        result = PyTuple_New(2);
        if (result == NULL)
            return NULL;
    }

    PyTuple_SET_ITEM(result, 0, pykey);
    PyTuple_SET_ITEM(result, 1, pyval);
    return result;

fail:
    Py_DECREF(d);
    di->depot = NULL;
    return NULL;
}

static PyObject *depotiter_iternextvalue(depotiterobject *di)
{
    datum key, val;
    PyObject *pyval;
    int tmp_size;
    depotobject *d = di->depot;

    if (d == NULL)
        return NULL;
    assert(is_depotobject(d));

    if (!(key.dptr = dpiternext(d->depot, &tmp_size))) {
        if (dpecode != DP_ENOITEM) {
            PyErr_SetString(DepotError, dperrmsg(dpecode));
        }
        goto fail;
    }
    key.dsize = tmp_size;

    if (!(val.dptr = dpget(d->depot, key.dptr, key.dsize, 0, -1, &tmp_size))) {
        PyErr_SetString(DepotError, dperrmsg(dpecode));
        free(key.dptr);
        goto fail;
    }
    val.dsize = tmp_size;
    pyval = PyString_FromStringAndSize(val.dptr, val.dsize);
    free(key.dptr);
    free(val.dptr);

    return pyval;

fail:
    Py_DECREF(d);
    di->depot = NULL;
    return NULL;
}


PyTypeObject PyDepotIterKey_Type = {
    PyObject_HEAD_INIT(&PyType_Type)
    0,                              /* ob_size */
    "depoty-keyiterator",           /* tp_name */
    sizeof(depotiterobject),        /* tp_basicsize */
    0,                              /* tp_itemsize */
    /* methods */
    (destructor)depotiter_dealloc,  /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_compare */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    &depotiter_as_sequence,         /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    0,                              /* tp_str */
    PyObject_GenericGetAttr,        /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,             /* tp_flags */
    0,                              /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    PyObject_SelfIter,              /* tp_iter */
    (iternextfunc)depotiter_iternextkey, /* tp_iternext */
};


PyTypeObject PyDepotIterItem_Type = {
    PyObject_HEAD_INIT(&PyType_Type)
    0,                              /* ob_size */
    "depot-itemiterator",           /* tp_name */
    sizeof(depotiterobject),        /* tp_basicsize */
    0,                              /* tp_itemsize */
    /* methods */
    (destructor)depotiter_dealloc,  /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_compare */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    &depotiter_as_sequence,         /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    0,                              /* tp_str */
    PyObject_GenericGetAttr,        /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,             /* tp_flags */
    0,                              /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    PyObject_SelfIter,              /* tp_iter */
    (iternextfunc)depotiter_iternextitem, /* tp_iternext */
};

PyTypeObject PyDepotIterValue_Type = {
    PyObject_HEAD_INIT(&PyType_Type)
    0,                              /* ob_size */
    "depot-valueiterator",          /* tp_name */
    sizeof(depotiterobject),        /* tp_basicsize */
    0,                              /* tp_itemsize */
    /* methods */
    (destructor)depotiter_dealloc,  /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_compare */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    &depotiter_as_sequence,         /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    0,                              /* tp_str */
    PyObject_GenericGetAttr,        /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,             /* tp_flags */
    0,                              /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    PyObject_SelfIter,              /* tp_iter */
    (iternextfunc)depotiter_iternextvalue, /* tp_iternext */
};


/* ----------------------------------------------------------------- */
/* depot module                                                      */
/* ----------------------------------------------------------------- */

static PyObject *
depotopen(PyObject *self, PyObject *args)
{
    char *name;
    char *flags = "r";
    int size = -1;
    int iflags;

    if (!PyArg_ParseTuple(args, "s|si:open", &name, &flags, &size))
        return NULL;
    switch (flags[0]) {
        case 'r':
            iflags = DP_OREADER;
            break;
        case 'w':
            iflags = DP_OWRITER;
            break;
        case 'c':
            iflags = DP_OWRITER | DP_OCREAT | DP_OSPARSE;
            break;
        case 'n':
            iflags = DP_OWRITER | DP_OCREAT | DP_OSPARSE | DP_OTRUNC;
            break;
        default:
            PyErr_SetString(DepotError,
                            "arg 2 to open should be 'r', 'w', 'c', or 'n'");
            return NULL;
    }
    return new_depot_object(name, iflags, size);
}

static PyMethodDef depotmodule_methods[] = {
    { "open", (PyCFunction)depotopen, METH_VARARGS,
      "open(path[, flag[, size]]) -> mapping\n"
      "Return a database object."},
    { 0, 0 },
};

PyMODINIT_FUNC
initdepot(void) {
    PyObject *m, *d, *s;

    Depottype.ob_type = &PyType_Type;
    m = Py_InitModule("depot", depotmodule_methods);
    if (m == NULL)
        return;
    d = PyModule_GetDict(m);
    if (DepotError == NULL)
        DepotError = PyErr_NewException("depot.error", NULL, NULL);
    s = PyString_FromString("depot");
    if (s != NULL) {
        PyDict_SetItemString(d, "library", s);
        Py_DECREF(s);
    }
    if (DepotError != NULL)
        PyDict_SetItemString(d, "error", DepotError);
}
