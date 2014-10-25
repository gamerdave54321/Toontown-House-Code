# File: D (Python 2.4)

from otp.ai.AIBaseGlobal import *
from direct.distributed import DistributedObjectAI
import SuitPlannerBase
import DistributedSuitAI
from toontown.battle import BattleManagerAI
from direct.task import Task
from direct.directnotify import DirectNotifyGlobal
import SuitDNA
from toontown.battle import SuitBattleGlobals
import SuitTimings
from toontown.toon import NPCToons
from toontown.building import HQBuildingAI
from toontown.hood import ZoneUtil
from toontown.building import SuitBuildingGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals
import math
import time
import random

from SuitLegList import *

def debugs(f):
    def w(*args, **kw):
        fn = f.func_name
        print 'SP.%s called' % fn
        x = f(*args, **kw)
        print 'SP.%s returned %s' % (fn, x)
        return x
    
    return w
    
FACTOR = 1.5
FC = lambda x: int(x * FACTOR)

NUM_BLDG_TT = 0
NUM_BLDG_DD = .15
NUM_BLDG_DG = .25
NUM_BLDG_MM = .4
NUM_BLDG_BR = .55
NUM_BLDG_DL = .65
NUM_BLDG_FF = .5

ALLOWED_FO_TRACKS = ['s', 'l']
DEFAULT_COGDO_RATIO = .5

