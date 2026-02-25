.PHONY: test build clean

test: build
	@./bin/skill-validate .

build:
	@mkdir -p bin
	go build -o bin/skill-validate ./cmd/skill-validate

clean:
	rm -rf bin
