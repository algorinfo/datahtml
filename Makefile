
#.PHONY: shell
#shell:
#	hatch shell

.PHONY: docs-serve
docss:
	hatch run sphinx-autobuild docs docs/_build/html --port 9292 --watch ./

