import pysam
import numpy as np


class CoverageCalculator(object):

    def __init__(self, paired_end=False):
        self._coverages = {}
        self._paired_end = paired_end
        self.no_of_used_bases = 0

    def ref_seq_and_coverages(self, bam_path):
        bam = self._open_bam_file(bam_path)
        for ref_seq, length in zip(bam.references, bam.lengths):
            self._init_coverage_list(length)
            self._calc_coverage(ref_seq, bam)
            yield(ref_seq, self._coverages)

    def _init_coverage_list(self, length):
        for strand in ["forward", "reverse"]:
            self._coverages[strand] = np.zeros(length)

    def _calc_coverage(self, ref_seq, bam):
        if not self._paired_end:
            self._calc_coverage_single_end(ref_seq, bam)
        else:
            self._calc_coverage_paired_end(ref_seq, bam)
            
    def _calc_coverage_single_end(self, ref_seq, bam):
        """Please be aware of the difference between 'read' and
        'alignment'. Depending on the read mapper a single read can
        result in multiple alignments. We are NOT correcting here but
        simply use all alignments.
        """
        for alignment in bam.fetch(ref_seq):
            self._add_coverage_of_single_end_reads(alignment)
            
    def _add_coverage_of_single_end_reads(self, alignment):
        # Note: No translation from bam coordinates to python
        # list coordinates is needed.
        start = alignment.pos
        end = alignment.aend
        increment = 1
        # Some mappers like bowtie2 return read alignments that do not
        # have a start or end. Those are skipped during the coverage
        # calculation.
        if end is None or start is None:
            return
        self.no_of_used_bases += end - start
        self._add_whole_alignment_coverage(alignment, increment, start, end)

    def _calc_coverage_paired_end(self, ref_seq, bam):
        """Can handle single and paired end reads. In case of paired end
        reads the reads are treated as one fragment."""
        read_pairs_by_qname = {}
        for alignment in bam.fetch(ref_seq):
            if not alignment.is_proper_pair:
                self._add_coverage_of_single_end_reads(alignment)
            else:
                # some paired-end mapping have a third supplementary
                # read that should be discarded
                if alignment.is_supplementary:
                    continue
                # Collect all read pairs - this might be memory intensive!
                index = 0
                if alignment.is_read2:
                    index = 1

                read_pairs_by_qname.setdefault(
                    alignment.qname, [None, None])
                read_pairs_by_qname[alignment.qname][index] = alignment
        for pair in read_pairs_by_qname.values():
            # TO FIX - raises Segementation fault:
            # if None in pair:
            #    continue
            read_1, read_2 = pair
            try:
                start = min(read_1.pos, read_1.aend, read_2.pos, read_2.aend)
            except AttributeError:
                continue
            end = max(read_1.pos, read_1.aend, read_2.pos, read_2.aend)
            increment = 1
            self._add_whole_alignment_coverage(read_1, increment, start, end)
            self.no_of_used_bases += end - start

    def _open_bam_file(self, bam_file):
        return pysam.AlignmentFile(bam_file)

    def _close_bam_fh(self, bam_fh):
        bam_fh.close()

    def _add_whole_alignment_coverage(self, alignment, increment, start, end):
        if alignment.is_reverse is False:
            self._coverages["forward"][start:end] += increment
        else:
            self._coverages["reverse"][start:end] += increment
