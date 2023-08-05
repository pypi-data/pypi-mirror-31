# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, division

import abc
import re

import pyparsing as pp
import typepy

from ._common import _to_unicode
from ._interface import PingParserInterface
from ._logger import logger
from .error import EmptyPingStatisticsError, PingStatisticsHeaderNotFoundError


class PingParser(PingParserInterface):

    def __init__(self):
        self.ping_option = ""

        self.__initialize_parse_result()

    @property
    def destination(self):
        return self._destination

    @property
    def packet_transmit(self):
        return self._packet_transmit

    @property
    def packet_receive(self):
        return self._packet_receive

    @property
    def packet_loss_rate(self):
        try:
            return (1.0 - (self.packet_receive / self.packet_transmit)) * 100
        except (TypeError, ZeroDivisionError, OverflowError):
            return None

    @property
    def packet_loss_count(self):
        try:
            return self.packet_transmit - self.packet_receive
        except TypeError:
            return None

    @property
    def rtt_min(self):
        return self._rtt_min

    @property
    def rtt_avg(self):
        return self._rtt_avg

    @property
    def rtt_max(self):
        return self._rtt_max

    @property
    def rtt_mdev(self):
        return self._rtt_mdev

    @property
    def packet_duplicate_rate(self):
        try:
            return (self.packet_duplicate_count / self.packet_receive) * 100
        except (TypeError, ZeroDivisionError, OverflowError):
            return None

    @property
    def packet_duplicate_count(self):
        return self._duplicates

    @abc.abstractproperty
    def _parser_name(self):  # pragma: no cover
        pass

    @abc.abstractproperty
    def _stats_headline_pattern(self):  # pragma: no cover
        pass

    def _preprocess_parse(self, line_list):
        logger.debug(
            "parsing as {:s} ping result format".format(self._parser_name))

        self.__initialize_parse_result()

        headline_idx = self.__find_stats_headline_idx(
            line_list, re.compile(self._stats_headline_pattern))
        body_line_list = line_list[headline_idx + 1:]
        self.__validate_stats_body(body_line_list)

        packet_info_line = body_line_list[0]

        return (line_list[headline_idx], packet_info_line, body_line_list)

    def _parse_destination(self, headline):
        return headline.lstrip("--- ").rstrip(" ping statistics ---")

    def __find_stats_headline_idx(self, line_list, re_stats_header):
        for i, line in enumerate(line_list):
            if re_stats_header.search(line):
                break
        else:
            raise PingStatisticsHeaderNotFoundError(
                "ping statistics not found")

        return i

    def __validate_stats_body(self, body_line_list):
        if typepy.is_empty_sequence(body_line_list):
            raise EmptyPingStatisticsError("ping statistics is empty")

    def __initialize_parse_result(self):
        self._destination = None
        self._packet_transmit = None
        self._packet_receive = None
        self._rtt_min = None
        self._rtt_avg = None
        self._rtt_max = None
        self._rtt_mdev = None
        self._duplicates = None

    def _parse_duplicate(self, line):
        packet_pattern = (
            pp.SkipTo(pp.Word("+" + pp.nums) + pp.Literal("duplicates,")) +
            pp.Word("+" + pp.nums) +
            pp.Literal("duplicates,")
        )
        try:
            duplicate_parse_list = packet_pattern.parseString(_to_unicode(line))
        except pp.ParseException:
            return 0

        return int(duplicate_parse_list[-2].strip("+"))


class NullPingParser(PingParser):

    @property
    def _parser_name(self):
        return "null"

    @property
    def _stats_headline_pattern(self):
        return ""

    def parse(self, ping_message):  # pragma: no cover
        pass

    def _preprocess_parse(self, line_list):  # pragma: no cover
        pass


class LinuxPingParser(PingParser):

    @property
    def _parser_name(self):
        return "Linux"

    @property
    def _stats_headline_pattern(self):
        return "--- .* ping statistics ---"

    def parse(self, ping_message):
        headline, packet_info_line, body_line_list = self._preprocess_parse(
            line_list=ping_message)
        packet_pattern = (
            pp.Word(pp.nums) +
            pp.Literal("packets transmitted,") +
            pp.Word(pp.nums) +
            pp.Literal("received,")
        )

        self._destination = self._parse_destination(headline)

        parse_list = packet_pattern.parseString(_to_unicode(packet_info_line))
        self._packet_transmit = int(parse_list[0])
        self._packet_receive = int(parse_list[2])
        self._duplicates = self._parse_duplicate(packet_info_line)

        try:
            rtt_line = body_line_list[1]
        except IndexError:
            return

        if typepy.is_null_string(rtt_line):
            return

        rtt_pattern = (
            pp.Literal("rtt min/avg/max/mdev =") +
            pp.Word(pp.nums + ".") + "/" +
            pp.Word(pp.nums + ".") + "/" +
            pp.Word(pp.nums + ".") + "/" +
            pp.Word(pp.nums + ".") +
            pp.Word(pp.nums + "ms")
        )
        parse_list = rtt_pattern.parseString(_to_unicode(rtt_line))
        self._rtt_min = float(parse_list[1])
        self._rtt_avg = float(parse_list[3])
        self._rtt_max = float(parse_list[5])
        self._rtt_mdev = float(parse_list[7])


