# ukpocopy

A python package for UK Postal Code validation and formatting.

# Installation

Install using `pip`:

```
pip install -U ukpocopy
```


# How to use

## Validation

You can validate UK postal codes using an instance of `PostalCode`, like this:
```
import PostalCode from ukpocopy


postal_code = PostalCode("SW1W 0NY") # valid
postal_code.is_valid() # returns True

postal_code = PostalCode("0000 000") # invalid
postal_code.is_valid() # returns True
```

