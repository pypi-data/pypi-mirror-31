/** @file mga/module/utility.cpp
 *
 *		Utility functions for MGA module.
 *
 *		$Revision: 25250 $
 *		$Date: 2017-06-01 12:13:32 +0200 (Thu, 01 Jun 2017) $
 *		$Author: lillo $
 *
 *		\defgroup mga_module MGA Python extension module
 *		The MGA Python extension module is a wrapper around the \ref mga_client and part of the \ref CL for Python.
 */

/*@{*/

#include "module.h"

static string sLanguage = "";


/**
 *	Addition operator for the MGA.Decimal type.
 *	\param	self				First MGA.Decimal operand.
 *	\param	other				Second MGA.Decimal operand.
 *	\return						A new reference to a MGA.Decimal object with the result of the operation.
 */
static MGA::DecimalObject *
MGA_Decimal_add(MGA::DecimalObject *self, MGA::DecimalObject *other)
{
	MGA::DecimalObject *result;
	
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue + other->fValue;
	
	return result;
}


/**
 *	Subtraction operator for the MGA.Decimal type.
 *	\param	self				First MGA.Decimal operand.
 *	\param	other				Second MGA.Decimal operand.
 *	\return						A new reference to a MGA.Decimal object with the result of the operation.
 */
static MGA::DecimalObject *
MGA_Decimal_sub(MGA::DecimalObject *self, MGA::DecimalObject *other)
{
	MGA::DecimalObject *result;
	
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue - other->fValue;
	
	return result;
}


/**
 *	Multiplication operator for the MGA.Decimal type.
 *	\param	self				First MGA.Decimal operand.
 *	\param	other				Second MGA.Decimal operand.
 *	\return						A new reference to a MGA.Decimal object with the result of the operation.
 */
static MGA::DecimalObject *
MGA_Decimal_mul(MGA::DecimalObject *self, MGA::DecimalObject *other)
{
	MGA::DecimalObject *result;
	
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue * other->fValue;
	
	return result;
}


/**
 *	Deprecated (old) division operator for the MGA.Decimal type.
 *	\param	self				First MGA.Decimal operand.
 *	\param	other				Second MGA.Decimal operand.
 *	\return						A new reference to a MGA.Decimal object with the result of the operation.
 */
static MGA::DecimalObject *
MGA_Decimal_classic_div(MGA::DecimalObject *self, MGA::DecimalObject *other)
{
	MGA::DecimalObject *result;
	
	if ((Py_DivisionWarningFlag >= 2) && (PyErr_Warn(PyExc_DeprecationWarning, "decimal classic division") < 0))
		return NULL;
	
	if (other->fValue == 0) {
		PyErr_SetString(PyExc_ZeroDivisionError, "decimal division");
		return NULL;
	}
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue / other->fValue;
	
	return result;
}


/**
 *	Remainder operator for the MGA.Decimal type.
 *	\param	self				First MGA.Decimal operand.
 *	\param	other				Second MGA.Decimal operand.
 *	\return						A new reference to a MGA.Decimal object with the result of the operation.
 */
static MGA::DecimalObject *
MGA_Decimal_rem(MGA::DecimalObject *self, MGA::DecimalObject *other)
{
	MGA::DecimalObject *result;
	
	if (other->fValue == 0) {
		PyErr_SetString(PyExc_ZeroDivisionError, "decimal division");
		return NULL;
	}
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue % other->fValue;
	
	return result;
}


/**
 *	divmod operator for the MGA.Decimal type. Returns a tuple with the quotient and remainder of the division between \a self and \a other.
 *	\param	self				First MGA.Decimal operand.
 *	\param	other				Second MGA.Decimal operand.
 *	\return						A new reference to a MGA.Decimal object with the result of the operation.
 */
static PyObject *
MGA_Decimal_divmod(MGA::DecimalObject *self, MGA::DecimalObject *other)
{
	MGA::DecimalObject *quotient, *remainder;
	
	if (other->fValue == 0) {
		PyErr_SetString(PyExc_ZeroDivisionError, "decimal division");
		return NULL;
	}
	quotient = MGA::DecimalObject::Allocate();
	quotient->fValue = (self->fValue / other->fValue).Floor();
	
	remainder = MGA::DecimalObject::Allocate();
	remainder->fValue = self->fValue % other->fValue;
	
	return Py_BuildValue("(OO)", quotient, remainder);
}


/**
 *	Exponentiation operator for the MGA.Decimal type.
 *	\param	self				First MGA.Decimal operand.
 *	\param	other				Second MGA.Decimal operand.
 *	\param	unused				Unused.
 *	\return						A new reference to a MGA.Decimal object with the result of the operation.
 */
