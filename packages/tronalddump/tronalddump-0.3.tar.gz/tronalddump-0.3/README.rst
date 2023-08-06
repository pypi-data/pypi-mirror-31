# tronalddump-python  

Python wrapper for the Tronalddump API: https://docs.tronalddump.io. Written and tested with Python 3.6.1.

### Setup
`pip3 install tronalddump`

### Example:
```python
from tronalddump import TronaldDump

td = TronaldDump()

# Get random quote
rq = td.randomquote()
print(rq.quote)
print(rq.quote_date)
print(rq.quote_tag)

# Get tags
tags = td.tags()
print(tags)

# Search for quotes
quotes_search = td.search("Obama")
for quote in quotes_search:
    print(quote.quote)
    print(quote.quote_date)
    print(quote.quote_tag)
```