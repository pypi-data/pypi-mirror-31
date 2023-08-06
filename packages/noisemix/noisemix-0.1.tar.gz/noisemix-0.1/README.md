
##### Installing

For required packages, run:
```
pip install -r requirements.txt
```

##### Running
To generate the noisy data, call the program with the path to your fastText data file, for example:

```
  python test.py train.ft.txt
```
This will generate a data file with the added suffix `.nmx`.

##### Supported data formats

fastText (`__label__` prefix) is the only supported format for now.

##### Benchmarks

To test the effectiveness of NoiseMix, we compare it control data on several benchmarks.  Several benchmarks and toy datasets are included.  Read instructions and results in benchmarks/README.md
