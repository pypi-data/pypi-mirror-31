# TkML

Library to build [Tkinter](https://docs.python.org/3/library/tkinter.html)
structures from [YAML](http://yaml.org/) descriptions.

It requires [PyYAML 3.12](http://pyyaml.org/wiki/PyYAML).

## Use

```python
import tkml

...

with open(filename) as fp:
    toplevel = tkml.load_fp(fp)
```

## Resource example

```yaml
frame:
  frame:
    label:
      text: 'Word to search:'
      pack:
        anchor: nw
        side: left
        expand: false
    entry:
      pack:
        anchor: ne
        side: right
        fill: x
        expand: true
      bind:
        <Return>: ctx[search]
      call/focus: null
    pack:
      anchor: n
      fill: x
      expand: true
  button:
    text: Search
    command: ctx[search]
    pack:
      anchor: s
      expand: false
  scrolled-text:
    wrap: word
    pack:
      anchor: s
      fill: both
      expand: true

  pack:
    fill: both
    expand: true
```

## Copyright

This library is under
[3-Clause BSD License](https://opensource.org/licenses/BSD-3-Clause).

You can read the copying text
[here](https://bitbucket.org/cacilhas/tkml/src/master/LICENSE.txt).
