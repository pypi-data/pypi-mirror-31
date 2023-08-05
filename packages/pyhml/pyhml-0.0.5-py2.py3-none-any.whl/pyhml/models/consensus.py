# coding: utf-8

from __future__ import absolute_import
from pyhml.models.consensus_seq_block import ConsensusSeqBlock
from pyhml.models.ref_database import RefDatabase
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class Consensus(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, date: str=None, consensus_sequence_block: List[ConsensusSeqBlock]=None, reference_database: List[RefDatabase]=None):
        """
        Consensus - a model defined in Swagger

        :param date: The date of this Consensus.
        :type date: str
        :param consensus_sequence_block: The consensus_sequence_block of this Consensus.
        :type consensus_sequence_block: List[ConsensusSeqBlock]
        :param reference_database: The reference_database of this Consensus.
        :type reference_database: List[RefDatabase]
        """
        self.swagger_types = {
            'date': str,
            'consensus_sequence_block': List[ConsensusSeqBlock],
            'reference_database': List[RefDatabase]
        }

        self.attribute_map = {
            'date': 'date',
            'consensus_sequence_block': 'consensus_sequence_block',
            'reference_database': 'reference_database'
        }

        self._date = date
        self._consensus_sequence_block = consensus_sequence_block
        self._reference_database = reference_database

    @classmethod
    def from_dict(cls, dikt) -> 'Consensus':
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Consensus of this Consensus.
        :rtype: Consensus
        """
        return deserialize_model(dikt, cls)

    @property
    def date(self) -> str:
        """
        Gets the date of this Consensus.

        :return: The date of this Consensus.
        :rtype: str
        """
        return self._date

    @date.setter
    def date(self, date: str):
        """
        Sets the date of this Consensus.

        :param date: The date of this Consensus.
        :type date: str
        """

        self._date = date

    @property
    def consensus_sequence_block(self) -> List[ConsensusSeqBlock]:
        """
        Gets the consensus_sequence_block of this Consensus.

        :return: The consensus_sequence_block of this Consensus.
        :rtype: List[ConsensusSeqBlock]
        """
        return self._consensus_sequence_block

    @consensus_sequence_block.setter
    def consensus_sequence_block(self, consensus_sequence_block: List[ConsensusSeqBlock]):
        """
        Sets the consensus_sequence_block of this Consensus.

        :param consensus_sequence_block: The consensus_sequence_block of this Consensus.
        :type consensus_sequence_block: List[ConsensusSeqBlock]
        """

        self._consensus_sequence_block = consensus_sequence_block

    @property
    def reference_database(self) -> List[RefDatabase]:
        """
        Gets the reference_database of this Consensus.

        :return: The reference_database of this Consensus.
        :rtype: List[RefDatabase]
        """
        return self._reference_database

    @reference_database.setter
    def reference_database(self, reference_database: List[RefDatabase]):
        """
        Sets the reference_database of this Consensus.

        :param reference_database: The reference_database of this Consensus.
        :type reference_database: List[RefDatabase]
        """

        self._reference_database = reference_database