static MGA::DecimalObject *
MGA_Decimal_pow(MGA::DecimalObject *self, MGA::DecimalObject *other, PyObject *unused)
{
	MGA::DecimalObject *result;
	
	if (unused != Py_None) {
		PyErr_SetString(PyExc_TypeError, "pow() 3rd argument not allowed unless all arguments are integers");
		return NULL;
	}
	
	if (other->fValue == 0) {
		result = MGA::DecimalObject::Allocate();
		result->fValue = 1;
		
		return result;
	}
	if (self->fValue == 0) {
		if (other->fValue < 0) {
			PyErr_SetString(PyExc_ZeroDivisionError, "0.0 cannot be raised to a negative power");
			return NULL;
		}
		
		result = MGA::DecimalObject::Allocate();
		result->fValue = 0;
		
		return result;
	}
	if ((self->fValue < 0) && (other->fValue != other->fValue.Floor())) {
		PyErr_SetString(PyExc_ValueError, "negative number cannot be raised to a fractional power");
		return NULL;
	}
	
#ifdef CL_DECIMAL_MPDEC
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue.Pow(other->fValue);
#else
	errno = 0;
	double v = pow((double)self->fValue, (double)other->fValue);
	if (errno != 0) {
		PyErr_SetFromErrno(errno == ERANGE ? PyExc_OverflowError : PyExc_ValueError);
		return NULL;
	}
	result = MGA::DecimalObject::Allocate();
	result->fValue = v;
#endif
	
	return result;
}


/**
 *	Returns the negated version of input MGA.Decimal object.
 *	\param	self				MGA.Decimal to be negated.
 *	\return						A new reference to a MGA.Decimal object with the result of the operation.
 */
static MGA::DecimalObject *
MGA_Decimal_neg(MGA::DecimalObject *self)
{
	MGA::DecimalObject *result;
	
	result = MGA::DecimalObject::Allocate();
	result->fValue = -self->fValue;
	
	return result;
}


/**
 *	Returns the positive version of input MGA.Decimal object. Actually just returns a new reference to \a self.
 *	\param	self				Input MGA.Decimal.
 *	\return						A new reference to \a self.
 */
static MGA::DecimalObject *
MGA_Decimal_pos(MGA::DecimalObject *self)
{
	Py_INCREF(self);
	return self;
}


/**
 *	Returns the absolute value of input MGA.Decimal object.
 *	\param	self				MGA.Decimal whose absolute value is to be returned.
 *	\return						A new reference to a MGA.Decimal object with the result of the operation.
 */
static MGA::DecimalObject *
MGA_Decimal_abs(MGA::DecimalObject *self)
{
	MGA::DecimalObject *result;
	
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue.Abs();
	
	return result;
}


/**
 *	Checks if a specified MGA.Decimal object is not zero.
 *	\param	self				MGA.Decimal to be checked.
 *	\return						0 if \a self is zero, -1 otherwise.
 */
static int
MGA_Decimal_nonzero(MGA::DecimalObject *self)
{
	return self->fValue != 0;
}


/**
 *	Coerces operand in \a pw to MGA.Decimal operand in \a pv.
 *	\param	pv					First operand (MGA.Decimal).
 *	\param	pw					Second operand (can be int, long or float), to be converted to MGA.Decimal.
 *	\retval	0					Coersion successful; \a pw converted to MGA.Decimal.
 *	\retval	1					Coersion failed.
 */
static int
MGA_Decimal_coerce(PyObject **pv, PyObject **pw)
{
	MGA::DecimalObject *object;
	
#ifndef CL_DECIMAL_MPDEC
	if (PyInt_Check(*pw)) {
		int32 value = PyInt_AS_LONG(*pw);
		object = MGA::DecimalObject::Allocate();
		object->fValue = value;
		*pw = (PyObject *)object;
		Py_INCREF(*pv);
		return 0;
	}
	else if (PyLong_Check(*pw)) {
		int64 value = PyLong_AsLongLong(*pw);
		if ((value == -1) && (PyErr_Occurred())) {
			PyErr_Clear();
			return 1;
		}
		if ((value < CL_DECIMAL_MIN) || (value > CL_DECIMAL_MAX))
			return 1;
		object = MGA::DecimalObject::Allocate();
		object->fValue = value * CL_DECIMAL_UNIT;
		*pw = (PyObject *)object;
		Py_INCREF(*pv);
		return 0;
	}
	else
#endif
	if (PyFloat_Check(*pw)) {
		double value = PyFloat_AS_DOUBLE(*pw);
		object = MGA::DecimalObject::Allocate();
		object->fValue = value;
		*pw = (PyObject *)object;
		Py_INCREF(*pv);
		return 0;
	}
	else if (PyObject_TypeCheck(*pw, &MGA::DecimalType)) {
		Py_INCREF(*pv);
		Py_INCREF(*pw);
		return 0;
	}
#ifdef CL_DECIMAL_MPDEC
	else {
		bool invalid, overflow;
		PyObject *o = PyObject_Str(*pw);
		if (!o) {
			PyErr_Clear();
			return 1;
		}
		object = MGA::DecimalObject::Allocate();
		object->fValue = CL_Decimal::FromString(PyString_AS_STRING(o), &invalid, &overflow);
		Py_DECREF(o);
		if ((invalid) || (overflow)) {
			Py_DECREF(object);
			return 1;
		}
		*pw = (PyObject *)object;
		Py_INCREF(*pv);
		return 0;
	}
#endif

	return 1;
}


