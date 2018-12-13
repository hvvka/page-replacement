# page-replacement

[Original project – VMsim](https://github.com/adpoe/Page-Replacement-Simulator) by [Tony Poerio](mailto:tony@tonypoer.io).
  
Simulation and data analysis for 4 different page replacement algorithms.  


## Algorithms

* **Clock**.
   More efficient version of the second chance algorithm (FINUFO, First In Not Used First Out), 
   because the pages do not have to be constantly moved to the end of the list, 
   while they fulfill the same general function as the second chance.
   
* **LRU** – Least Recently Used.
   This algorithm assumes that pages that were most often used in the past will also be 
   the most commonly used in the future. While LRU provides in theory almost optimal performance, 
   it is expensive to implement.
   
* **OPT** – optimal. 
   Used as a baseline in the analysis, because it requires perfect future knowledge and 
   is therefore not possible to implement in a real system.
   Also known as the Bélády algorithm.
   
* **Aging** – approximate LRU.
   The aging algorithm derives from the NFU (Not Frequently Used) algorithm. 
   Each page in the page table has its own counter.


## Usage notes

Requires Python 3.

### [vmsim](vmsim.py)

Main program. 3 arguments can be passed:

- _--numframes_ – number of frames in RAM. **Required**

- _--refresh_ – refresh time [ms] for aging algorithm. _Optional_

- _--tracefile_ – path to the source file (should contain 32b addresses with memory access type). **Required**
 
E.g. run:

```bash
$ python vmsim.py --numframes 8 --refresh 6 --tracefile data/100000.trace
```

 
### [generator](generator.py)

Generates trace file. Parametrized with file size. E.g.:

```bash
$ python generator.py --pages 500000
```

Output directory is `data/`.


### [run](run.sh)


Bash script used for measurement.

The script is parameterized with two data arrays (traces & frames). 
It runs two scripts in Python – [generator](generator.py) and [vmsim](vmsim.py).

Firstly, 3 files with input data (trace files) are generated.
Then for each of the files all algorithms are executed for each frame length.

9 CSV files in `results/` are produced as a result.

Simply run:

```bash
$ ./run.sh
```


## Analysis

Tables and charts can be found [here](excel/output_analysis.xlsx).

There's also a wiki page.