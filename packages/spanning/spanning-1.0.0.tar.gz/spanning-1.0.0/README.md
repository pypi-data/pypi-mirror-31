# Python Span
A simple library providing `Span` and `ReadOnlySpan` classes. The idea of these are very similar to [C#'s Span<T>](https://github.com/dotnet/corefxlab/blob/master/docs/specs/span.md), however they are a pure-Python implementation of it. The start and end points are handled via Python's `slice` object, meaning negative ends and starts work as expected, and step works is it does for sliced lists.

The classes provide read/write and read-only access to certain sections of list-like object, without having to reallocate them via normal slicing. Any object that can be indexed and has a length can be used, meaning you can even create `ReadOnlySpan`s over strings (useful in processing large strings that could have been read from a file).

These classes are useful when looking at certain regions of a list that is very long (upwards of 100,000s of items). Using the classes looks like this:

```python
import math

data = get_data() # returns a very large list

# we only want the first half of the list
end = int(math.ceil(len(data) / 2))

# without span
first_half = data[:end] # copies the entire first half

# with span
first_half = Span(data, 0, end)
# no copies, just a reference is stored, acts like a list of half the length
```

In the above example, if the list was very long (e.g. 1,000,000 items), then the first example would copy the entire second half of the list into the new variable, whereas the second example just stores the reference, and the start & end points that you requested. The new Span object would then act exactly like a list of half the length (e.g. `len` would return a length of 500,000 for the example before.). The only allocations that are done are for the Span objects themselves, and the object stores very little data inside (just the start, end, and step values, and the object reference), meaning that it will have little impact on memory by itself.
