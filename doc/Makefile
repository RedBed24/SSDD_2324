SRC_DIR := src/
BUILD_DIR := build/

STATIC :=
DIAGRAMS := interfaces.svg uso_interfaces.svg apuntes_sobre_interfaces.svg


all: dirs styles $(DIAGRAMS) index.html

dirs:
	mkdir -p $(BUILD_DIR)

styles: styles.html
	mkdir -p ~/.local/share/pandoc/templates/
	cp $^ ~/.local/share/pandoc/templates/

static: $(STATIC)
	cp $^ $(BUILD_DIR)

plantuml:
	wget https://github.com/plantuml/plantuml/releases/download/v1.2023.13/plantuml-lgpl-1.2023.13.jar
	mv plantuml-lgpl-1.2023.13.jar plantuml.jar

pandoc:
	wget https://github.com/jgm/pandoc/releases/download/3.1.11.1/pandoc-3.1.11.1-linux-amd64.tar.gz
	tar -xvf pandoc-3.1.11.1-linux-amd64.tar.gz
	mv pandoc-3.1.11.1/bin/pandoc .
	rm pandoc-3.1.11.1-linux-amd64.tar.gz
	rm -rf pandoc-3.1.11.1/

%.html: $(SRC_DIR)%.md
	./pandoc $^ -o $(BUILD_DIR)$@ --mathjax -s

%.svg: $(SRC_DIR)%.puml
	java -jar plantuml.jar -tsvg $^ -o ../$(BUILD_DIR)

clean:
	rm -rf *~ $(BUILD_DIR) $(SRC_DIR)*~ pandoc

