FILES=domain transport

DB=$(patsubst %,%.db,$(FILES))

.PHONY: all clean reload

all: $(DB)
clean:
	rm -f $(FILES) $(DB)

reload: $(DB)
	postfix reload

$(DB) : %.db: %
	postmap $^

%: %.in ../settings_local.py
	sed "s/@RCPT_DOMAIN@/`./get-var.py ../settings_local.py RCPT_DOMAIN`/" $< > $@
