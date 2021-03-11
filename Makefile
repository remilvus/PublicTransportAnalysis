init:
	( \
	  python3 -m venv .venv; \
	  . ./.venv/bin/activate; \
	  which pip3; \
	  pip3 install -r requirements.txt; \
	  pip3 install -e .; \
    	)
    
    
jupyter:
	( \
	  . ./.venv/bin/activate; \
	  python3 -m jupyter notebook; \
    	)
