CIBS = $(wildcard cib*.xml)
SVGS = $(CIBS:.xml=-start.svg) $(CIBS:.xml=-colocation.svg)

%-start.dot: %.xml
	python ../graph-constraints.py -S -o $@ $<

%-colocation.dot: %.xml ../graph-constraints.py
	python ../graph-constraints.py -nC -o $@ $<

%-start.svg: %-start.dot
	dot -Tsvg -o $@ $<
	sed -i 's/%3/$^/g' $@

%-colocation.svg: %-colocation.dot
	fdp -Tsvg -o $@ $<
	sed -i 's/%3/$^/g' $@

all: $(SVGS)

clean:
	rm -f $(SVGS)

