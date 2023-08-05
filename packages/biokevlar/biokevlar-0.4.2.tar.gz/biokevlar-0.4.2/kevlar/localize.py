#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2017 The Regents of the University of California
#
# This file is part of kevlar (http://github.com/dib-lab/kevlar) and is
# licensed under the MIT license: see LICENSE.
# -----------------------------------------------------------------------------

from collections import defaultdict
import os.path
import sys

import kevlar
from kevlar.reference import bwa_align, autoindex, ReferenceCutout
import khmer


class KevlarRefrSeqNotFoundError(ValueError):
    """Raised if the reference sequence cannot be found."""
    pass


class Localizer(object):
    def __init__(self, seedsize, delta=0):
        self._positions = defaultdict(list)
        self._seedsize = seedsize
        self._delta = delta

    def __len__(self):
        return len(self._positions)

    def add_seed_match(self, seqid, pos):
        self._positions[seqid].append(pos)

    def get_cutouts(self, refrseqs=None, clusterdist=1000):
        for seqid in sorted(self._positions):
            matchpos = sorted(self._positions[seqid])
            assert len(matchpos) > 0
            if refrseqs:
                if seqid not in refrseqs:
                    raise KevlarRefrSeqNotFoundError(seqid)

            def new_cutout(cluster):
                startpos = max(cluster[0] - self._delta, 0)
                endpos = cluster[-1] + self._seedsize + self._delta
                subseq = None
                if refrseqs:
                    endpos = min(endpos, len(refrseqs[seqid]))
                    subseq = refrseqs[seqid][startpos:endpos]
                defline = '{:s}_{:d}-{:d}'.format(seqid, startpos, endpos)
                return ReferenceCutout(defline, subseq)

            if not clusterdist:
                yield new_cutout(matchpos)
                continue

            cluster = list()
            prevpos = None
            for nextpos in matchpos:
                if prevpos:
                    dist = nextpos - prevpos
                    if dist > clusterdist:
                        yield new_cutout(cluster)
                        cluster = list()
                cluster.append(nextpos)
                prevpos = nextpos
            if len(cluster) > 0:
                yield new_cutout(cluster)


def get_unique_seeds(recordstream, seedsize):
    """Grab all unique seeds from the specified sequence file.

    Input is expected to be an iterable containing screed or khmer sequence
    records.
    """
    ct = khmer.Counttable(seedsize, 1, 1)
    kmers = set()
    for record in recordstream:
        for kmer in ct.get_kmers(record.sequence):
            minkmer = kevlar.revcommin(kmer)
            if minkmer not in kmers:
                kmers.add(minkmer)
                yield kmer


def unique_seed_string(records, seedsize):
    """Convert contigs to Fasta records of seed sequences for BWA input.

    Input is expected to be an iterable containing screed or khmer sequence
    records.
    """
    output = ''
    for n, kmer in enumerate(get_unique_seeds(records, seedsize)):
        output += '>kmer{:d}\n{:s}\n'.format(n, kmer)
    return output


def get_exact_matches(contigstream, bwaindexfile, seedsize=31):
    """Compute a list of exact seed matches using BWA MEM.

    Input should be an iterable containing contigs generated by
    `kevlar assemble`. This function decomposes the contigs into their
    constituent seeds and searches for exact matches in the reference using
    `bwa mem`. This function is a generator, and yields tuples of
    (seqid, startpos) for each exact match found.
    """
    kmers = unique_seed_string(contigstream, seedsize)
    cmd = 'bwa mem -k {k} -T {k} {idx} -'.format(k=seedsize, idx=bwaindexfile)
    cmdargs = cmd.split(' ')
    for seqid, pos in bwa_align(cmdargs, seqstring=kmers):
        yield seqid, pos


def localize(contigstream, refrfile, seedsize=31, delta=50, maxdiff=None,
             refrseqs=None, logstream=sys.stderr):
    """Wrap the `kevlar localize` task as a generator.

    Input is an iterable containing contigs (assembled by `kevlar assemble`)
    stored as khmer or screed sequence records, the filename of the reference
    genome sequence, and the desired seed size.
    """
    autoindex(refrfile, logstream)
    contigs = list(contigstream)
    localizer = Localizer(seedsize, delta)
    for seqid, pos in get_exact_matches(contigs, refrfile, seedsize):
        localizer.add_seed_match(seqid, pos)
    if len(localizer) == 0:
        message = 'WARNING: no reference matches'
        print('[kevlar::localize]', message, file=logstream)
        return
    if refrseqs:
        seqs = refrseqs
    else:
        refrstream = kevlar.open(refrfile, 'r')
        seqs = kevlar.seqio.parse_seq_dict(refrstream)
    if maxdiff is None:
        maxcontiglen = max([len(c.sequence) for c in contigs])
        maxdiff = maxcontiglen * 3
    for cutout in localizer.get_cutouts(refrseqs=seqs, clusterdist=maxdiff):
        yield cutout


def main(args):
    contigstream = kevlar.parse_augmented_fastx(kevlar.open(args.contigs, 'r'))
    outstream = kevlar.open(args.out, 'w')
    localizer = localize(
        contigstream, args.refr, seedsize=args.seed_size, delta=args.delta,
        maxdiff=args.max_diff, logstream=args.logfile
    )
    for cutout in localizer:
        record = khmer.Read(name=cutout.defline, sequence=cutout.sequence)
        khmer.utils.write_record(record, outstream)
