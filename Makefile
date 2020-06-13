all : main.py.png \
    boundary.py.png

%.py.png : %.py
	python ./main.py
