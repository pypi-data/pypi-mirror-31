from .instance import BlockchainInstance
from .account import Account
from .exceptions import ProposalDoesNotExistException
from .blockchainobject import BlockchainObject
import logging
log = logging.getLogger(__name__)


class Proposal(BlockchainObject):
    """ Read data about a Proposal Balance in the chain

        :param str id: Id of the proposal
        :param peerplays blockchain_instance: Peerplays() instance to use when accesing a RPC

    """
    type_id = 10

    def refresh(self):
        proposal = self.blockchain.rpc.get_objects([self.identifier])
        if not any(proposal):
            raise ProposalDoesNotExistException
        super(Proposal, self).__init__(proposal[0])

    @property
    def proposed_operations(self):
        yield from self["proposed_transaction"]["operations"]

    @property
    def proposer(self):
        """ Return the proposer of the proposal if available in the backend,
            else returns None
        """
        if "proposer" in self:
            return self["proposer"]


class Proposals(list):
    """ Obtain a list of pending proposals for an account

        :param str account: Account name
        :param peerplays blockchain_instance: PeerPlays() instance to use when accesing a RPC
    """
    def __init__(self, account, **kwargs):
        BlockchainInstance.__init__(self, **kwargs)

        account = Account(account)
        proposals = self.blockchain.rpc.get_proposed_transactions(account["id"])

        super(Proposals, self).__init__(
            [
                Proposal(x, blockchain_instance=self.blockchain)
                for x in proposals
            ]
        )
