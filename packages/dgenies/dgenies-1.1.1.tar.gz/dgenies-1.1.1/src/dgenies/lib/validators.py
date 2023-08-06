"""
Define formats validators here (for alignment files)

Each validator (main function) has a name which is exactly the name of the format in the aln-formats.yaml file.
Only 1 argument to this function:
- Input file to check

Secondary functions must start with _

Returns True if file is valid, else False
"""

from Bio import AlignIO
import shutil, os


def paf(in_file):
    try:
        with open(in_file, "r") as aln:
            n = 0
            for line in aln:
                parts = line.rstrip().split("\t")
                if len(parts) < 12:
                    return False
                for i in (1, 2, 3, 6, 7, 8, 9, 10, 11):
                    if not parts[i].isdigit():
                        return False
                if parts[4] not in ("+", "-"):
                    return False
                n += 1
                if n == 1000:
                    break
    except:
        return False
    else:
        return  True


def _filter_maf(in_file):
    new_file = in_file + ".new"
    with open(in_file, "r") as inf, open(new_file, "w") as new:
        for line in inf:
            if len(line.rstrip()) == 0 or line[0] in ["#", "a", "s"]:
                new.write(line)
    os.remove(in_file)
    shutil.move(new_file, in_file)


def maf(in_file):
    _filter_maf(in_file)
    try:
        maf = AlignIO.parse(in_file, "maf")
        for grp in maf:
            if len(grp) != 2:
                return False
    except:
        return False
    else:
        return True


def idx(in_file):
    try:
        with open(in_file, "r") as inf:
            first_line = inf.readline()
            if "\t" in first_line:
                return False
            must_be_last = False
            for line in inf:
                if must_be_last:
                    return False
                line = line.rstrip()
                if line == "":
                    must_be_last = True
                else:
                    cols = line.split("\t")
                    if len(cols) != 2:
                        return False
                    if not cols[1].isdigit():
                        return False
    except:
        return False
    else:
        return True