class DistributedSuitPlannerAI(DistributedObjectAI.DistributedObjectAI, SuitPlannerBase.SuitPlannerBase):
    CogdoPopFactor = config.GetFloat('cogdo-pop-factor', 1.5)
    CogdoRatio = min(1.0, max(0.0, config.GetFloat('cogdo-ratio', DEFAULT_COGDO_RATIO)))
    SuitHoodInfo = [
                    # tt
                    [2100,5,15,NUM_BLDG_TT,5,20,3,(1,5,10,40,60,80),(25,25,25,25),(1,2,3),[]],
                    [2200,3,10,NUM_BLDG_TT,5,15,3,(1,5,10,40,60,80),(10,70,10,10),(1,2,3),[]],
                    [2300,3,10,NUM_BLDG_TT,5,15,3,(1,5,10,40,60,80),(10,10,40,40),(1,2,3),[]],
                    
                    # dd
                    [1100,FC(1),FC(5),NUM_BLDG_DD,99,100,4,(1,5,10,40,60,80),(90,10,0,0),(2,3,4),[]],
                    [1200,FC(1),FC(5),NUM_BLDG_DD,99,100,4,(1,5,10,40,60,80),(0,0,90,10),(3,4,5,6),[]],
                    [1300,FC(1),FC(5),NUM_BLDG_DD,99,100,4,(1,5,10,40,60,80),(40,40,10,10),(3,4,5,6),[]],
                    
                    # br
                    [3100,FC(1),FC(5),NUM_BLDG_BR,99,100,4,(1,5,10,40,60,80),(90,10,0,0),(5,6,7),[]],
                    [3200,FC(1),FC(5),NUM_BLDG_BR,99,100,4,(1,5,10,40,60,80),(10,20,30,40),(5,6,7),[]],
                    [3300,FC(1),FC(5),NUM_BLDG_DL,99,100,4,(1,5,10,40,60,80),(5,85,5,5),(7,8,9),[]],
                    
                    # mm
                    [4100,FC(1),FC(5),NUM_BLDG_MM,99,100,4,(1,5,10,40,60,80),(0,0,50,50),(2,3,4),[]],
                    [4200,FC(1),FC(5),NUM_BLDG_MM,99,100,4,(1,5,10,40,60,80),(0,0,90,10),(3,4,5,6),[]],
                    [4300,FC(1),FC(5),NUM_BLDG_MM,99,100,4,(1,5,10,40,60,80),(50,50,0,0),(3,4,5,6),[]],
                    
                    # dg
                    [5100,FC(1),FC(5),NUM_BLDG_DG,99,100,4,(1,5,10,40,60,80),(0,20,10,70),(2,3,4),[]],
                    [5200,FC(1),FC(5),NUM_BLDG_DG,99,100,4,(1,5,10,40,60,80),(10,70,0,20),(3,4,5,6),[]],
                    [5300,FC(1),FC(5),NUM_BLDG_DG,99,100,4,(1,5,10,40,60,80),(5,5,5,85),(3,4,5,6),[]],
                    
                    # dl
                    [9100,FC(1),FC(5),NUM_BLDG_DL,99,100,4,(1,5,10,40,60,80),(25,25,25,25),(6,7,8,9),[]],
                    [9200,FC(1),FC(5),NUM_BLDG_DL,99,100,4,(1,5,10,40,60,80),(5,5,85,5),(6,7,8,9),[]],
                    
                    # hqs
                    [11000,3,15,0,0,0,4,(1,5,10,40,60,80),(0,0,0,100),(4,5,6),[]],
                    [11200,10,20,0,0,0,4,(1,5,10,40,60,80),(0,0,0,100),(4,5,6),[]],
                    [12000,10,20,0,0,0,4,(1,5,10,40,60,80),(0,0,100,0),(7,8,9),[]],
                    [13000,10,20,0,0,0,4,(1,5,10,40,60,80),(0,100,0,0),(8,9,10),[]],
                    
                    # ff
                    [7100,FC(3),FC(9),NUM_BLDG_FF,99,100,4,(1,5,10,40,60,80),(25,25,25,25),range(1, 11),[]]
                   ]
                   
    SUIT_HOOD_INFO_ZONE = 0
    SUIT_HOOD_INFO_MIN = 1
    SUIT_HOOD_INFO_MAX = 2
    SUIT_HOOD_INFO_BMIN = 3
    SUIT_HOOD_INFO_BMAX = 4
    SUIT_HOOD_INFO_BWEIGHT = 5
    SUIT_HOOD_INFO_SMAX = 6
    SUIT_HOOD_INFO_JCHANCE = 7
    SUIT_HOOD_INFO_TRACK = 8
    SUIT_HOOD_INFO_LVL = 9
    SUIT_HOOD_INFO_HEIGHTS = 10
    MAX_SUIT_TYPES = 6
    POP_UPKEEP_DELAY = 10
    POP_ADJUST_DELAY = 300
    PATH_COLLISION_BUFFER = 5
    TOTAL_MAX_SUITS = 50
    MIN_PATH_LEN = 40
    MAX_PATH_LEN = 300
    MIN_TAKEOVER_PATH_LEN = 2
    SUITS_ENTER_BUILDINGS = simbase.config.GetBool('want-suit-buildings', 1)
    SUIT_BUILDING_NUM_SUITS = 1.5
    SUIT_BUILDING_TIMEOUT = [
        None,
        None,
        None,
        None,
        None,
        None,
        72,
        60,
        48,
        36,
        24,
        12,
        6,
        3,
        1,
        0.5]
    TOTAL_SUIT_BUILDING_PCT = 18 * CogdoPopFactor
    BUILDING_HEIGHT_DISTRIBUTION = [
        14,
        18,
        25,
        23,
        20]
    TOTAL_BWEIGHT = 0
    TOTAL_BWEIGHT_PER_TRACK = [
        0,
        0,
        0,
        0]
    TOTAL_BWEIGHT_PER_HEIGHT = [
        0,
        0,
        0,
        0,
        0]
    for currHoodInfo in SuitHoodInfo:
        weight = currHoodInfo[SUIT_HOOD_INFO_BWEIGHT]
        tracks = currHoodInfo[SUIT_HOOD_INFO_TRACK]
        levels = currHoodInfo[SUIT_HOOD_INFO_LVL]
        heights = [
            0,
            0,
            0,
            0,
            0]
        for level in levels:
            (minFloors, maxFloors) = SuitBuildingGlobals.SuitBuildingInfo[level - 1][0]
            for i in range(minFloors - 1, maxFloors):
                heights[i] += 1
            
        
        currHoodInfo[SUIT_HOOD_INFO_HEIGHTS] = heights
        TOTAL_BWEIGHT += weight
        TOTAL_BWEIGHT_PER_TRACK[0] += weight * tracks[0]
        TOTAL_BWEIGHT_PER_TRACK[1] += weight * tracks[1]
        TOTAL_BWEIGHT_PER_TRACK[2] += weight * tracks[2]
        TOTAL_BWEIGHT_PER_TRACK[3] += weight * tracks[3]
        TOTAL_BWEIGHT_PER_HEIGHT[0] += weight * heights[0]
        TOTAL_BWEIGHT_PER_HEIGHT[1] += weight * heights[1]
        TOTAL_BWEIGHT_PER_HEIGHT[2] += weight * heights[2]
        TOTAL_BWEIGHT_PER_HEIGHT[3] += weight * heights[3]
        TOTAL_BWEIGHT_PER_HEIGHT[4] += weight * heights[4]
    
    defaultSuitName = simbase.config.GetString('suit-type', 'random')
    if defaultSuitName == 'random':
        defaultSuitName = None
    
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSuitPlannerAI')
    
    def __init__(self, air, zoneId):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        SuitPlannerBase.SuitPlannerBase.__init__(self)
        self.air = air
        self.zoneId = zoneId
        self.canonicalZoneId = ZoneUtil.getCanonicalZoneId(zoneId)
        if simbase.air.wantCogdominiums:
            if not hasattr(self.__class__, 'CogdoPopAdjusted'):
                self.__class__.CogdoPopAdjusted = True
                for index in xrange(len(self.SuitHoodInfo)):
                    hoodInfo = self.SuitHoodInfo[index]
                    hoodInfo[self.SUIT_HOOD_INFO_BMIN] = int(0.5 + self.CogdoPopFactor * hoodInfo[self.SUIT_HOOD_INFO_BMIN])
                    hoodInfo[self.SUIT_HOOD_INFO_BMAX] = int(0.5 + self.CogdoPopFactor * hoodInfo[self.SUIT_HOOD_INFO_BMAX])
                
            
        
        self.hoodInfoIdx = -1
        for index in range(len(self.SuitHoodInfo)):
            currHoodInfo = self.SuitHoodInfo[index]
            if currHoodInfo[self.SUIT_HOOD_INFO_ZONE] == self.canonicalZoneId:
                self.hoodInfoIdx = index
        
        self.currDesired = None
        self.baseNumSuits = (self.SuitHoodInfo[self.hoodInfoIdx][self.SUIT_HOOD_INFO_MIN] + self.SuitHoodInfo[self.hoodInfoIdx][self.SUIT_HOOD_INFO_MAX]) / 2
        self.targetNumSuitBuildings = 0
        if ZoneUtil.isWelcomeValley(self.zoneId):
            self.targetNumSuitBuildings = 0
        
        self.pendingBuildingTracks = []
        self.pendingBuildingHeights = []
        self.suitList = []
        self.numFlyInSuits = 0
        self.numBuildingSuits = 0
        self.numAttemptingTakeover = 0
        self.zoneInfo = { }
        self.zoneIdToPointMap = None
        self.cogHQDoors = []
        self.battleList = []
        self.battleMgr = BattleManagerAI.BattleManagerAI(self.air)
        self.setupDNA()
        if self.notify.getDebug():
            self.notify.debug('Creating a building manager AI in zone' + str(self.zoneId))
        
        self.buildingMgr = self.air.buildingManagers.get(self.zoneId)
        if self.buildingMgr:
            (blocks, hqBlocks, gagshopBlocks, petshopBlocks, kartshopBlocks, animBldgBlocks) = self.buildingMgr.getDNABlockLists()
            for currBlock in blocks:
                bldg = self.buildingMgr.getBuilding(currBlock)
                bldg.setSuitPlannerExt(self)
            
            for currBlock in animBldgBlocks:
                bldg = self.buildingMgr.getBuilding(currBlock)
                bldg.setSuitPlannerExt(self)
                
            self.targetNumSuitBuildings = int(len(animBldgBlocks + blocks) * self.SuitHoodInfo[self.hoodInfoIdx][self.SUIT_HOOD_INFO_BMIN])
            self.SuitHoodInfo[self.hoodInfoIdx][self.SUIT_HOOD_INFO_BMIN] = self.targetNumSuitBuildings
                
        else:
            self.notify.warning('No building manager at %s' % self.zoneId)
        
        self.dnaStore.resetBlockNumbers()
        self.initBuildingsAndPoints()
        numSuits = simbase.config.GetInt('suit-count', -1)
        if numSuits >= 0:
            self.currDesired = numSuits
        
        suitHood = simbase.config.GetInt('suits-only-in-hood', -1)
        if suitHood >= 0:
            if self.SuitHoodInfo[self.hoodInfoIdx][self.SUIT_HOOD_INFO_ZONE] != suitHood:
                self.currDesired = 0
            
        
        self.suitCountAdjust = 0
        
    def isBlockSuitTarget(self, block):
        for suit in self.suitList:
            if suit.buildingDestination == block:
                return 1
                
        return 0
    
    def cleanup(self):
        taskMgr.remove(self.taskName('sptUpkeepPopulation'))
        taskMgr.remove(self.taskName('sptAdjustPopulation'))
        for suit in self.suitList:
            suit.stopTasks()
            if suit.isGenerated():
                self.zoneChange(suit, suit.zoneId)
                suit.requestDelete()
                continue
        
        self.suitList = []
        self.numFlyInSuits = 0
        self.numBuildingSuits = 0
        self.numAttemptingTakeover = 0

    
    def delete(self):
        self.cleanup()
        DistributedObjectAI.DistributedObjectAI.delete(self)

    
    def initBuildingsAndPoints(self):
        if not self.buildingMgr:
            return None
        
        if self.notify.getDebug():
            self.notify.debug('Initializing building points')
        
        self.buildingFrontDoors = { }
        self.buildingSideDoors = { }
        for p in self.frontdoorPointList:
            blockNumber = p.getLandmarkBuildingIndex()
            if blockNumber < 0: #p < 0:
                self.notify.warning('No landmark building for (%s) in zone %d' % (repr(p), self.zoneId))
                continue
            if self.buildingFrontDoors.has_key(blockNumber):
                self.notify.warning('Multiple front doors for building %d in zone %d' % (blockNumber, self.zoneId))
                continue
            self.buildingFrontDoors[blockNumber] = p
        
        for p in self.sidedoorPointList:
            blockNumber = p.getLandmarkBuildingIndex()
            if blockNumber < 0: #p < 0:
                self.notify.warning('No landmark building for (%s) in zone %d' % (repr(p), self.zoneId))
                continue
            if self.buildingSideDoors.has_key(blockNumber):
                self.buildingSideDoors[blockNumber].append(p)
                continue
            self.buildingSideDoors[blockNumber] = [
                p]
        
        for bldg in self.buildingMgr.getBuildings():
            if isinstance(bldg, HQBuildingAI.HQBuildingAI):
                continue
            
            blockNumber = bldg.getBlock()[0]
            if not self.buildingFrontDoors.has_key(blockNumber):
                self.notify.warning('No front door for building %d in zone %d' % (blockNumber, self.zoneId))
            
            if not self.buildingSideDoors.has_key(blockNumber):
                self.notify.warning('No side door for building %d in zone %d' % (blockNumber, self.zoneId))
                continue
        

    
    def countNumSuitsPerTrack(self, count):
        for suit in self.suitList:
            if count.has_key(suit.track):
                count[suit.track] += 1
                continue
            count[suit.track] = 1
        

    
    def countNumBuildingsPerTrack(self, count):
        if self.buildingMgr:
            for building in self.buildingMgr.getBuildings():
                if building.isSuitBuilding():
                    if count.has_key(building.track):
                        count[building.track] += 1
                    else:
                        count[building.track] = 1

                
    def countNumBuildingsPerHeight(self, count):
        if self.buildingMgr:
            for building in self.buildingMgr.getBuildings():
                if building.isSuitBuilding():
                    height = building.numFloors - 1
                    count.setdefault(height, 0)
                    count[height] += 1
    
    def formatNumSuitsPerTrack(self, count):
        result = ' '
        for (track, num) in count.items():
            result += ' %s:%d' % (track, num)
        
        return result[2:]


    def calcDesiredNumFlyInSuits(self):
        if self.currDesired != None:
            return 0
        
        return self.baseNumSuits + self.suitCountAdjust

    
    def calcDesiredNumBuildingSuits(self):
        if self.currDesired != None:
            return self.currDesired
        
        if not self.buildingMgr:
            return 0
        
        suitBuildings = self.buildingMgr.getEstablishedSuitBlocks()
        return int(len(suitBuildings) * self.SUIT_BUILDING_NUM_SUITS)

    
    def getZoneIdToPointMap(self):
        if self.zoneIdToPointMap != None:
            return self.zoneIdToPointMap
        
        self.zoneIdToPointMap = { }
        for point in self.streetPointList:
            points = self.dnaStore.getAdjacentPoints(point)
            i = points.getNumPoints() - 1
            while i >= 0:
                pi = points.getPointIndex(i)
                p = self.pointIndexes[pi]
                i -= 1
                zoneName = self.dnaStore.getSuitEdgeZone(point.getIndex(), p.getIndex())
                zoneId = int(self.extractGroupName(zoneName))
                if self.zoneIdToPointMap.has_key(zoneId):
                    self.zoneIdToPointMap[zoneId].append(point)
                    continue
                self.zoneIdToPointMap[zoneId] = [
                    point]
        
        return self.zoneIdToPointMap

    
    def getStreetPointsForBuilding(self, blockNumber):
        pointList = []
        if self.buildingSideDoors.has_key(blockNumber):
            for doorPoint in self.buildingSideDoors[blockNumber]:
                points = self.dnaStore.getAdjacentPoints(doorPoint)
                i = points.getNumPoints() - 1
                while i >= 0:
                    pi = points.getPointIndex(i)
                    point = self.pointIndexes[pi]
                    if point.getPointType() == 0:#DNASuitPoint.STREETPOINT:
                        pointList.append(point)
                    
                    i -= 1
            
        
        if self.buildingFrontDoors.has_key(blockNumber):
            doorPoint = self.buildingFrontDoors[blockNumber]
            points = self.dnaStore.getAdjacentPoints(doorPoint)
            i = points.getNumPoints() - 1
            while i >= 0:
                pi = points.getPointIndex(i)
                pointList.append(self.pointIndexes[pi])
                i -= 1
        
        return pointList


    def createNewSuit(self, blockNumbers, streetPoints, toonBlockTakeover = None, cogdoTakeover = None, minPathLen = None, maxPathLen = None, buildingHeight = None, suitLevel = None, suitType = None, suitTrack = None, suitName = None, skelecog = None, revives = None):
        startPoint = None
        blockNumber = None
        if self.notify.getDebug():
            self.notify.debug('Choosing origin from %d+%d possibles.' % (len(streetPoints), len(blockNumbers)))
        
        while startPoint == None and len(blockNumbers) > 0:
            bn = random.choice(blockNumbers)
            blockNumbers.remove(bn)
            if self.buildingSideDoors.has_key(bn):
                for doorPoint in self.buildingSideDoors[bn]:
                    points = self.dnaStore.getAdjacentPoints(doorPoint)
                    
                    i = points.getNumPoints() - 1
                    while blockNumber == None and i >= 0:
                        pi = points.getPointIndex(i)
                        p = self.pointIndexes[pi]
                        i -= 1
                        startTime = SuitTimings.fromSuitBuilding
                        startTime += self.dnaStore.getSuitEdgeTravelTime(doorPoint.getIndex(), pi, self.suitWalkSpeed)
                        if not self.pointCollision(p, doorPoint, startTime):
                            startTime = SuitTimings.fromSuitBuilding
                            startPoint = doorPoint
                            blockNumber = bn
                            continue
                
        while startPoint == None and len(streetPoints) > 0:
            p = random.choice(streetPoints)
            streetPoints.remove(p)
            if not self.pointCollision(p, None, SuitTimings.fromSky):
                startPoint = p
                startTime = SuitTimings.fromSky
                continue
        if startPoint == None:
            return None
        
        newSuit = DistributedSuitAI.DistributedSuitAI(simbase.air, self)
        newSuit.startPoint = startPoint
        if blockNumber != None:
            newSuit.buildingSuit = 1
            if suitTrack == None:
                suitTrack = self.buildingMgr.getBuildingTrack(blockNumber)
            
        else:
            newSuit.flyInSuit = 1
            newSuit.attemptingTakeover = self.newSuitShouldAttemptTakeover()
            if newSuit.attemptingTakeover:
                if suitTrack == None and len(self.pendingBuildingTracks) > 0:
                    suitTrack = self.pendingBuildingTracks.pop(0)
                    self.pendingBuildingTracks.append(suitTrack)
                
                if buildingHeight == None and len(self.pendingBuildingHeights) > 0:
                    buildingHeight = self.pendingBuildingHeights.pop(0)
                    self.pendingBuildingHeights.append(buildingHeight)
                
            
        if suitName == None:
            (suitName, skelecog) = self.air.suitInvasionManager.getInvadingCog()
            if suitName == None:
                suitName = self.defaultSuitName
            
        
        if suitType == None and suitName != None:
            suitType = SuitDNA.getSuitType(suitName)
            suitTrack = SuitDNA.getSuitDept(suitName)
        
        if suitLevel == None and buildingHeight != None:
            suitLevel = self.chooseSuitLevel(self.SuitHoodInfo[self.hoodInfoIdx][self.SUIT_HOOD_INFO_LVL], 0)#buildingHeight)
        
        (suitLevel, suitType, suitTrack) = self.pickLevelTypeAndTrack(suitLevel, suitType, suitTrack)
        newSuit.setupSuitDNA(suitLevel, suitType, suitTrack)
        newSuit.buildingHeight = buildingHeight

        gotDestination = self.chooseDestination(newSuit, startTime, toonBlockTakeover = toonBlockTakeover, cogdoTakeover = cogdoTakeover, minPathLen = minPathLen, maxPathLen = maxPathLen)
        if not gotDestination:
            self.notify.debug("Couldn't get a destination in %d!" % self.zoneId)
            newSuit.doNotDeallocateChannel = None
            newSuit.delete()
            return None

        newSuit.initializePath()
        self.zoneChange(newSuit, None, newSuit.zoneId)
        if skelecog:
            newSuit.setSkelecog(skelecog)
        
        if revives:
            newSuit.setSkeleRevives(revives)
        
        newSuit.generateWithRequired(newSuit.zoneId)
        newSuit.moveToNextLeg(None)
        self.suitList.append(newSuit)
        if newSuit.flyInSuit:
            self.numFlyInSuits += 1
        
        if newSuit.buildingSuit:
            self.numBuildingSuits += 1
        
        if newSuit.attemptingTakeover:
            self.numAttemptingTakeover += 1
        
        return newSuit

    
    def countNumNeededBuildings(self):
        if not self.buildingMgr:
            return 0
        
        numSuitBuildings = len(self.buildingMgr.getSuitBlocks())
        numNeeded = self.targetNumSuitBuildings - numSuitBuildings
        return numNeeded

        
    def newSuitShouldAttemptTakeover(self):
        if not self.SUITS_ENTER_BUILDINGS:
            return 0
        
        numNeeded = self.countNumNeededBuildings()
                                
        if self.zoneId in (2100, 2200, 2300):
            # TTC (6% of chance, max 3 bldgs per street)
            if random.random() < .06:
                if self.numAttemptingTakeover == 0:
                    numSuitBuildings = len(self.buildingMgr.getSuitBlocks())
                    if numSuitBuildings < 3:
                        return 1
                        
        if self.numAttemptingTakeover >= numNeeded:
            self.pendingBuildingTracks = []
            return 0
        
        self.notify.debug('DSP %d is planning a takeover attempt in zone %d' % (self.getDoId(), self.zoneId))
        return 1


    def chooseDestination(self, suit, startTime, toonBlockTakeover = None, cogdoTakeover = None, minPathLen = None, maxPathLen = None):
        possibles = []
        backup = []
        
        if toonBlockTakeover != None:
            suit.attemptingTakeover = 1
            blockNumber = toonBlockTakeover
            if self.buildingFrontDoors.has_key(blockNumber):
                possibles.append((blockNumber, self.buildingFrontDoors[blockNumber]))
                            
        elif suit.attemptingTakeover:
            for blockNumber in self.buildingMgr.getToonBlocks():
                building = self.buildingMgr.getBuilding(blockNumber)
                (extZoneId, intZoneId) = building.getExteriorAndInteriorZoneId()
                if not NPCToons.isZoneProtected(intZoneId):
                    if self.buildingFrontDoors.has_key(blockNumber):
                        if not self.isBlockSuitTarget(blockNumber):
                            possibles.append((blockNumber, self.buildingFrontDoors[blockNumber]))
                                
            if cogdoTakeover is None:
                if suit.dna.dept in ALLOWED_FO_TRACKS:
                    cogdoTakeover = random.random() < self.CogdoRatio
            
        elif self.buildingMgr and 0:
            for blockNumber in self.buildingMgr.getSuitBlocks():
                track = self.buildingMgr.getBuildingTrack(blockNumber)
                if track == suit.track and self.buildingSideDoors.has_key(blockNumber):
                    for doorPoint in self.buildingSideDoors[blockNumber]:
                        possibles.append((blockNumber, doorPoint))
 
        backup = []
        for p in self.streetPointList:
            backup.append((None, p))
        
        if self.notify.getDebug():
            self.notify.debug('Choosing destination point from %d+%d possibles.' % (len(possibles), len(backup)))
        
        if len(possibles) == 0:
            possibles = backup
            backup = []
        
        if minPathLen == None:
            if suit.attemptingTakeover:
                minPathLen = self.MIN_TAKEOVER_PATH_LEN
            else:
                minPathLen = self.MIN_PATH_LEN
        
        if maxPathLen == None:
            maxPathLen = self.MAX_PATH_LEN
        
        retryCount = 0
        while len(possibles) > 0 and retryCount < 50:
            p = random.choice(possibles)
            possibles.remove(p)
            if len(possibles) == 0:
                possibles = backup
                backup = []
            
            try:
                path = self.genPath(suit.startPoint, p[1], minPathLen, maxPathLen)
                
            except Exception as e:
                print self.zoneId, e
                exit()
            
            if path and not self.pathCollision(path, startTime):                   
                suit.endPoint = p[1]
                suit.minPathLen = minPathLen
                suit.maxPathLen = maxPathLen
                suit.buildingDestination = p[0]
                
                if suit.buildingDestination is not None and self.zoneId == 7100:
                    print 'DSP assigned %r buildingDestination to %s/%s' % (suit, p[0], p[1].getIndex())
                    
                suit.buildingDestinationIsCogdo = cogdoTakeover
                suit.setPath(path)
                return 1
            
            retryCount += 1
        return 0


    def pathCollision(self, path, elapsedTime):
        pathLength = path.getNumPoints()
        i = 0
        pi = path.getPointIndex(i)
        point = self.pointIndexes[pi]
        adjacentPoint = self.pointIndexes[path.getPointIndex(i + 1)]
        while point.getPointType() in (1, 2):
            i += 1
            lastPi = pi
            pi = path.getPointIndex(i)
            adjacentPoint = point
            point = self.pointIndexes[pi]
            elapsedTime += self.dnaStore.getSuitEdgeTravelTime(lastPi, pi, self.suitWalkSpeed)
        result = self.pointCollision(point, adjacentPoint, elapsedTime)
        return result


    def pointCollision(self, point, adjacentPoint, elapsedTime):
        for suit in self.suitList:
            if suit.pointInMyPath(point, elapsedTime):
                return 1
        
        if adjacentPoint != None:
            return self.battleCollision(point, adjacentPoint)
        else:
            points = self.dnaStore.getAdjacentPoints(point)
            i = points.getNumPoints() - 1
            while i >= 0:
                pi = points.getPointIndex(i)
                p = self.pointIndexes[pi]
                i -= 1
                if self.battleCollision(point, p):
                    return 1

        return 0

    
    def battleCollision(self, point, adjacentPoint):
        zoneName = self.dnaStore.getSuitEdgeZone(point.getIndex(), adjacentPoint.getIndex())
        zoneId = int(self.extractGroupName(zoneName))
        return self.battleMgr.cellHasBattle(zoneId)

    
    def removeSuit(self, suit):
        self.zoneChange(suit, suit.zoneId)
        if self.suitList.count(suit) > 0:
            self.suitList.remove(suit)
            if suit.flyInSuit:
                self.numFlyInSuits -= 1
            
            if suit.buildingSuit:
                self.numBuildingSuits -= 1
            
            if suit.attemptingTakeover:
                self.numAttemptingTakeover -= 1
            
        
        suit.requestDelete()

    
    def countTakeovers(self):
        count = 0
        for suit in self.suitList:
            if suit.attemptingTakeover:
                count += 1
                continue
        
        return count

    
    def _DistributedSuitPlannerAI__waitForNextUpkeep(self):
        t = random.random() * 2.0 + self.POP_UPKEEP_DELAY
        taskMgr.doMethodLater(t, self.upkeepSuitPopulation, self.taskName('sptUpkeepPopulation'))

    
    def _DistributedSuitPlannerAI__waitForNextAdjust(self):
        t = random.random() * 10.0 + self.POP_ADJUST_DELAY
        taskMgr.doMethodLater(t, self.adjustSuitPopulation, self.taskName('sptAdjustPopulation'))


    def upkeepSuitPopulation(self, task):
        targetFlyInNum = self.calcDesiredNumFlyInSuits()
        targetFlyInNum = min(targetFlyInNum, self.TOTAL_MAX_SUITS - self.numBuildingSuits)
        streetPoints = self.streetPointList[:]
        flyInDeficit = ((targetFlyInNum - self.numFlyInSuits) + 3) / 4
        while flyInDeficit > 0:
            if not self.createNewSuit([], streetPoints):
                break
            
            flyInDeficit -= 1
        if self.buildingMgr:
            suitBuildings = self.buildingMgr.getEstablishedSuitBlocks()
        else:
            suitBuildings = []
        if self.currDesired != None:
            targetBuildingNum = max(0, self.currDesired - self.numFlyInSuits)
        else:
            targetBuildingNum = int(len(suitBuildings) * self.SUIT_BUILDING_NUM_SUITS)
        targetBuildingNum += flyInDeficit
        targetBuildingNum = min(targetBuildingNum, self.TOTAL_MAX_SUITS - self.numFlyInSuits)
        buildingDeficit = ((targetBuildingNum - self.numBuildingSuits) + 3) / 4
        while buildingDeficit > 0:
            if not self.createNewSuit(suitBuildings, streetPoints):
                break
            
            buildingDeficit -= 1
        if self.notify.getDebug() and self.currDesired == None:
            self.notify.debug('zone %d has %d of %d fly-in and %d of %d building suits.' % (self.zoneId, self.numFlyInSuits, targetFlyInNum, self.numBuildingSuits, targetBuildingNum))
            if buildingDeficit != 0:
                self.notify.debug('remaining deficit is %d.' % buildingDeficit)
            
        
        if self.buildingMgr:
            suitBuildings = self.buildingMgr.getEstablishedSuitBlocks()
            timeoutIndex = min(len(suitBuildings), len(self.SUIT_BUILDING_TIMEOUT) - 1)
            timeout = self.SUIT_BUILDING_TIMEOUT[timeoutIndex]
            if timeout != None:
                timeout *= 3600.0
                oldest = None
                oldestAge = 0
                now = time.time()
                for b in suitBuildings:
                    building = self.buildingMgr.getBuilding(b)
                    if hasattr(building, 'elevator'):
                        if building.elevator.fsm.getCurrentState().getName() == 'waitEmpty':
                            age = now - building.becameSuitTime
                            if age > oldestAge:
                                oldest = building
                                oldestAge = age
                
                if oldestAge > timeout:
                    self.notify.info('Street %d has %d buildings; reclaiming %0.2f-hour-old building.' % (self.zoneId, len(suitBuildings), oldestAge / 3600.0))
                    oldest.b_setVictorList([
                        0,
                        0,
                        0,
                        0])
                    oldest.updateSavedBy(None)
                    oldest.toonTakeOver()
                
            
        
        self._DistributedSuitPlannerAI__waitForNextUpkeep()
        return Task.done

    
    def adjustSuitPopulation(self, task):
        hoodInfo = self.SuitHoodInfo[self.hoodInfoIdx]
        if hoodInfo[self.SUIT_HOOD_INFO_MAX] == 0:
            self._DistributedSuitPlannerAI__waitForNextAdjust()
            return Task.done
        
        min = hoodInfo[self.SUIT_HOOD_INFO_MIN]
        max = hoodInfo[self.SUIT_HOOD_INFO_MAX]
        adjustment = random.choice((-2, -1, -1, 0, 0, 0, 1, 1, 2))
        self.suitCountAdjust += adjustment
        desiredNum = self.calcDesiredNumFlyInSuits()
        if desiredNum < min:
            self.suitCountAdjust = min - self.baseNumSuits
        elif desiredNum > max:
            self.suitCountAdjust = max - self.baseNumSuits
        
        self._DistributedSuitPlannerAI__waitForNextAdjust()
        return Task.done

    
    def suitTakeOver(self, blockNumber, suitTrack, difficulty, buildingHeight):
        if self.pendingBuildingTracks.count(suitTrack) > 0:
            self.pendingBuildingTracks.remove(suitTrack)
        
        if self.pendingBuildingHeights.count(buildingHeight) > 0:
            self.pendingBuildingHeights.remove(buildingHeight)
        
        building = self.buildingMgr.getBuilding(blockNumber)
        building.suitTakeOver(suitTrack, difficulty, buildingHeight)

    
    def cogdoTakeOver(self, blockNumber, difficulty, buildingHeight, dept):
        if self.pendingBuildingHeights.count(buildingHeight) > 0:
            self.pendingBuildingHeights.remove(buildingHeight)
        
        building = self.buildingMgr.getBuilding(blockNumber)
        building.cogdoTakeOver(difficulty, buildingHeight, dept)

    
    def recycleBuilding(self):
        bmin = self.SuitHoodInfo[self.hoodInfoIdx][self.SUIT_HOOD_INFO_BMIN]
        current = len(self.buildingMgr.getSuitBlocks())
        if self.targetNumSuitBuildings > bmin and current <= self.targetNumSuitBuildings:
            return
            self.targetNumSuitBuildings -= 1
            self.assignSuitBuildings(1)
        

    
    def assignInitialSuitBuildings(self):
        return
        
    def assignSuitBuildings(self, numToAssign):
        return

    def unassignSuitBuildings(self, numToAssign):
        return
    
    def chooseStreetWithPreference(self, hoodInfo, buildingTrackIndex, buildingHeight):
        dist = []
        for currHoodInfo in hoodInfo:
            weight = currHoodInfo[self.SUIT_HOOD_INFO_BWEIGHT]
            thisValue = weight * currHoodInfo[self.SUIT_HOOD_INFO_TRACK][buildingTrackIndex] * currHoodInfo[self.SUIT_HOOD_INFO_HEIGHTS][buildingHeight]
            dist.append(thisValue)
        
        totalWeight = sum(dist)
        c = random.random() * totalWeight
        t = 0
        for i in range(len(hoodInfo)):
            t += dist[i]
            if c < t:
                return hoodInfo[i]
                continue
        
        self.notify.warning('Weighted random choice failed!  Total is %s, chose %s' % (t, c))
        return random.choice(hoodInfo)

    
    def chooseSuitLevel(self, possibleLevels, buildingHeight):
        choices = []
        for level in possibleLevels:
            #(minFloors, maxFloors) = SuitBuildingGlobals.SuitBuildingInfo[level - 1][0]
            #if buildingHeight >= minFloors - 1 and buildingHeight <= maxFloors - 1:
                choices.append(level)
                
        if not choices:
            raise ValueError(self.zoneId)
        
        return random.choice(choices)

    
    def initTasks(self):
        #if self.zoneId == 7100:
        #    self.newSuitShouldAttemptTakeover = debugs(self.newSuitShouldAttemptTakeover)
        self._DistributedSuitPlannerAI__waitForNextUpkeep()
        self._DistributedSuitPlannerAI__waitForNextAdjust()

    
    def resyncSuits(self):
        for suit in self.suitList:
            suit.resync()
        

    
    def flySuits(self):
        for suit in self.suitList:
            if suit.pathState == 1:
                suit.flyAwayNow()

            
    def requestBattle(self, zoneId, suit, toonId):
        self.notify.debug('requestBattle() - zone: %d suit: %d toon: %d' % (zoneId, suit.doId, toonId))
        canonicalZoneId = ZoneUtil.getCanonicalZoneId(zoneId)
        if not self.battlePosDict.has_key(canonicalZoneId):
            return 0
        
        toon = self.air.doId2do.get(toonId)
        if toon.getBattleId() > 0:
            self.notify.warning('We tried to request a battle when the toon was already in battle')
            return 0
        
        if toon:
            if hasattr(toon, 'doId'):
                toon.b_setBattleId(toonId)
            
        
        pos = self.battlePosDict[canonicalZoneId]
        interactivePropTrackBonus = -1
        if simbase.config.GetBool('props-buff-battles', True) and self.cellToGagBonusDict.has_key(canonicalZoneId):
            tentativeBonusTrack = self.cellToGagBonusDict[canonicalZoneId]
            trackToHolidayDict = {
                ToontownBattleGlobals.SQUIRT_TRACK: ToontownGlobals.HYDRANTS_BUFF_BATTLES,
                ToontownBattleGlobals.THROW_TRACK: ToontownGlobals.MAILBOXES_BUFF_BATTLES,
                ToontownBattleGlobals.HEAL_TRACK: ToontownGlobals.TRASHCANS_BUFF_BATTLES }
            if tentativeBonusTrack in trackToHolidayDict:
                holidayId = trackToHolidayDict[tentativeBonusTrack]
                if simbase.air.holidayManager.isHolidayRunning(holidayId):#and simbase.air.holidayManager.getCurPhase(holidayId) >= 1:
                    interactivePropTrackBonus = tentativeBonusTrack
                
            
        
        self.battleMgr.newBattle(zoneId, zoneId, pos, suit, toonId, self._DistributedSuitPlannerAI__battleFinished, self.SuitHoodInfo[self.hoodInfoIdx][self.SUIT_HOOD_INFO_SMAX], interactivePropTrackBonus)
        for currOther in self.zoneInfo[zoneId]:
            self.notify.debug('Found suit %d in this new battle zone %d' % (currOther.getDoId(), zoneId))
            if currOther != suit:
                if currOther.pathState == 1 and currOther.legType == SuitLeg.TWalk:
                    self.checkForBattle(zoneId, currOther)
                
            currOther.legType == SuitLeg.TWalk
        
        return 1

    
    def _DistributedSuitPlannerAI__battleFinished(self, zoneId):
        self.notify.debug('DistSuitPlannerAI:  battle in zone ' + str(zoneId) + ' finished')
        currBattleIdx = 0
        while currBattleIdx < len(self.battleList):
            currBattle = self.battleList[currBattleIdx]
            if currBattle[0] == zoneId:
                self.notify.debug('DistSuitPlannerAI: battle removed')
                self.battleList.remove(currBattle)
                continue
            currBattleIdx = currBattleIdx + 1

    def _DistributedSuitPlannerAI__suitCanJoinBattle(self, zoneId):
        battle = self.battleMgr.getBattle(zoneId)
        if len(battle.suits) >= 4:
            return 0
        
        if battle:
            if simbase.config.GetBool('suits-always-join', 0):
                return 1
            
            jChanceList = self.SuitHoodInfo[self.hoodInfoIdx][self.SUIT_HOOD_INFO_JCHANCE]
            ratioIdx = (len(battle.toons) - battle.numSuitsEver) + 2
            if ratioIdx >= 0:
                if ratioIdx < len(jChanceList):
                    if random.randint(0, 99) < jChanceList[ratioIdx]:
                        return 1
                    
                else:
                    self.notify.warning('__suitCanJoinBattle idx out of range!')
                    return 1
            
        
        return 0

    
    def checkForBattle(self, zoneId, suit):
        if self.battleMgr.cellHasBattle(zoneId):
            if not (self.__suitCanJoinBattle(zoneId) and self.battleMgr.requestBattleAddSuit(zoneId, suit)):
                suit.flyAwayNow()
                return 1
        
        return 0
    
    def postBattleResumeCheck(self, suit):
        self.notify.debug('DistSuitPlannerAI:postBattleResumeCheck:  suit ' + str(suit.getDoId()) + ' is leaving battle')
        battleIndex = 0
        for currBattle in self.battleList:
            if suit.zoneId == currBattle[0]:
                self.notify.debug('    battle found' + str(suit.zoneId))
                for currPath in currBattle[1]:
                    for currPathPtSuit in range(suit.currWpt, suit.myPath.getNumPoints()):
                        ptIdx = suit.myPath.getPointIndex(currPathPtSuit)
                        if self.notify.getDebug():
                            self.notify.debug('    comparing' + str(ptIdx) + 'with' + str(currPath))
                        
                        if currPath == ptIdx:
                            if self.notify.getDebug():
                                self.notify.debug('    match found, telling' + 'suit to fly')
                            
                            return 0
                            continue
                    
                
            battleIndex = battleIndex + 1
        
        pointList = []
        for currPathPtSuit in range(suit.currWpt, suit.myPath.getNumPoints()):
            ptIdx = suit.myPath.getPointIndex(currPathPtSuit)
            if self.notify.getDebug():
                self.notify.debug('    appending point with index of' + str(ptIdx))
            
            pointList.append(ptIdx)
        
        self.battleList.append([
            suit.zoneId,
            pointList])
        return 1

    
    def zoneChange(self, suit, oldZone, newZone = None):
        if self.zoneInfo.has_key(oldZone) and suit in self.zoneInfo[oldZone]:
            self.zoneInfo[oldZone].remove(suit)
        
        if newZone != None:
            if not self.zoneInfo.has_key(newZone):
                self.zoneInfo[newZone] = []
            
            self.zoneInfo[newZone].append(suit)
        

    
    def d_setZoneId(self, zoneId):
        self.sendUpdate('setZoneId', [
            self.getZoneId()])

    
    def getZoneId(self):
        return self.zoneId

    
    def suitListQuery(self):
        suitIndexList = []
        for suit in self.suitList:
            suitIndexList.append(SuitDNA.suitHeadTypes.index(suit.dna.name))
        
        self.sendUpdateToAvatarId(self.air.getAvatarIdFromSender(), 'suitListResponse', [
            suitIndexList])

    
    def buildingListQuery(self):
        buildingDict = { }
        self.countNumBuildingsPerTrack(buildingDict)
        buildingList = [
            0,
            0,
            0,
            0]
        for dept in SuitDNA.suitDepts:
            if buildingDict.has_key(dept):
                buildingList[SuitDNA.suitDepts.index(dept)] = buildingDict[dept]
                continue
        
        self.sendUpdateToAvatarId(self.air.getAvatarIdFromSender(), 'buildingListResponse', [
            buildingList])

    
    def pickLevelTypeAndTrack(self, level = None, type = None, track = None):
        if level == None:
            level = random.choice(self.SuitHoodInfo[self.hoodInfoIdx][self.SUIT_HOOD_INFO_LVL])
        
        if type == None:
            typeChoices = range(max(level - 4, 1), min(level, self.MAX_SUIT_TYPES) + 1)
            if not typeChoices:
                print 'XXXX typeChoices is empty'
                print 'error dump:'
                print level, self.MAX_SUIT_TYPES, max(level - 4, 1), min(level, self.MAX_SUIT_TYPES)
            type = random.choice(typeChoices)
        else:
            level = min(max(level, type), type + 4)
        if track == None:
            track = SuitDNA.suitDepts[SuitBattleGlobals.pickFromFreqList(self.SuitHoodInfo[self.hoodInfoIdx][self.SUIT_HOOD_INFO_TRACK])]
        
        self.notify.debug('pickLevelTypeAndTrack: %d %d %s' % (level, type, track))
        return (level, type, track)