/**
 *	Casts the MGA.Decimal object in \a self to an int.
 *	\param	self				MGA.Decimal object to be casted to int.
 *	\return						An int object representing \a self.
 */
static PyObject *
MGA_Decimal_int(MGA::DecimalObject *self)
{
#ifdef CL_DECIMAL_MPDEC
	int64 value = self->fValue.ToInt64();
#else
	int64 value = (int64)self->fValue / CL_DECIMAL_UNIT;
#endif
	if ((value >= -2147483647L - 1) && (value <= 2147483647L))
		return PyInt_FromLong((long)value);
	else
		return PyLong_FromLongLong(value);
}


/**
 *	Casts the MGA.Decimal object in \a self to a long.
 *	\param	self				MGA.Decimal object to be casted to long.
 *	\return						A long object representing \a self.
 */
static PyObject *
MGA_Decimal_long(MGA::DecimalObject *self)
{
#ifdef CL_DECIMAL_MPDEC
	string s = self->fValue.Floor().ToString();
	return PyLong_FromString((char *)s.c_str(), NULL, 10);
#else
	return PyLong_FromLongLong((int64)self->fValue / CL_DECIMAL_UNIT);
#endif
}


/**
 *	Casts the MGA.Decimal object in \a self to a float.
 *	\param	self				MGA.Decimal object to be casted to float.
 *	\return						A float object representing \a self.
 */
static PyObject *
MGA_Decimal_float(MGA::DecimalObject *self)
{
	return PyFloat_FromDouble(self->fValue);
}


/**
 *	Integer division operator for the MGA.Decimal type.
 *	\param	self				First MGA.Decimal operand.
 *	\param	other				Second MGA.Decimal operand.
 *	\return						A new reference to a MGA.Decimal object with the integer part of the result of the operation.
 */
static MGA::DecimalObject *
MGA_Decimal_floor_div(MGA::DecimalObject *self, MGA::DecimalObject *other)
{
	PyObject *tuple;
	MGA::DecimalObject *result;
	
	tuple = MGA_Decimal_divmod(self, other);
	if ((!tuple) || (tuple == Py_NotImplemented))
		return (MGA::DecimalObject *)tuple;
	result = (MGA::DecimalObject *)PyTuple_GET_ITEM(tuple, 0);
	Py_INCREF(result);
	Py_DECREF(tuple);
	
	return result;
}


/**
 *	Division operator for the MGA.Decimal type.
 *	\param	self				First MGA.Decimal operand.
 *	\param	other				Second MGA.Decimal operand.
 *	\return						A new reference to a MGA.Decimal object with the result of the operation.
 */
static MGA::DecimalObject *
MGA_Decimal_div(MGA::DecimalObject *self, MGA::DecimalObject *other)
{
	MGA::DecimalObject *result;
	
	if (other->fValue == 0) {
		PyErr_SetString(PyExc_ZeroDivisionError, "decimal division");
		return NULL;
	}
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue / other->fValue;
	
	return result;
}



/**
 *	Returns an hash value generated from the \a self MGA.Decimal object, to be used to index mapped objects.
 *	\param	self				The MGA.Decimal object used as index.
 *	\return						The generated hash value.
 */
static long
MGA_Decimal_hash(MGA::DecimalObject *self)
{
	return _Py_HashDouble(self->fValue);
}


/**
 *	Converts an MGA.Decimal object to a string representation.
 *	\param	self				The MGA.Decimal object to be represented as a string.
 *	\return						A string object holding the string representation of \a self, in the form <tt>integer_part.fractional_part</tt>.
 */
static PyObject *
MGA_Decimal_str(MGA::DecimalObject *self)
{
#ifdef CL_DECIMAL_MPDEC
	string s = self->fValue.ToString();
	return PyString_FromString(s.c_str());
#else
	char buffer[64], *p;
	int64 iPart = self->fValue;
	bool neg = iPart < 0;
	if (neg)
		iPart = -iPart;
	int64 fPart = iPart % CL_DECIMAL_UNIT;
	int64 mask;
	
	iPart /= CL_DECIMAL_UNIT;
	mask = fPart >> 63LL;
	fPart = (fPart ^ mask) - mask;
	
	buffer[0] = 0;
	p = buffer;
	if (neg)
		*p++ = '-';
	if (iPart == 0) {
		*p++ = '0';
	}
	else {
		char *_buffer = p;
		while (iPart > 0) {
			memmove(_buffer + 1, _buffer, 62);
			_buffer[0] = '0' + (iPart % 10);
			iPart /= 10;
			p++;
		}
	}
	*p++ = '.';
	if (fPart == 0) {
		*p++ = '0';
	}
	else {
		int unit = CL_DECIMAL_UNIT;
		while ((unit > 0) && ((fPart % unit) != 0)) {
			unit /= 10;
			*p++ = '0' + ((fPart / unit) % 10);
		}
	}
	*p = 0;
	
	return PyString_FromString(buffer);
#endif
}


