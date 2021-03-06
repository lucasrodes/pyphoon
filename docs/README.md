The current version of the documentation can be visited at [http://lcsrg.me/pyphoon](http://lcsrg.me/pyphoon). 

## Editing the Documentation
As the project evolves, documentation files might be edited. You can edit the python modules from [pyphoon](../pyphoon) according to the docstring formatting. You can also edit the `.rst` files from [source](source). For both, please refer to the `.py` and `.rst` files to see examples on the format.

Once the documentation has beed edited, you can generate multiple formats.



**HTML**
```
$ make html
```

This generates the corresponding HTML files under `source/html`. To visualize
 it you can simply run an http server
 
```
$ cd docs/build/html
$ python -m http.server 8000
```

and visit [http://localhost:8000](http://localhost:8000).

**LaTeX**

LaTeX document is generated by typing:

```
$ make latex
```

Alternatively, you may want to run the following to directly generate a pdf file.

```
$ make latexpdf
$ open source/latex/pyphoon.pdf
```

---

#### Ignore this for now

Generate the `.rst` files corresponding to the different python files.

```
$ sphinx-apidoc -o source/ ../pyphoon
```

More [info](http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html#sphinx-apidoc-manual-page)
