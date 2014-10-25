# File: D (Python 2.4)

from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedElevatorExtAI import DistributedElevatorExtAI

class DistributedCogdoElevatorExtAI(DistributedElevatorExtAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCogdoElevatorExtAI')
    
    def _createInterior(self):
        self.bldg.createCogdoInterior()