/**
 *	Compares an MGA.Decimal object with another Python object and returns the result of this comparision. Currently only supports
 *	comparing with MGA.Decimal, int, long and float objects; comparing with another object type will return Py_NotImplemented.
 *	\param	self				First operand (always MGA.Decimal type).
 *	\param	other				Second operand.
 *	\param	op					Python comparision operator.
 *	\return						A bool object holding the comparision result, or Py_NotImplemented if \a other is not MGA.Decimal, int, long or float.
 */
static PyObject *
MGA_Decimal_richcompare(MGA::DecimalObject *self, PyObject *other, int op)
{
	int result = 0;
	
	if (PyObject_TypeCheck(other, &MGA::DecimalType)) {
		MGA::DecimalObject *value = (MGA::DecimalObject *)other;
		switch (op) {
		case Py_EQ: result = self->fValue == value->fValue; break;
		case Py_NE: result = self->fValue != value->fValue; break;
		case Py_LE: result = self->fValue <= value->fValue; break;
		case Py_GE: result = self->fValue >= value->fValue; break;
		case Py_LT: result = self->fValue < value->fValue; break;
		case Py_GT: result = self->fValue > value->fValue; break;
		}
	}
	else if (PyInt_Check(other)) {
		long value = PyInt_AS_LONG(other);
		switch (op) {
		case Py_EQ: result = self->fValue == value; break;
		case Py_NE: result = self->fValue != value; break;
		case Py_LE: result = self->fValue <= value; break;
		case Py_GE: result = self->fValue >= value; break;
		case Py_LT: result = self->fValue < value; break;
		case Py_GT: result = self->fValue > value; break;
		}
	}
	else if (PyLong_Check(other)) {
#ifdef CL_DECIMAL_MPDEC
		PyObject *o = PyObject_Str(other);
		CL_Decimal value(string(PyString_AS_STRING(o)));
		Py_DECREF(o);
#else
		int64 value = PyLong_AsLongLong(other) * CL_DECIMAL_UNIT;
		if ((value == -1) && (PyErr_Occurred())) {
			PyErr_Clear();
			if (op == Py_EQ)
				result = -1;
			else
				result = 0;
		}
		else
#endif
		{
			switch (op) {
			case Py_EQ: result = self->fValue == value; break;
			case Py_NE: result = self->fValue != value; break;
			case Py_LE: result = self->fValue <= value; break;
			case Py_GE: result = self->fValue >= value; break;
			case Py_LT: result = self->fValue < value; break;
			case Py_GT: result = self->fValue > value; break;
			}
		}
	}
	else if (PyFloat_Check(other)) {
		double value = PyFloat_AS_DOUBLE(other);
		switch (op) {
		case Py_EQ: result = self->fValue == value; break;
		case Py_NE: result = self->fValue != value; break;
		case Py_LE: result = self->fValue <= value; break;
		case Py_GE: result = self->fValue >= value; break;
		case Py_LT: result = self->fValue < value; break;
		case Py_GT: result = self->fValue > value; break;
		}
	}
	else {
		Py_INCREF(Py_NotImplemented);
		return Py_NotImplemented;
	}
	
	return PyBool_FromLong(result);
}


/**
 *	Internal function to parse a decimal number from a Python string or unicode object.
 *	\param	result				#CL_Decimal object that will contain the parsed decimal on exit.
 *	\param	string				Python string or unicode object to be parsed.
 *	\param	overflow			On exit, this will return true if the parsed number generates an overflow.
 *	\return						True if parsing successful, False otherwise or if overflow.
 */
static bool
MGA_Decimal_from_string(CL_Decimal& result, PyObject *string, bool *overflow)
{
	PyObject *temp = NULL;
	std::string value;
	bool invalid = false;

	*overflow = false;
	
	if (PyUnicode_Check(string)) {
		temp = PyUnicode_AsUTF8String(string);
		string = temp;
	}
	value = CL_StringStripped(PyString_AS_STRING(string));
	Py_XDECREF(temp);
	
	if (value.empty())
		return false;
	result = CL_Decimal::FromString(value, &invalid, overflow);
	
	return !invalid;
}


/**
 *	Initialization method for the MGA.Decimal class. Accepts the "value" parameter with which to initialize the decimal number.
 *	\param	self				MGA.Decimal object being initialized.
 *	\param	args				Initialization arguments tuple.
 *	\param	kwds				Supported argument keywords. Accepted keywords are:
 *								- \e value: int, long, float or string object from which to fetch initial decimal value to be set.
 *	\retval	0					Initialization successful.
 *	\retval	-1					An error occured, and an exception was raised.
 */
