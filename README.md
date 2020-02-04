# Tinybeans API Wrapper (unofficial)
This library will allow you to interact with [Tinybeans](https://tinybeans.com/).

## Installation
`pip install pytinybeans`

## Examples
```python3
In [1]: from pytinybeans import PyTinybeans

In [2]: tb = PyTinybeans()

In [3]: tb.login('<username>', '<password>')

In [4]: print(tb.children)
[<Jane Doe 2019-10-16 00:00:00>]

In [5]: entry = tb.get_entries(tb.children[0])[0]

In [6]: entry.blobs
Out[6]:
{'o': 'https://tinybeans.com/pv/e/<url>/<url>.jpg',
 'p': 'https://tinybeans.com/pv/e/<url>/<url>.jpg'}

In [7]: entry.comments[0].text
Out[7]: 'Ok, I got this!'

```

## Notes

This isn't a wonderful example of API design, and there's some weirdness like using `.format()` in some places vs old style string replacement in others. In my defense, I was extremely sleep deprived, but it's functional :)
