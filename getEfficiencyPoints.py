import ROOT
import re
import math
import json
import copy

def main():

    x = ROOT.Double()
    #path1 = "turnons_data17_withEmulation_02_26.root"
    path1 = "turnons.root"
    TFile1 = ROOT.TFile(path1)

    efficiencies = [0.95, 0.99, 0.995]
    
    efficiencyPointDict = {}
    listHistNames = []
    listHists = []

    for h in TFile1.GetListOfKeys():
        print(h)
        #here you can avoid this clause or have a loop on an array of names
        #if "HLT_j260-HLT_j110" in h.GetName() :
            #listHists.append(TFile1.Get(h.GetName()))
            #continue
        print(h.GetName())
        print(TFile1.Get(h.GetName()))
        #print(TFile1.Get("effHists_jetTriggerEfficiencies_smallR/HLT_j400-HLT_j260_pt[0]TDT_turnon_TDT_effHists_jetTriggerEfficiencies_smallR/HLT_j400-HLT_j260_0_TDT"))
        listHists.append(TFile1.Get(h.GetName()))
    print(listHists)

    for hist in listHists:
        #histName = re.search('effHists_jetTriggerEfficiencies_smallR/(.*)_pt[0]_numTDT*', hist.GetName())
        #listHistNames.append(histName)
        histName = hist.GetName().rsplit('/', 1)[-1]
        #listHistNames.append(histName)
        #if "Emulated" in histName:
        efficiencyPoints = findEfficiencyPoints(hist, efficiencies)
        print(efficiencyPoints)
        efficiencyPointDict[histName] = efficiencyPoints

    with open("efficiencyPointsDict_03_04.json", 'wb') as outfile:
        json.dump(efficiencyPointDict, outfile, indent=4)

    with open("efficiencyPointDict_03_04.py", "w") as filePy:
        filePy.write(str(efficiencyPointDict))
    #listHists[0].Print("v")
        
def findEfficiencyPoints(hist, efficiencyValues):
    x = ROOT.Double(0.0)
    y = ROOT.Double(0.0)
    xPrev = ROOT.Double(0.0)
    yPrev = ROOT.Double(0.0)
    minX = 0.0 #in case you want to force a minimum pT for efficiency
    effPoints = {}
    for value in efficiencyValues:
        print "checking turnon for", value
        tempEffPoint = 0.0
        effCut = value
        efficientXValues = []
        for i in range(hist.GetN()):
           hist.GetPoint(i,x,y)
           #print "i: ", i
           #print "x: ", x
           #print "y: ", y
           #print "tempEffPoint: ", tempEffPoint
           #print "minX: ", minX, " effCut: ", effCut
           if x > minX and y >= effCut:
               efficientXValues.append(x)
               hist.GetPoint(i-1,xPrev,yPrev)
               #print "xPrev: ", xPrev, " yPrev: ", yPrev
               if yPrev < effCut and x > 0:
                   tempEffPoint = copy.copy(x)
                   print "tempEffPoint reset to: ", tempEffPoint
           if i == (len(range(hist.GetN()))-1):
               print "final tempEffPoint: ", tempEffPoint
               effPoints[value] = tempEffPoint

    return effPoints
               
               
main()
