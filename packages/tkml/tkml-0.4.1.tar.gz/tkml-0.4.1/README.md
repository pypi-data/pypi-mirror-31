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

There is a fixtures factory too:

```python
import tkml

# With no arguments, it assumes fixtures/ subdirectory neighbor to current script
loader = tkml.fixtures()
toplevel = loader('my-app.yaml')
```

### API

`tkml.load_fp()`:

- `fp: io.TextBase`: file pointer to YAML file
- `master: tkinter.Misc`: parent widget
- `use_tix: bool`: use or not `tix` – defaults to false
- `context`: context to `ctx[]`, `argparse.Namespace`,
  `collections.namedtuple`, or `dict`
- returns the toplevel widget

`tkml.fixtures()`:

- `origin: str`: the directory containing the YAML files, defaults to
  subdirectory `fixtures/` neighbor to the script calling the factory
- returns the loader function

Loader function returned by `tkml.fixtures()`:

- `fixture: str`: YAML file name under fixtures directory
- `master: tkinter.Misc`: parent widget
- `use_tix: bool`: use or not `tix` – defaults to false
- `context`: context to `ctx[]`, `argparse.Namespace`,
  `collections.namedtuple`, or `dict`
- returns the toplevel widget

## Resource example

```yaml
frame:
  children:
      - frame:
          children:
            - label:
                text: 'Word to search:'
                pack:
                  anchor: nw
                  side: left
                  expand: false
            - entry:
                pack:
                  anchor: ne
                  side: right
                  fill: x
                  expand: true
                bind:
                  <Return>: ctx[search]
                focus: null
          pack:
            anchor: n
            fill: x
            expand: true
      - button:
          text: Search
          command: ctx[search]
          pack:
            anchor: s
            expand: false
      - scrolled-text:
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
