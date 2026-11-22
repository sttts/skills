.PHONY: test build clean

test: build
	@./bin/skill-validate .

build:
	@mkdir -p bin
	go build -o bin/skill-validate ./cmd/skill-validate

clean:
	rm -rf bin

visualize_skills := plugins/visualize/skills

.PHONY: package-visualize-poster
package-visualize-poster:
	@mkdir -p bin
	@set -eu; \
	stage=$$(mktemp -d); trap 'rm -rf "$$stage"' EXIT; \
	poster="$$stage/visualize-poster"; \
	cp -R $(visualize_skills)/visualize-poster "$$poster"; \
	mkdir -p "$$poster/references"; \
	cp $(visualize_skills)/visualize-slide/SKILL.md "$$poster/references/slide-guide.md"; \
	cp -R $(visualize_skills)/visualize-slide/assets "$$poster/references/assets"; \
	sed -e 's|\.\./visualize-slide/SKILL.md|references/slide-guide.md|g' \
	    -e 's|\.\./visualize-slide/assets/|references/assets/|g' \
	    $(visualize_skills)/visualize-poster/SKILL.md > "$$poster/SKILL.md"; \
	tar -czf "$$stage/visualize-poster.tar.gz" -C "$$stage" visualize-poster; \
	mv "$$stage/visualize-poster.tar.gz" bin/