static int
MGA_Decimal_init(MGA::DecimalObject *self, PyObject *args, PyObject *kwds)
{
	static char *kwlist[] = { "value", NULL };
	PyObject *value = NULL, *number;
	bool overflow = false, bad = false;
	
	self->fValue = 0LL;
	
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O", kwlist, &value))
		return -1;
	
	if (value) {
		if (PyObject_TypeCheck(value, &MGA::DecimalType)) {
			self->fValue = ((MGA::DecimalObject *)value)->fValue;
		}
		else if (PyInt_Check(value)) {
			self->fValue = (int32)PyInt_AS_LONG(value);
		}
		else if (PyLong_Check(value)) {
#ifdef CL_DECIMAL_MPDEC
			PyObject *o = PyObject_Str(value);
			self->fValue = CL_Decimal::FromString(string(PyString_AS_STRING(o)), &bad, &overflow);
			Py_DECREF(o);
#else
			int64 n = PyLong_AsLongLong(value);
			if (((n == -1) && (PyErr_Occurred())) || (n < CL_DECIMAL_MIN) || (n > CL_DECIMAL_MAX)) {
				PyErr_Clear();
				bad = overflow = true;
			}
			else {
				self->fValue = PyLong_AsLongLong(value) * CL_DECIMAL_UNIT;
			}
#endif
		}
		else if (PyFloat_Check(value)) {
			self->fValue = PyFloat_AS_DOUBLE(value);
		}
		else if (PyNumber_Check(value)) {
			number = PyNumber_Float(value);
			if (number) {
				self->fValue = PyFloat_AS_DOUBLE(number);
				Py_DECREF(number);
			}
			else
				return -1;
		}
		else if ((PyString_Check(value)) || (PyUnicode_Check(value)))
			bad = !MGA_Decimal_from_string(self->fValue, value, &overflow);
		else
			bad = true;
		
		if (bad) {
			if (overflow)
				PyErr_SetString(PyExc_OverflowError, "Arithmetic overflow");
			else
				PyErr_SetString(PyExc_ValueError, "Bad Decimal initializer");
			return -1;
		}
	}
	
	return 0;
}


/**
 *	Formats this decimal object into a string to be displayed.
 *	\param	self				The decimal object for which a formatted string is requested.
 *	\param	args				Arguments tuple.
 *	\param	kwds				Supported argument keywords. Accepted keywords are:
 *								- \e precision: Number of fractional digits of this decimal to be printed.
 *								- \e width: Total number of characters of the returned formatted string.
 *								- \e sep: If True, put a '<tt>,</tt>' separator between thousands.
 *								- \e padzero: If True, pad with '<tt>0</tt>' ahead of the decimal.
 *	\return						A string object containing the formatted decimal string, or NULL on exception.
 */
static PyObject *
MGA_Decimal_format(MGA::DecimalObject *self, PyObject *args, PyObject *kwds)
{
	static char *kwlist[] = { "precision", "width", "sep", "padzero", "monetary", NULL };
	int precision = -1, width = 0, padzero = 0, sep = 0, monetary=0;
	CL_LocaleInfo info;

	CL_GetLocaleInfo(&info, sLanguage);
	
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "|iiiii", kwlist, &precision, &width, &sep, &padzero, &monetary))
		return NULL;
	
	if (precision < 0)
		precision = 5;
	
	if (padzero)
		sep = 0;
	
	if (sep)
		monetary = 1;
	
	char buffer[64];
	int64 iPart = self->fValue;
	int64 fPart = iPart % CL_DECIMAL_UNIT;
	int64 mask;
	int32 iPos, fPos = 0;
	
	bool neg = (iPart < 0);
	iPart /= CL_DECIMAL_UNIT;
	iPart = CL_ABS64(iPart);
	mask = fPart >> 63LL;
	fPart = (fPart ^ mask) - mask;
	
	if (sep) {
		int32 i, digits = iPart ? ((int32)log10((double)iPart) + 1) : 1;
		
		iPos = digits + ((digits - 1) / 3);
		for (i = 0; i < iPos; i++) {
			if ((i % 4) == 3) {
				buffer[iPos - i - 1] = info.fThousandSep[0];
			}
			else {
				buffer[iPos - i - 1] = char(iPart % 10) + '0';
				iPart /= 10LL;
			}
		}
		buffer[iPos] = '\0';
	}
	else
		iPos = sprintf(buffer, CL_INT64_FORMAT_SPEC, iPart);
	
	if (precision) {
		if (monetary)
			buffer[iPos] = info.fDecimalSep[0];
		else
			buffer[iPos] = '.';
		fPos = 0;
		mask = CL_DECIMAL_UNIT / 10;
		do {
			buffer[iPos + ++fPos] = '0' + ((fPart / mask) % 10);
			if ((fPart % mask) == 0)
				break;
			mask /= 10;
		} while (fPos < 6);
		if (fPos < precision)
			memset(buffer + iPos + 1 + fPos, '0', precision - fPos);
		fPos = precision;
		buffer[iPos + 1 + fPos] = '\0';
		iPos++;
	}
	iPos += fPos;
	if (width) {
		if (width > iPos) {
			memmove(buffer + width - iPos, buffer, iPos + 1);
			if (padzero)
				memset(buffer, '0', width - iPos);
			else
				memset(buffer, ' ', width - iPos);
		}
	}
	if (((int64)self->fValue != 0) && (neg)) {
		memmove(buffer + 1, buffer, strlen(buffer) + 1);
		buffer[0] = '-';
	}
	
	return PyString_FromString(buffer);
}


