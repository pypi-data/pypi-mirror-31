#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2018 The Regents of the University of California
#
# This file is part of kevlar (http://github.com/dib-lab/kevlar) and is
# licensed under the MIT license: see LICENSE.
# -----------------------------------------------------------------------------

from itertools import chain
import re
import sys
import kevlar
from kevlar.alignment import align_both_strands
from kevlar.cigar import AlignmentTokenizer
from kevlar.vcf import Variant, VariantSNV, VariantIndel
from kevlar.vcf import VariantFilter as vf


class VariantMapping(object):
    """Class for managing contig alignments to reference genome.

    All variant calls are made from alignments of contigs (assembled from reads
    containing novel sequence content) to a cutout of the reference genome.
    This class manages relevant data and implements the variant calling
    procedures.
    """
    def __init__(self, contig, cutout, score=None, cigar=None, strand=1,
                 match=1, mismatch=2, gapopen=5, gapextend=0):
        if score is None:
            score, cigar, strand = align_both_strands(
                cutout, contig, match, mismatch, gapopen, gapextend
            )
        self.contig = contig
        self.cutout = cutout
        self.score = score
        self.strand = strand
        self.matedist = None

        self.tok = AlignmentTokenizer(self.varseq, self.refrseq, cigar)
        self.cigar = self.tok._cigar

        self.vartype = None
        snvpattern = r'^((\d+)([DI]))?(\d+)M((\d+)[DI])?$'
        indelpattern = r'^((\d+)([DI]))?(\d+)M(\d+)([ID])(\d+)M((\d+)[DI])?$'
        if re.search(snvpattern, self.cigar):
            self.vartype = 'snv'
        elif re.search(indelpattern, self.cigar):
            self.vartype = 'indel'

    @property
    def interval(self):
        return self.cutout.interval

    @property
    def ikmers(self):
        for kmer in self.contig.ikmers:
            yield kmer.sequence
            yield kevlar.revcom(kmer.sequence)

    @property
    def varseq(self):
        assert self.strand in (-1, 1)
        if self.strand == 1:
            return self.contig.sequence
        else:
            return kevlar.revcom(self.contig.sequence)

    @property
    def refrseq(self):
        return self.cutout.sequence

    @property
    def seqid(self):
        return self.cutout._seqid

    @property
    def pos(self):
        return self.cutout._startpos

    @property
    def offset(self):
        if self.vartype is None:
            return None
        if self.tok.blocks[0].type == 'M':
            return 0
        return self.tok.blocks[0].length

    @property
    def targetshort(self):
        if self.vartype is None:
            return None
        return self.tok.blocks[0].type == 'I'

    @property
    def match(self):
        if self.vartype != 'snv':
            return None
        i = 0 if self.tok.blocks[0].type == 'M' else 1
        return self.tok.blocks[i]

    @property
    def leftflank(self):
        if self.vartype != 'indel':
            return None
        i = 0 if self.tok.blocks[0].type == 'M' else 1
        return self.tok.blocks[i]

    @property
    def indel(self):
        if self.vartype != 'indel':
            return None
        i = 1 if self.tok.blocks[0].type == 'M' else 2
        return self.tok.blocks[i]

    @property
    def indeltype(self):
        if self.vartype != 'indel':
            return None
        return self.indel.type

    @property
    def rightflank(self):
        if self.vartype != 'indel':
            return None
        i = -1 if self.tok.blocks[-1].type == 'M' else -2
        return self.tok.blocks[i]

    def is_passenger(self, call):
        if call.window is None:
            return False
        numikmers = sum([1 for k in self.ikmers if k in call.window])
        return numikmers == 0

    def call_variants(self, ksize, mindist=6, logstream=sys.stderr):
        """Attempt to call variants from this contig alignment.

        If the alignment CIGAR matches a known pattern, the appropriate caller
        is invoked (SNV or INDEL caller). If not, a "no call" is reported.

        If an SNV call is within `mindist` base pairs of the end of the
        alignment it is ignored. Set to `None` to disable this behavior.

        Variant calls with no spanning interesting k-mers are designated as
        "passenger calls" and discarded.
        """
        offset = 0 if self.targetshort else self.offset
        if self.vartype == 'snv':
            caller = self.call_snv(self.match.query, self.match.target, offset,
                                   ksize, mindist, logstream=logstream)
            for call in caller:
                if self.is_passenger(call):
                    call.filter(vf.PassengerVariant)
                yield call
        elif self.vartype == 'indel':
            indelcaller = self.call_indel(ksize)
            leftflankcaller = self.call_snv(
                self.leftflank.query, self.leftflank.target, offset, ksize,
                mindist, donocall=False
            )
            offset += self.leftflank.length
            if self.indeltype == 'D':
                offset += self.indel.length
            rightflankcaller = self.call_snv(
                self.rightflank.query, self.rightflank.target, offset, ksize,
                mindist, donocall=False
            )
            for call in chain(leftflankcaller, indelcaller, rightflankcaller):
                if self.is_passenger(call):
                    call.filter(vf.PassengerVariant)
                yield call
        else:
            nocall = Variant(
                self.seqid, self.pos, '.', '.', CONTIG=self.varseq,
                CIGAR=self.cigar, KSW2=str(self.score)
            )
            nocall.filter(vf.InscrutableCigar)
            yield nocall

    def call_snv(self, qseq, tseq, offset, ksize, mindist=6, donocall=True,
                 logstream=sys.stderr):
        """Call SNVs from the aligned mismatched sequences.

        The `qseq` and `tseq` are strings containing query and target sequences
        of identical length; `mismatches` is a list of positions where `qseq`
        and `tseq` do not match; `offset` is the number of 5' nucleotides in
        the target not aligned to the query; and `ksize` is used to compute a
        window that spans all reference allele k-mers in `tseq` and all
        alternate allele k-mers in `qseq`.
        """
        length = len(qseq)
        assert len(tseq) == length
        diffs = [i for i in range(length) if tseq[i] != qseq[i]]
        if mindist:
            diffs = trim_terminal_snvs(diffs, length, mindist, logstream)
        if len(diffs) == 0:
            if donocall:
                nocall = Variant(
                    self.seqid, self.cutout.local_to_global(offset), '.', '.',
                    CONTIG=qseq, CIGAR=self.cigar, KSW2=str(self.score),
                    IKMERS=len(self.contig.ikmers)
                )
                nocall.filter(vf.PerfectMatch)
                yield nocall
            return

        for pos in diffs:
            minpos = max(pos - ksize + 1, 0)
            maxpos = min(pos + ksize, length)
            altwindow = qseq[minpos:maxpos]
            refrwindow = tseq[minpos:maxpos]

            refr = tseq[pos].upper()
            alt = qseq[pos].upper()
            localcoord = pos + offset
            globalcoord = self.cutout.local_to_global(localcoord)
            nikmers = n_ikmers_present(self.contig.ikmers, altwindow)
            snv = VariantSNV(
                self.seqid, globalcoord, refr, alt, CONTIG=qseq,
                CIGAR=self.cigar, KSW2=str(self.score), IKMERS=str(nikmers),
                ALTWINDOW=altwindow, REFRWINDOW=refrwindow
            )
            yield snv

    def call_indel(self, ksize):
        if self.indeltype == 'D':
            refrwindow = self.leftflank.target[-(ksize-1):] \
                + self.indel.target \
                + self.rightflank.target[:(ksize-1)]
            refrallele = self.leftflank.target[-1] + self.indel.target
            altwindow = self.leftflank.query[-(ksize-1):] \
                + self.rightflank.query[:(ksize-1)]
            altallele = self.leftflank.query[-1]
        else:
            refrwindow = self.leftflank.target[-(ksize-1):] \
                + self.rightflank.target[:(ksize-1)]
            refrallele = self.leftflank.target[-1]
            altwindow = self.leftflank.query[-(ksize-1):] \
                + self.indel.query \
                + self.rightflank.query[:(ksize-1)]
            altallele = self.leftflank.query[-1] + self.indel.query
        nikmers = n_ikmers_present(self.contig.ikmers, altwindow)
        localcoord = 0 if self.targetshort else self.offset
        localcoord += self.leftflank.length
        globalcoord = self.cutout.local_to_global(localcoord)
        indel = VariantIndel(
            self.seqid, globalcoord - 1, refrallele, altallele,
            CONTIG=self.refrseq, CIGAR=self.cigar, KSW2=str(self.score),
            IKMERS=str(nikmers), ALTWINDOW=altwindow, REFRWINDOW=refrwindow
        )
        yield indel


def n_ikmers_present(ikmers, window):
    n = 0
    for ikmer in ikmers:
        if ikmer.sequence in window:
            n += 1
        elif kevlar.revcom(ikmer.sequence) in window:
            n += 1
    return n


def trim_terminal_snvs(mismatches, alnlength, mindist=5, logstream=sys.stderr):
    valid = list()
    for mm in mismatches:
        if mm < mindist or alnlength - mm < mindist:
            msg = 'discarding SNV due to proximity to end of the contig'
            print('[kevlar::call] NOTE:', msg, file=logstream)
        else:
            valid.append(mm)
    return valid
