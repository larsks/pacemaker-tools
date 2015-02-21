CIBS = $(wildcard cib*.xml)
SVGS = $(CIBS:.xml=.svg)

%.dot: %.xml
	python cibparser.py < $^ > $@ || rm -f $@

%.svg: %.dot
	dot -Tsvg -o $@ $^
	sed -i 's/%3/$^/g' $@

all: $(SVGS)

clean:
	rm -f $(SVGS)