static MGA::DecimalObject *
MGA_Decimal_ceil(MGA::DecimalObject *self, PyObject *args, PyObject *kwds)
{
	static char *kwlist[] = { "value", NULL };
	MGA::DecimalObject *value = NULL;
	MGA::DecimalObject *result = NULL;
	
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O&", kwlist, MGA::ConvertDecimal, &value))
		return NULL;
	
	if (!value) {
		value = MGA::DecimalObject::Allocate();
		value->fValue = 1;
	}
	if (value->fValue == 0) {
		Py_DECREF(value);
		PyErr_SetString(PyExc_ZeroDivisionError, "ceil operand cannot be zero");
		return NULL;
	}
	
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue.Ceil(value->fValue);
	
	Py_DECREF(value);
	
	return result;
}


static MGA::DecimalObject *
MGA_Decimal_floor(MGA::DecimalObject *self, PyObject *args, PyObject *kwds)
{
	static char *kwlist[] = { "value", NULL };
	MGA::DecimalObject *value = NULL;
	MGA::DecimalObject *result = NULL;
	
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O&", kwlist, MGA::ConvertDecimal, &value))
		return NULL;
	
	if (!value) {
		value = MGA::DecimalObject::Allocate();
		value->fValue = 1;
	}
	if (value->fValue == 0) {
		Py_DECREF(value);
		PyErr_SetString(PyExc_ZeroDivisionError, "floor operand cannot be zero");
		return NULL;
	}
	
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue.Floor(value->fValue);
	
	Py_DECREF(value);
	
	return result;
}


static MGA::DecimalObject *
MGA_Decimal_round(MGA::DecimalObject *self, PyObject *args, PyObject *kwds)
{
	static char *kwlist[] = { "value", NULL };
	MGA::DecimalObject *value = NULL;
	MGA::DecimalObject *result = NULL;
	
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O&", kwlist, MGA::ConvertDecimal, &value))
		return NULL;
	
	if (!value) {
		value = MGA::DecimalObject::Allocate();
		value->fValue = 1;
	}
	if (value->fValue == 0) {
		Py_DECREF(value);
		PyErr_SetString(PyExc_ZeroDivisionError, "round operand cannot be zero");
		return NULL;
	}
	
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue.Round(value->fValue);
	
	Py_DECREF(value);
	
	return result;
}


static MGA::DecimalObject *
MGA_Decimal_multiply(MGA::DecimalObject *self, PyObject *args, PyObject *kwds)
{
	static char *kwlist[] = { "other", "value", "mode", NULL };
	MGA::DecimalObject *other, *result;
	MGA::DecimalObject *value = NULL;
	int mode = CL_Decimal::ROUND;
	
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&|O&i", kwlist, MGA::ConvertDecimal, &other, MGA::ConvertDecimal, &value, &mode))
		return NULL;
	
	if (!value) {
		value = MGA::DecimalObject::Allocate();
		value->fValue = 1;
	}
	
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue.Multiply(other->fValue, value->fValue, (CL_Decimal::RoundType)mode);
	
	Py_DECREF(value);
	Py_DECREF(other);
	
	return result;
}


static MGA::DecimalObject *
MGA_Decimal_divide(MGA::DecimalObject *self, PyObject *args, PyObject *kwds)
{
	static char *kwlist[] = { "other", "value", "mode", NULL };
	MGA::DecimalObject *other, *result;
	MGA::DecimalObject *value = NULL;
	int mode = CL_Decimal::ROUND;
	
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&|O&i", kwlist, MGA::ConvertDecimal, &other, MGA::ConvertDecimal, &value, &mode))
		return NULL;
	
	if (!value) {
		value = MGA::DecimalObject::Allocate();
		value->fValue = 1;
	}
	if (value->fValue == 0) {
		Py_DECREF(value);
		PyErr_SetString(PyExc_ZeroDivisionError, "decimal division");
		return NULL;
	}
	
	result = MGA::DecimalObject::Allocate();
	result->fValue = self->fValue.Divide(other->fValue, value->fValue, (CL_Decimal::RoundType)mode);
	
	Py_DECREF(value);
	Py_DECREF(other);
	
	return result;
}


