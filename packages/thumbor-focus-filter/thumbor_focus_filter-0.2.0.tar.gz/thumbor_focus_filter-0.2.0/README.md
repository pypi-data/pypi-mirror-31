Thumbor Focus Filter 
[![Build Status](https://travis-ci.org/sport1online/thumbor-focus-filter.svg?branch=master)](https://travis-ci.org/sport1online/thumbor-focus-filter)
===

This plugins provide a way to generate text via Thumbor Filter.

## Installation
`pip install thumbor-focus-filter`

## Configuration

By adding `FILTERS` in `thumbor.conf` with `thumbor-focus-filter`, for example:
```
FILTERS =     [
    # other filters....
    'thumbor_focus_filter',
]
```

## Usage
Add `focus()` to thumbor url at `filters` section, method signature is like this:

`focus(percentage_width,percentage_height)`

Here'are some examples:
```
http://thumbor/unsafe/filter:focus(49,32)/your-image-url
```
