# gc-content

gc-content is a command-line tool that calculates the GC content (the fraction amount of G and C bases) of each DNA sequence in a FASTA file. The output generated will be A CSV file with each name of the DNA sequences (ex. `myprimer_123`) in the FASTA input file along with its GC content in total percent(%).   

## Install (Python 3 on Ubuntu 16.04)

To install using pip: 

```bash
pip install gc-content
```

I have also included the entire repo as tar file if you'd prefer to install using `setup.py` instead.

```bash
tar -xvzf gc-content-0.1.tar.gz
cd gc-content-0.1/
python setup.py install
```

## Usage

Currently, the tool only accepts FASTA file types, so a FASTA file input is REQUIRED:

```bash
gc-content -i <input_file> -o <output_file>
```

where `input_file` is the file path of the FASTA file you would like to analyze. 

If a file path is not specified in the `output_file` argument, the output file will be created in the current working directory by default. If the file name already exists, the user will be prompted to enter a different name for the output file. 

In addition, you can import this package (`import gc_content`) for use in other scripts if desired.

## Options

```
--help -h           Show help message.
--input_file -i     File path of FASTA input file.
--output_file -o    File path of output CSV file.
```

