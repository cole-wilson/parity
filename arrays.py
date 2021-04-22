from typing import List, Tuple, Union, Callable


class Array:
	"""
	The basic Array class for all objects in the Parity programming language.
		- All Arrays are mutable, and they are also of infinite length.
		- Undefined indices evaluate to Array(0).
		- Items in Arrays are also Arrays.
	"""
	items: list = []

	def append(self, item):
		item = ensureArray(item)
		if len(item) == 1:
			item = item[0]
		self.items.append(item)

	def delete(self, item):
		item = ensureArray(item)
		try:
			del self.items[item]
		except IndexError:
			pass
		return self

	def insert(self, index, item):
		self[index - 1] = 0
		self.items.insert(index, item)

	def __init__(self, *items):
		"""
		Constructor for the Array class
		*args is expanded to make the items of the list.
		Iterables are preserved, but singletons are expanded:
			- Array(1, 2, 3) -> [1, 2, 3]
			- Array(1, 2, [3]) -> [1, 2, 3]
			- Array(1, 2, [3, 4]) -> [1, 2, [3, 4]]
		"""
		try:
			if isinstance(items[0], str):
				self.items = list(map(ord, items[0]))
				return
		except IndexError:
			return
		self.items = list(items)
		return

	def __call__(self, *args, **kwargs):
		return self

	def __repr__(self):
		"""Representation of an Array is the list expansion of its items."""
		items = self.items
		return f"[{', '.join(map(str, items))}]"

	def __setitem__(self, k, v):
		if int(k) >= len(self.items):
			for i in range(len(self.items), k + 1):
				self.items.append(0)
		self.items[k] = v

	def __getitem__(self, item):
		if isinstance(item, slice):
			return self.items[item]
		elif int(item) >= len(self.items):
			return 0
		else:
			return self.items[item]

	def __len__(self):
		return len(self.items)

	def __int__(self):
		return self.items[0]

	def __iter__(self):
		return iter(map(Array, self.items))

	def __bool__(self):
		return bool(self[0])

	def __contains__(self, item):
		if ensureArray(item) == Array(0):
			return True
		else:
			return item[0] in self.items

	def __add__(self, other):
		return array_math(self, other, lambda a, b: a + b)

	def __sub__(self, other):
		return array_math(self, other, lambda a, b: a - b)

	def __mul__(self, other):
		return array_math(self, other, lambda a, b: a * b)

	def __truediv__(self, other):
		return array_math(self, other, lambda a, b: a / b)

	def __floordiv__(self, other):
		return array_math(self, other, lambda a, b: a // b)

	def __pow__(self, power):
		return array_math(self, power, lambda a, b: a ** b)

	def __mod__(self, other):
		return array_math(self, other, lambda a, b: a % b)

	def __matmul__(self, other):
		print('What are you doing???')
		return Array()

	def __eq__(self, other):
		return self.items == other.items

	def __gt__(self, other):
		return array_math(self, other, lambda a, b: a > b)

	def __lt__(self, other):
		return array_math(self, other, lambda a, b: a < b)

	def __ge__(self, other):
		return array_math(self, other, lambda a, b: a >= b)

	def __le__(self, other):
		return array_math(self, other, lambda a, b: a <= b)

	def __hash__(self):
		return hash(self.items)

	__index__ = __int__



ArrayLike = Union[list, int, float]


def ensureArray(a: ArrayLike) -> Array:
	"""Coerces parameter `a` into an Array"""
	if isinstance(a, list):
		a = Array(*a)
	elif not isinstance(a, Array):
		a = Array(a)
	return a


def array_math(a: Union[ArrayLike, Array], b: Union[ArrayLike, Array], func: Callable):
	a, b = ensureArray(a), ensureArray(b)
	if len(a) == len(b):
		return Array(*map(lambda i: func(i[0][0], i[1][0]), zip(a, b)))
	elif len(a) == 1:
		return Array(*map(lambda i: func(a[0], i[0]), b))
	else:
		return Array(*map(lambda i: func(i[0], b[0]), a))


def expandarray(array):
	def __expandhelper(i):
		i = ensureArray(i)
		out = []
		for part in map(lambda a: a[0], i()):
			if type(part) in (int, float):
				out.append(part)
			else:
				out.extend(__expandhelper(part))
		return out
	return Array(*__expandhelper(array))
