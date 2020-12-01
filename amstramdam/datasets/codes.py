import bidict

def read_codefile(filename):
    with open(filename) as f:
        codes = bidict.bidict()
        for line in f:
            name, code = line.rstrip().split("\t")
            codes[code] = name
    return codes

def read_region_file(filename, sep=";"):
    with open(filename) as f:
        codes = bidict.bidict()
        regions = dict()
        for line in f:
            code, name, *elements = line.rstrip().split(sep)
            codes[code] = name
            regions[code] = set(elements)
        return codes, regions




