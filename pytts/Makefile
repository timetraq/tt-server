ci: clean test

test: test-pylint test-smoke test-pytest

test-pylint:
	pylint --rcfile=pylint.rc tts

test-pylint_html:
	pylint --rcfile=pylint.rc -f html tts > pylint-report.html

test-smoke:
	py.test -c pytest-smoke.rc

test-pytest:
	py.test -c pytest.rc

clean: clean-pycache clean-pyc_pyo clean-test_cache clean-coverage clean-pylint_report

clean-pycache:
	find -path '*/__pycache__/*' -not -path '*/virtualenv/*' -delete
	find -name '__pycache__' -not -path '*/virtualenv/*' -type d -delete

clean-pyc_pyo:
	find -name '*.pyc' -not -path '*/virtualenv/*' -delete
	find -name '*.pyo' -not -path '*/virtualenv/*' -delete

clean-test_cache:
	find -path '*/.cache/*' -not -path '*/virtualenv/*' -delete
	find -name '.cache' -not -path '*/virtualenv/*' -type d -delete

clean-coverage:
	find -name '.coverage' -not -path '*/virtualenv/*' -delete

clean-pylint_report:
	rm -rf pylint-report.html
