venv/bin/python:
	virtualenv --python=python3 venv
	venv/bin/pip install -r requirements.txt

run: venv/bin/python
	venv/bin/python app.py

test: venv/bin/python
	venv/bin/python app.py &
	sleep 1 # give app a second to startup
	venv/bin/python test_repository_service.py
	pkill python

clean:
	rm -rf venv
	rm -f *.pyc
	rm -rf __pycache__/
