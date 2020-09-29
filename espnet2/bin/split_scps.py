#!/usr/bin/env python3
import argparse
from collections import Counter
from itertools import zip_longest
import logging
from pathlib import Path
import sys
from typing import List
from typing import Optional

from espnet.utils.cli_utils import get_commandline_args


def split_scps(
    scps: List[str],
    num_splits: int,
    names: Optional[List[str]],
    output_dir: str,
    log_level: str,
):
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s (%(module)s:%(lineno)d) %(levelname)s: %(message)s",
    )
    if num_splits < 2:
        raise RuntimeError(f"{num_splits} must be more than 1")

    if names is None:
        names = [Path(s).name for s in scps]
        if len(set(names)) != len(names):
            raise RuntimeError(f"names are duplicated: {names}")

    for name in names:
        (Path(output_dir) / name).mkdir(parents=True, exist_ok=True)

    scp_files = [open(s, "r", encoding="utf-8") for s in scps]
    
    
    
    # ===================== replace ============================
    for n in range(num_splits):
        for name in names:
            if (Path(output_dir) / name / f"split.{n}").exists():
                (Path(output_dir) / name / f"split.{n}").unlink()
                
    temp_line1=[]
    temp_line2=[]
    for i in range(num_splits):
        temp_line1.append([])
        temp_line2.append([])
                
    counter = Counter()
    linenum = -1
             
    for linenum, lines in enumerate(zip_longest(*scp_files)):
        if any(line is None for line in lines):
            raise RuntimeError("Number of lines are mismatched")

        prev_key = None
        for line in lines:
            key = line.rstrip().split(maxsplit=1)[0]
            if prev_key is not None and prev_key != key:
                raise RuntimeError("Not sorted or not having same keys")

        # Select a piece from split texts alternatively
        num = linenum % num_splits
        counter[num] += 1
        
        templine_num = 10000  #500000   #this is the maximum number of lines in temp_line, but be care of the problem (out of memory).
        
        for line, name in zip(lines, names):
            if name == names[0]:
                temp_line1[num].append(line)
            else:
                temp_line2[num].append(line)
            if len(temp_line1[num]) == len(temp_line2[num]) and len(temp_line2[-1])>=templine_num:
                for split_id in range(len(temp_line1)):
                    with (Path(output_dir)/names[0]/f"split.{split_id}").open("a", encoding="utf-8") as f:
                        for j in temp_line1[split_id]:
                            f.write(j)
                for split_id in range(len(temp_line2)):
                    with (Path(output_dir)/names[1]/f"split.{split_id}").open("a", encoding="utf-8") as f:
                        for j in temp_line2[split_id]:
                            f.write(j)
                for i in range(len(temp_line1)):
                    temp_line1[i]=[]
                for i in range(len(temp_line2)):
                    temp_line2[i]=[]
                    
    if temp_line1!=[]:
        for split_id in range(len(temp_line1)):
            with (Path(output_dir)/names[0]/f"split.{split_id}").open("a", encoding="utf-8") as f:
                for j in temp_line1[split_id]:
                    f.write(j)
        for split_id in range(len(temp_line2)):
            with (Path(output_dir)/names[1]/f"split.{split_id}").open("a", encoding="utf-8") as f:
                for j in temp_line2[split_id]:
                    f.write(j)
    
    del temp_line1
    del temp_line2
    
    '''
    # ====================== original code ======================
    # Remove existing files
    for n in range(num_splits):
        for name in names:
            if (Path(output_dir) / name / f"split.{n}").exists():
                (Path(output_dir) / name / f"split.{n}").unlink()

    counter = Counter()
    linenum = -1
    for linenum, lines in enumerate(zip_longest(*scp_files)):
        if any(line is None for line in lines):
            raise RuntimeError("Number of lines are mismatched")

        prev_key = None
        for line in lines:
            key = line.rstrip().split(maxsplit=1)[0]
            if prev_key is not None and prev_key != key:
                raise RuntimeError("Not sorted or not having same keys")

        # Select a piece from split texts alternatively
        num = linenum % num_splits
        counter[num] += 1
        # Write lines respectively
        for line, name in zip(lines, names):
            # To reduce the number of opened file descriptors, open now
            with (Path(output_dir) / name / f"split.{num}").open(
                "a", encoding="utf-8"
            ) as f:
                f.write(line)
    '''
    
    
    
    if linenum + 1 < num_splits:
        raise RuntimeError(
            f"The number of lines is less than num_splits: {linenum + 1} < {num_splits}"
        )

    for name in names:
        with (Path(output_dir) / name / "num_splits").open("w", encoding="utf-8") as f:
            f.write(str(num_splits))
    logging.info(f"N lines of split text: {set(counter.values())}")


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Split scp files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--log_level",
        type=lambda x: x.upper(),
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"),
        help="The verbose level of logging",
    )

    parser.add_argument("--scps", required=True, help="Input texts", nargs="+")
    parser.add_argument("--names", help="Output names for each files", nargs="+")
    parser.add_argument("--num_splits", help="Split number", type=int)
    parser.add_argument("--output_dir", required=True, help="Output directory")
    return parser


def main(cmd=None):
    print(get_commandline_args(), file=sys.stderr)
    parser = get_parser()
    args = parser.parse_args(cmd)
    kwargs = vars(args)
    split_scps(**kwargs)


if __name__ == "__main__":
    main()