class WindowsPingParser(PingParser):

    @property
    def _parser_name(self):
        return "Windows"

    @property
    def _stats_headline_pattern(self):
        return "^Ping statistics for "

    def parse(self, ping_message):
        headline, packet_info_line, body_line_list = self._preprocess_parse(
            line_list=ping_message)
        packet_pattern = (
            pp.Literal("Packets: Sent = ") +
            pp.Word(pp.nums) +
            pp.Literal(", Received = ") +
            pp.Word(pp.nums)
        )

        self._destination = self._parse_destination(headline)

        parse_list = packet_pattern.parseString(_to_unicode(packet_info_line))
        self._packet_transmit = int(parse_list[1])
        self._packet_receive = int(parse_list[3])

        try:
            rtt_line = body_line_list[2].strip()
        except IndexError:
            return

        if typepy.is_null_string(rtt_line):
            return

        rtt_pattern = (
            pp.Literal("Minimum = ") +
            pp.Word(pp.nums) +
            pp.Literal("ms, Maximum = ") +
            pp.Word(pp.nums) +
            pp.Literal("ms, Average = ") +
            pp.Word(pp.nums)
        )
        parse_list = rtt_pattern.parseString(_to_unicode(rtt_line))
        self._rtt_min = float(parse_list[1])
        self._rtt_avg = float(parse_list[5])
        self._rtt_max = float(parse_list[3])

    def _parse_destination(self, headline):
        return headline.lstrip("Ping statistics for ").rstrip(":")


class MacOsPingParser(PingParser):

    @property
    def _parser_name(self):
        return "macOS"

    @property
    def _stats_headline_pattern(self):
        return "--- .* ping statistics ---"

    def parse(self, ping_message):
        headline, packet_info_line, body_line_list = self._preprocess_parse(
            line_list=ping_message)
        packet_pattern = (
            pp.Word(pp.nums) +
            pp.Literal("packets transmitted,") +
            pp.Word(pp.nums) +
            pp.Literal("packets received,")
        )

        self._destination = self._parse_destination(headline)

        parse_list = packet_pattern.parseString(_to_unicode(packet_info_line))
        self._packet_transmit = int(parse_list[0])
        self._packet_receive = int(parse_list[2])
        self._duplicates = self._parse_duplicate(packet_info_line)

        try:
            rtt_line = body_line_list[1]
        except IndexError:
            return

        if typepy.is_null_string(rtt_line):
            return

        rtt_pattern = (
            pp.Literal("round-trip min/avg/max/stddev =") +
            pp.Word(pp.nums + ".") + "/" +
            pp.Word(pp.nums + ".") + "/" +
            pp.Word(pp.nums + ".") + "/" +
            pp.Word(pp.nums + ".") +
            pp.Word(pp.nums + "ms")
        )
        parse_list = rtt_pattern.parseString(_to_unicode(rtt_line))
        self._rtt_min = float(parse_list[1])
        self._rtt_avg = float(parse_list[3])
        self._rtt_max = float(parse_list[5])
        self._rtt_mdev = float(parse_list[7])


class AlpineLinuxPingParser(LinuxPingParser):

    @property
    def _parser_name(self):
        return "AlpineLinux"

    def parse(self, ping_message):
        headline, packet_info_line, body_line_list = self._preprocess_parse(
            line_list=ping_message)
        packet_pattern = (
            pp.Word(pp.nums) +
            pp.Literal("packets transmitted,") +
            pp.Word(pp.nums) +
            pp.Literal("packets received,")
        )

        self._destination = self._parse_destination(headline)

        parse_list = packet_pattern.parseString(_to_unicode(packet_info_line))
        self._packet_transmit = int(parse_list[0])
        self._packet_receive = int(parse_list[2])
        self._duplicates = self._parse_duplicate(packet_info_line)

        try:
            rtt_line = body_line_list[1]
        except IndexError:
            return

        if typepy.is_null_string(rtt_line):
            return

        rtt_pattern = (
            pp.Literal("round-trip min/avg/max =") +
            pp.Word(pp.nums + ".") + "/" +
            pp.Word(pp.nums + ".") + "/" +
            pp.Word(pp.nums + ".") +
            pp.Word(pp.nums + "ms")
        )
        parse_list = rtt_pattern.parseString(_to_unicode(rtt_line))
        self._rtt_min = float(parse_list[1])
        self._rtt_avg = float(parse_list[3])
        self._rtt_max = float(parse_list[5])

    def _parse_duplicate(self, line):
        packet_pattern = (
            pp.SkipTo(pp.Word(pp.nums) + pp.Literal("duplicates,")) +
            pp.Word(pp.nums) +
            pp.Literal("duplicates,")
        )
        try:
            duplicate_parse_list = packet_pattern.parseString(
                _to_unicode(line))
        except pp.ParseException:
            return 0

        return int(duplicate_parse_list[-2])