static MGA::DecimalObject *
MGA_Decimal_copy(MGA::DecimalObject *self, PyObject *args, PyObject *kwds)
{
	MGA::DecimalObject *value;
	
	value = MGA::DecimalObject::Allocate();
	value->fValue = self->fValue;
	
	return value;
}


static PyObject *
MGA_Decimal_reduce(MGA::DecimalObject *self, PyObject *args, PyObject *kwds)
{
	PyObject *tuple = PyTuple_New(2);
	PyObject *arguments = PyTuple_New(1);
	PyTuple_SET_ITEM(arguments, 0, MGA_Decimal_str(self));
	Py_INCREF(&MGA::DecimalType);
	PyTuple_SET_ITEM(tuple, 0, (PyObject *)&MGA::DecimalType);
	PyTuple_SET_ITEM(tuple, 1, arguments);
	return tuple;
}


static PyObject *
MGA_Decimal_set_locale(MGA::DecimalObject *self, PyObject *args, PyObject *kwds)
{
	static char *kwlist[] = { "lang", NULL };
	const char *lang;
	
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &lang))
		return NULL;
	
	sLanguage = lang;

	Py_RETURN_NONE;
}


static MGA::DecimalObject *
MGA_Decimal_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	return MGA::DecimalObject::Allocate();
}


static void
MGA_Decimal_dealloc(MGA::DecimalObject *self)
{
	self->~DecimalObject();
	self->ob_type->tp_free((PyObject*)self);
}


/** Vtable for MGA.Decimal numeric operations. */
static PyNumberMethods MGA_Decimal_as_number = {
	(binaryfunc)MGA_Decimal_add,			/* nb_add */
	(binaryfunc)MGA_Decimal_sub,			/* nb_subtract */
	(binaryfunc)MGA_Decimal_mul,			/* nb_multiply */
	(binaryfunc)MGA_Decimal_classic_div,	/* nb_divide */
	(binaryfunc)MGA_Decimal_rem,			/* nb_remainder */
	(binaryfunc)MGA_Decimal_divmod,			/* nb_divmod */
	(ternaryfunc)MGA_Decimal_pow,			/* nb_power */
	(unaryfunc)MGA_Decimal_neg,				/* nb_negative */
	(unaryfunc)MGA_Decimal_pos,				/* nb_positive */
	(unaryfunc)MGA_Decimal_abs,				/* nb_absolute */
	(inquiry)MGA_Decimal_nonzero,			/* nb_nonzero */
	0,										/* nb_invert */
	0,										/* nb_lshift */
	0,										/* nb_rshift */
	0,										/* nb_and */
	0,										/* nb_xor */
	0,										/* nb_or */
	(coercion)MGA_Decimal_coerce,			/* nb_coerce */
	(unaryfunc)MGA_Decimal_int,				/* nb_int */
	(unaryfunc)MGA_Decimal_long,			/* nb_long */
	(unaryfunc)MGA_Decimal_float,			/* nb_float */
	0,										/* nb_oct */
	0,										/* nb_hex */
	0,										/* nb_inplace_add */
	0,										/* nb_inplace_subtract */
	0,										/* nb_inplace_multiply */
	0,										/* nb_inplace_divide */
	0,										/* nb_inplace_remainder */
	0,										/* nb_inplace_power */
	0,										/* nb_inplace_lshift */
	0,										/* nb_inplace_rshift */
	0,										/* nb_inplace_and */
	0,										/* nb_inplace_xor */
	0,										/* nb_inplace_or */
	(binaryfunc)MGA_Decimal_floor_div,		/* nb_floor_divide */
	(binaryfunc)MGA_Decimal_div,			/* nb_true_divide */
	0,										/* nb_inplace_floor_divide */
	0,										/* nb_inplace_true_divide */
};


