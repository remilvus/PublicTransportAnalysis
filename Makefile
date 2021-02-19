init:
	pip3 install -r requirements.txt
    
init_venv:
	( \
	  . ./.venv/bin/activate; \
	  which pip3; \
	  pip3 install -r requirements.txt; \
    	)
    
