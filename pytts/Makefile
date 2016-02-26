ci: clean test

test: test-pylint test-pytest-coverage

test-pylint:
	pylint --rcfile=pylint.rc tts

test-pytest:
	py.test --cache-clear --strict -c pytest.rc tts

test-pytest-coverage:
	py.test --cov=tts --cov-config=coverage.rc --cache-clear --strict -c pytest.rc tts

clean: clean-pycache clean-pyc_pyo clean-test_cache clean-coverage

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
