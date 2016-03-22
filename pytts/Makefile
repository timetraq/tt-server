.PHONY: ci
ci: clean test

.PHONY: generate-standalone-test-script
generate-standalone-test-script: clean-standalone-test-script
	py.test -c pytest.rc --genscript=testrunner.py

.PHONY: test-coverage
test-coverage: generate-standalone-test-script
	coverage run --rcfile=coverage.rc testrunner.py
	rm -rf testrunner.py

.PHONY: test
test: test-pylint test-smoke test-pytest

.PHONY: test-pylint
test-pylint:
	pylint --rcfile=pylint.rc tts

.PHONY: test-pylint_html
test-pylint_html:
	pylint --rcfile=pylint.rc -f html tts > pylint-report.html

.PHONY: test-pylint_multithread
test-pylint_multithread:
	pylint --rcfile=pylint.rc -j 4 tts

.PHONY: test-smoke
test-smoke:
	py.test -c pytest-smoke.rc

.PHONY: test-pytest
test-pytest:
	py.test -c pytest.rc

.PHONY: clean
clean: clean-standalone-test-script clean-pycache clean-pyc_pyo clean-test_cache clean-coverage clean-pylint_report

.PHONY: clean-standalone-test-script
clean-standalone-test-script:
	rm -rf testrunner.py

.PHONY: clean-pycache
clean-pycache:
	find -path '*/__pycache__/*' -not -path '*/virtualenv/*' -delete
	find -name '__pycache__' -not -path '*/virtualenv/*' -type d -delete

.PHONY: clean-pyc_pyo
clean-pyc_pyo:
	find -name '*.pyc' -not -path '*/virtualenv/*' -delete
	find -name '*.pyo' -not -path '*/virtualenv/*' -delete

.PHONY: clean-test_cache
clean-test_cache:
	find -path '*/.cache/*' -not -path '*/virtualenv/*' -delete
	find -name '.cache' -not -path '*/virtualenv/*' -type d -delete

.PHONY: clean-coverage
clean-coverage:
	find -name '.coverage' -not -path '*/virtualenv/*' -delete

.PHONY: clean-pylint_report
clean-pylint_report:
	rm -rf pylint-report.html
