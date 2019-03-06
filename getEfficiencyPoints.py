import ROOT
import re
import math
import json
import copy

def main():

    x = ROOT.Double()
    path1 = "turnons_data17_withEmulation_02_26.root"
    #path1 = "turnons.root"
    TFile1 = ROOT.TFile(path1)

    outputFilename = "efficiencyPointsDict_03_04"

    efficiencies = [0.95, 0.99, 0.995]
    
    efficiencyPointDict = {}
    efficiencyPointDictEmulated = {}
    efficiencyPointDictTDT = {}
    listHistNames = []
    listHists = []

    for h in TFile1.GetListOfKeys():
        ##print(h)
        #here you can avoid this clause or have a loop on an array of names
        #if "HLT_j260-HLT_j110" in h.GetName() :
            #listHists.append(TFile1.Get(h.GetName()))
            #continue
        ##print(h.GetName())
        ##print(TFile1.Get(h.GetName()))
        print(h.ReadObj())
        #print(TFile1.Get("effHists_jetTriggerEfficiencies_smallR/HLT_j400-HLT_j260_pt[0]TDT_turnon_TDT_effHists_jetTriggerEfficiencies_smallR/HLT_j400-HLT_j260_0_TDT"))
        ##listHists.append(TFile1.Get(h.GetName()))
        listHists.append(h.ReadObj())
    print(listHists)

    for hist in listHists:
        if type(hist) != ROOT.TGraphAsymmErrors:
            continue
        #histName = re.search('effHists_jetTriggerEfficiencies_smallR/(.*)_pt[0]_numTDT*', hist.GetName())
        #listHistNames.append(histName)
        histName = hist.GetName().rsplit('/', 1)[-1]
        #listHistNames.append(histName)
        efficiencyPoints = findEfficiencyPoints(hist, efficiencies)
        if "Emulated" in hist.GetName():
            histNameLabel = histName + "_Emulated"
            efficiencyPointDictEmulated[histNameLabel] = efficiencyPoints
            #print "'Emulated' found in: " + str(hist.GetName())
        if "TDT" in hist.GetName():
            histNameLabel = histName + "_TDT"
            efficiencyPointDictTDT[histNameLabel] = efficiencyPoints
            #print "'TDT' found in: " + str(hist.GetName())
        print(efficiencyPoints)
        efficiencyPointDict[histName] = efficiencyPoints

    with open(outputFilename+".json", 'wb') as outfile:
        #json.dump(efficiencyPointDict, outfile, indent=4)
        json.dump(efficiencyPointDictEmulated, outfile, indent=4)
        json.dump(efficiencyPointDictTDT, outfile, indent=4)

    with open(outputFilename+".py", "w") as filePy:
        #filePy.write(str(efficiencyPointDict))
        filePy.write(str(efficiencyPointDictEmulated))
        filePy.write(str(efficiencyPointDictTDT))
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
