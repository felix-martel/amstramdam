import bidict
import warnings

def read_codefile(filename):
    warnings.warn("You're using the deprecated function `read_codefile` (from `ams.datasets.codes`)."
                  "Please use `read_code` instead.", DeprecationWarning)
    with open(filename) as f:
        codes = bidict.bidict()
        for line in f:
            name, code = line.rstrip().split("\t")
            codes[code] = name
    return codes

def read_code(filename, sep="\t", comment="#", errors="ignore"):
    bidirectional_codes = bidict.bidict()
    with open(filename, "r", encoding="utf8") as f:
        for i, line in enumerate(f):
            if line.startswith(comment):
                continue
            try:
                name, code = line.rstrip().split(sep)
                bidirectional_codes[code] = name
            except ValueError as e:
                print(f"Error on line {i}: {line.rstrip()}")
                if errors == "strict":
                    raise e
                continue
    return bidirectional_codes

def read_region_file(filename, sep=";"):
    with open(filename) as f:
        codes = bidict.bidict()
        regions = dict()
        for line in f:
            code, name, *elements = line.rstrip().split(sep)
            codes[code] = name
            regions[code] = set(elements)
        return codes, regions




