DB= \
	domain.db \
	transport.db

all: $(DB)
	postfix reload

%.db: %
	postmap $^

