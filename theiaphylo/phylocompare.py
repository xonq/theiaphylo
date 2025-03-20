#! /usr/bin/env python3

import sys
import logging
import argparse
from TheiaPhylo import *
from StdPath import Path


def compare_trees(tree1, tree2, mc=True, rf=True, lrm=True, rooted=True):
    """Quantify tree distances between two phylogenetic trees"""
    mc_dist, rf_dist, lrm_dist = None, None, None
    if rooted:
        # compare rooted trees
        if rf:
            # calculate the Robinson-Foulds distance
            rf_dist = tree1.tree_distance(tree2, method="rooted_robinson_foulds")
        if mc:
            # calculate the matching cluster distance
            mc_dist = tree1.tree_distance(tree2, method="matching_cluster")
    else:
        # compare unrooted trees
        if lrm:
            # calculate the least lin rajan moret distance
            lrm_dist = tree1.tree_distance(tree2, method="lin_rajan_moret")
        if rf:
            # calculate the Robinson-Foulds distance
            rf_dist = tree1.tree_distance(tree2, method="unrooted_robinson_foulds")
    return mc_dist, rf_dist, lrm_dist


def output_results(res_path, tree_res):
    """Output the results of the tree comparison"""
    with open(res_path, "w") as res_file:
        res_file.write(
            "#robinson_foulds_distance\tmatching_cluster_distance\tlin-rajan-moret_distance\n"
        )
        res_file.write(f"{tree_res[0]}\t{tree_res[1]}\t{tree_res[2]}\n")


def main(args, output_file="phylocompare_results.txt"):
    """Main function"""
    outgroup = []
    if args.outgroup and args.midpoint:
        raise ValueError(
            "cannot root trees at midpoint and with outgroup simultaneously"
        )
    elif args.outgroup or args.midpoint:
        if args.unrooted:
            raise ValueError("unrooted and rooting options simultaneously specified")
        rooted = True
        if args.outgroup:
            outgroup = args.outgroup.split(",")
            # CURRENTLY NOT FUNCTIONAL WITH MULTIPLE OUTGROUPS
            if len(outgroup) > 1:
                raise RootError("multiple outgroups not supported")
    elif not args.unrooted:
        # CURRENTLY NOT FUNCTIONAL WITHOUT EXPLICIT ROOT
        raise ValueError("no rooting method provided")
    else:
        rooted = False

    # import the trees
    tree1 = import_tree(Path(args.tree1), outgroup=outgroup, midpoint=args.midpoint)
    tree2 = import_tree(Path(args.tree2), outgroup=outgroup, midpoint=args.midpoint)

    # compare the trees
    tree_res = compare_trees(
        tree1,
        tree2,
        rooted=rooted,
        mc=args.matching_cluster,
        rf=args.robinson_foulds,
        lrm=args.lin_rajan_moret,
    )

    # output the results
    output_results(output_file, tree_res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare phylogenetic trees by distance metrics: "
        + "Robinson-Foulds, Matching Cluster, and Lin-Rajan-Moret"
    )
    in_args = parser.add_argument_group("Inputs")
    in_args.add_argument("tree1", help="First tree file")
    in_args.add_argument("tree2", help="Second tree file")

    phy_args = parser.add_argument_group("Phylogenetics Options")
    phy_args.add_argument(
        "-o",
        "--outgroup",
        help="Comma-delimited list of outgroup tips to root on their most" \
            +"recent common ancestor",
    )
    phy_args.add_argument(
        "-m", "--midpoint", action="store_true", help="Root trees at midpoint"
    )
    phy_args.add_argument(
        "-u", "--unrooted", action="store_true", help="Compare unrooted trees"
    )
    phy_args.add_argument(
        "-mc",
        "--matching_cluster",
        action="store_true",
        help="Calculate matching cluster distance (rooted only); overwrites default: ALL",
    )
    phy_args.add_argument(
        "-rf",
        "--robinson_foulds",
        action="store_true",
        help="Calculate Robinson-Foulds distance; overwrites default: ALL",
    )
    phy_args.add_argument(
        "-lrm",
        "--lin_rajan_moret",
        action="store_true",
        help="Calculate Lin-Rajan-Moret distance; overwrites default: ALL",
    )

    run_args = parser.add_argument_group("Run Options")
    run_args.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug mode"
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
        )
    else:
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
    logger = logging.getLogger(__name__)

    # run all comparisons by default
    if (
        not args.matching_cluster
        and not args.robinson_foulds
        and not args.lin_rajan_moret
    ):
        args.matching_cluster = True
        args.robinson_foulds = True
        args.lin_rajan_moret = True

    main(args)
    sys.exit(0)