static PyMethodDef MGA_Decimal_methods[] = {
	{	"format",			(PyCFunction)MGA_Decimal_format,			METH_VARARGS | METH_KEYWORDS,	"format([precision, width, sep, padzero]) -> str\n\nFormats the number into a string with specified precision." },
	{	"ceil",				(PyCFunction)MGA_Decimal_ceil,				METH_VARARGS | METH_KEYWORDS,	"ceil([value]) -> Decimal\n\nReturns number rounded up to given value." },
	{	"floor",			(PyCFunction)MGA_Decimal_floor,				METH_VARARGS | METH_KEYWORDS,	"floor([value]) -> Decimal\n\nReturns number rounded down to given value." },
	{	"round",			(PyCFunction)MGA_Decimal_round,				METH_VARARGS | METH_KEYWORDS,	"round([value]) -> Decimal\n\nReturns number rounded to given value." },
	{	"multiply",			(PyCFunction)MGA_Decimal_multiply,			METH_VARARGS | METH_KEYWORDS,	"multiply(other [, value, mode])\n\nMultiplies and rounds number by a given value using mode for rounding." },
	{	"divide",			(PyCFunction)MGA_Decimal_divide,			METH_VARARGS | METH_KEYWORDS,	"divide(other [, value, mode])\n\nMultiplies and rounds number by a given value using mode for rounding." },
	{	"__copy__",			(PyCFunction)MGA_Decimal_copy,				METH_VARARGS | METH_KEYWORDS,	"__copy__() -> Decimal\n\nReturns a copy of the decimal." },
	{	"__deepcopy__",		(PyCFunction)MGA_Decimal_copy,				METH_VARARGS | METH_KEYWORDS,	"__deepcopy__() -> Decimal\n\nReturns a copy of the decimal." },
	{	"__reduce__",		(PyCFunction)MGA_Decimal_reduce,			METH_VARARGS | METH_KEYWORDS,	"__reduce__() -> tuple\n\nReduce method for pickling support." },
	{	"set_locale",		(PyCFunction)MGA_Decimal_set_locale,		METH_VARARGS | METH_KEYWORDS | METH_CLASS,		"set_locale(lang)\n\nSets the current locale for decimal format." },
	{	NULL }
};


/** Vtable describing the MGA.Decimal type. */
PyTypeObject MGA::DecimalType = {
	PyObject_HEAD_INIT(NULL)
    0,										/* ob_size */
    "kongalib.Decimal",						/* tp_name */
    sizeof(MGA::DecimalObject),				/* tp_basicsize */
	0,										/* tp_itemsize */
	(destructor)MGA_Decimal_dealloc,		/* tp_dealloc */
	0,										/* tp_print */
	0,										/* tp_getattr */
	0,										/* tp_setattr */
	0,										/* tp_compare */
	(reprfunc)MGA_Decimal_str,				/* tp_repr */
	&MGA_Decimal_as_number,					/* tp_as_number */
	0,										/* tp_as_sequence */
	0,										/* tp_as_mapping */
	(hashfunc)MGA_Decimal_hash,				/* tp_hash */
	0,										/* tp_call */
	(reprfunc)MGA_Decimal_str,				/* tp_str */
	0,										/* tp_getattro */
	0,										/* tp_setattro */
	0,										/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,						/* tp_flags */
	"Decimal objects",						/* tp_doc */
	0,										/* tp_traverse */
	0,										/* tp_clear */
	(richcmpfunc)MGA_Decimal_richcompare,	/* tp_richcompare */
	0,										/* tp_weaklistoffset */
	0,										/* tp_iter */
	0,										/* tp_iternext */
	MGA_Decimal_methods,					/* tp_methods */
	0,										/* tp_members */
	0,										/* tp_getset */
	0,										/* tp_base */
	0,										/* tp_dict */
	0,										/* tp_descr_get */
	0,										/* tp_descr_set */
	0,										/* tp_dictoffset */
	(initproc)MGA_Decimal_init,				/* tp_init */
	0,										/* tp_alloc */
	(newfunc)MGA_Decimal_new,				/* tp_new */
};


MGA::DecimalObject *
MGA::DecimalObject::Allocate()
{
	return new (DecimalType.tp_alloc(&DecimalType, 0)) MGA::DecimalObject();
}


int
MGA::ConvertDecimal(PyObject *object, MGA::DecimalObject **decimal)
{
	CL_Decimal value;
	if (PyObject_TypeCheck(object, &MGA::DecimalType)) {
		*decimal = (MGA::DecimalObject *)object;
		Py_INCREF(object);
		return 1;
	}
	else if (PyInt_Check(object)) {
		value = (int32)PyInt_AS_LONG(object);
	}
	else if (PyLong_Check(object)) {
#ifdef CL_DECIMAL_MPDEC
		PyObject *o = PyObject_Str(object);
		bool invalid;
		value = CL_Decimal::FromString(string(PyString_AS_STRING(o)), &invalid);
		Py_DECREF(o);
		if (invalid) {
			PyErr_SetString(PyExc_ValueError, "Invalid Decimal object");
			return 0;
		}
#else
		value = PyLong_AsLongLong(object) * CL_DECIMAL_UNIT;
#endif
	}
	else if (PyFloat_Check(object)) {
		value = PyFloat_AS_DOUBLE(object);
	}
	else if (PyNumber_Check(object)) {
		PyObject *number = PyNumber_Float(object);
		if (number) {
			value = PyFloat_AS_DOUBLE(number);
			Py_DECREF(number);
		}
		else
			return 0;
	}
	else if ((PyString_Check(object)) || (PyUnicode_Check(object))) {
		bool overflow;
		if ((!MGA_Decimal_from_string(value, object, &overflow)) || (overflow)) {
			PyErr_SetString(PyExc_ValueError, "Invalid Decimal object");
			return 0;
		}
	}
	*decimal = MGA::DecimalObject::Allocate();
	(*decimal)->fValue = value;
	return 1;
}

