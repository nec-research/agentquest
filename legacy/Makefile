# List all folders in benchmarks directory
BENCHMARK_FOLDERS := $(wildcard benchmarks/*)

# Extract only folder names
BENCHMARK_NAMES := $(notdir $(BENCHMARK_FOLDERS))

# Define the install target
install:
	@echo "Please specify a benchmark to install (e.g., make install mastermind)"

install-%:
	@echo "Installing benchmark: $*"
	cd benchmarks/$* && ./setup.sh

init-%:
	@echo "Setting up benchmark: $*"
	python3 .templates/customize.py $*
	mkdir agentquest/drivers/$*
	mv .templates/$*_driver.py agentquest/drivers/$*/
	mv .templates/__init__.py agentquest/drivers/$*/
	mkdir benchmarks/$*
	touch benchmarks/$*/setup.sh
	touch benchmarks/$*/requirements.txt
	mv .templates/README.md benchmarks/$*/
	mkdir agentquest/data/$*

clean-%:
	@echo "Removing benchmark: $*"
	rm -rf agentquest/drivers/$*
	rm -rf benchmarks/$*
	rm -rf agentquest/data/$*

# Define the rule to install benchmarks
installall: $(BENCHMARK_NAMES)

# Rule to install each benchmark folder
$(BENCHMARK_NAMES):
	make install-$@
