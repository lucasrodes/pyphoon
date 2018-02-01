#### 1. Autmatic generation of sphinx sources

Generate the `.rst` files corresponding to the different python files.

```
$ sphinx-apidoc -o source/ ../pyphoon
```

More [info](http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html#sphinx-apidoc-manual-page)

#### 2. Generate documentation

Generate the `.rst` files corresponding to the different python files. 
There are multiple formats to save the documentation (e.g. latex, pdf, html)

**HTML**
```
$ make html
```

This generates the corresponding HTML files under `source/html`. To visualize
 it you can simply run an http server
 
```
$ python -m http.server 8000
```

and visit [http://localhost:8000](http://localhost:8000).

**LaTeX**
```
$ make latex
```

Generated files are stored at `source/latex`

**PDF**
```
$ make latexpdf
```

To visualize the generated file simply use:

```
$ open source/latex/pyphoon.pdf
```