"""This module contains the general information for MessageEp ManagedObject."""

from ...ucscmo import ManagedObject
from ...ucsccoremeta import UcscVersion, MoPropertyMeta, MoMeta
from ...ucscmeta import VersionMeta


class MessageEpConsts():
    pass


class MessageEp(ManagedObject):
    """This is MessageEp class."""

    consts = MessageEpConsts()
    naming_props = set([])

    mo_meta = MoMeta("MessageEp", "messageEp", "ep", VersionMeta.Version151a, "InputOutput", 0xf, [], ["read-only"], [u'domainProfile', u'equipmentCPMeta', u'fabricDceSwSrvPcOperation', u'fabricEthEstcEpOperation', u'fabricEthEstcPcOperation', u'fabricEthLanEpOperation', u'fabricEthLanPcOperation', u'fabricEthMonOperation', u'fabricFcEstcEpOperation', u'fabricFcMonOperation', u'fabricFcSanEpOperation', u'fabricFcSanPcOperation', u'fabricFcUserZone', u'fabricFcoeEstcEpOperation', u'fabricFcoeSanEpOperation', u'fabricFcoeSanPcOperation', u'fdBlade', u'fdChassis', u'fdRackUnit', u'glBlockOp', u'glIdentCtxOp', u'glIdentCtxResOp', u'glMcastPolicy', u'glPolicy', u'glPolicyAlgorithmedOp', u'glPolicyOp', u'glPolicyResOp', u'glPool', u'glPoolOp', u'glRequest', u'glServerPoolResOp', u'glServiceProfile', u'glTemplateOp', u'glTemplateResOp', u'glVlan', u'glVsan', u'glVxanOp', u'glVxanResOp', u'lsSPMeta', u'vnicOutbandMgmtEp'], [u'messageEntry'], [None])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version151a, MoPropertyMeta.INTERNAL, None, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version151a, MoPropertyMeta.READ_ONLY, 0x2, 0, 256, None, [], []), 
        "index": MoPropertyMeta("index", "index", "uint", VersionMeta.Version151a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version151a, MoPropertyMeta.READ_ONLY, 0x4, 0, 256, None, [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version151a, MoPropertyMeta.READ_WRITE, 0x8, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "dn": "dn", 
        "index": "index", 
        "rn": "rn", 
        "status": "status", 
    }

    def __init__(self, parent_mo_or_dn, **kwargs):
        self._dirty_mask = 0
        self.child_action = None
        self.index = None
        self.status = None

        ManagedObject.__init__(self, "MessageEp", parent_mo_or_dn, **kwargs)

