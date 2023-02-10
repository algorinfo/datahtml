
#.PHONY: shell
#shell:
#	hatch shell

.PHONY: docs-serve
docs-serve:
	hatch run sphinx-autobuild docs docs/_build/html --port 9292 --watch ./

