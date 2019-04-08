import ROOT
import re
import math
import json
import copy

def main():

    x = ROOT.Double()
    #provide file path to root file containing turnon plots
    path1 = "turnons_data17_withEmulation_02_26.root"
    #path1 = "turnons.root"
    TFile1 = ROOT.TFile(path1)

    #name of output dictionary files (no file extension)
    outputFilename = "efficiencyPointsDict_03_04"

    #specify efficiency point values, add more or less to the list as needed
    efficiencies = [0.95, 0.99, 0.995]
    
    efficiencyPointDict = {}
    efficiencyPointDictEmulated = {}
    efficiencyPointDictTDT = {}
    listHistNames = []
    listHists = []

    for h in TFile1.GetListOfKeys():
        #here you can avoid this clause or have a loop on an array of names
        #if "HLT_j260-HLT_j110" in h.GetName() :
            #listHists.append(TFile1.Get(h.GetName()))
            #continue
        #print(h.ReadObj())
        listHists.append(h.ReadObj())
    #print(listHists)

    print "writing efficiency point information to " + outputFilename + ".json and " + outputFilename + ".py..."
    for hist in listHists:
        #jetTriggerEfficiencies should only produce TGraphAsymmErrors.  This script doesn't read TH1s
        if type(hist) != ROOT.TGraphAsymmErrors:
            continue

        #isolate name of trigger from hist name
        histName = hist.GetName().rsplit('/', 1)[-1]
        efficiencyPoints = findEfficiencyPoints(hist, efficiencies)
        if "Emulated" in hist.GetName():
            histNameLabel = histName + "_Emulated"
            efficiencyPointDictEmulated[histNameLabel] = efficiencyPoints
            #print "'Emulated' found in: " + str(hist.GetName())
        if "TDT" in hist.GetName():
            histNameLabel = histName + "_TDT"
            efficiencyPointDictTDT[histNameLabel] = efficiencyPoints
            #print "'TDT' found in: " + str(hist.GetName())
        #print(efficiencyPoints)
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

#function to find efficiency points for each turnon, specified efficiency value     
def findEfficiencyPoints(hist, efficiencyValues):
    x = ROOT.Double(0.0)
    y = ROOT.Double(0.0)
    xPrev = ROOT.Double(0.0)
    yPrev = ROOT.Double(0.0)
    minX = 0.0 #in case you want to force a minimum pT for efficiency
    effPoints = {}
    for value in efficiencyValues:
        ##print "checking turnon for", value
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
                   ##print "tempEffPoint reset to: ", tempEffPoint
           if i == (len(range(hist.GetN()))-1):
               ##print "final tempEffPoint: ", tempEffPoint
               effPoints[value] = tempEffPoint

    return effPoints
               
               
main()
