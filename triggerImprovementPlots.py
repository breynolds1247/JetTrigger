
import ROOT
import re
import math
import json
from ROOT import TLorentzVector
import pprint

#Formatting purposes
#import morisotColorsAndMarkers as colorsAndMarkers
#from plottingWrapper import drawPlotsOverlaidAndTheirRatio

def main():

    ROOT.gROOT.SetStyle("ATLAS")
    ROOT.gStyle.SetLegendBorderSize(0)
    ##Configurable variables
    ##manually re-name these for each new input .root files that you want to analyze
    #path1 = "/home/bryan/work/TLA/TriggerImprovementStudies/03_13_triggerImprovements_singleJet_gsc_mu/singleJet/hist-filelist.root"
    #path1 = "hist-filelist.root"
    path1 = "rawPtSpectraFiles/2016/test2016.root"
    efficiencyDictPath = "efficiencyPointsDict.json"
    plotTitle = "Jet pT(Lead) Single Jet Triggers"
    #outputPDF = "TriggerImprovements_2017_singleJet_allTriggers_10_10"
    outputPDF = "TriggerImprovements_triggerPaperTest_logX_2016"
    ##Formatting- change these if needed
    setLogX = True
    setLogY = False
    rebin = True
    rebinValue = 2

    ##Read in efficiency points from json
    ##When there are different probe collections for each reference collection, use the higher threshold reference collection
    #namesAndEffs = makeNamesAndEffPointDict(efficiencyDictPath)
    
    TFile1 = ROOT.TFile(path1)

    histList = []
    histNames = []
    legendLabels = []
    effPercentDict = {}
    #goodColors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 28, 30, 35, 38, 39, 41, 42, 46, 49] #20 distinctive colors.  If more than 20 plots things need to be re-though, including putting 20 plots on one canvas...
    goodColors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,  28, 29, 30, 35, 38, 39, 41, 42, 46, 49]
    stack = ROOT.THStack("hStack", plotTitle) 

    ##get leading pT histograms from .root file
    for h in TFile1.GetListOfKeys():
        h = h.ReadObj()
        if "h_PtLeadingReference_" in h.GetName():
            histList.append(TFile1.Get(h.GetName()))

    ##sort the histogram list by max value in the histogram.
    ##This allows the first histogram in the list to automatically set a y-axis that ensures all plots will be visible on the canvas         
    histList.sort(reverse=True, key=getMax)
    for hists in histList:
        histNames.append(hists.GetName())
        legendLabels.append(hists.GetName().replace('h_PtLeadingReference_',''))

    print "HISTNAMES: ", histNames
    print "LEGENDLABELS: ", legendLabels
        
    ##Draw histograms and label legend entries as trigger names
    ##Block for drawing all single trigger hists on same canvas
    ##Will look like a complete mess with too many hists
    for i,hist1 in enumerate(histList):
        if getMax(hist1) == 0:
            continue
        if rebin:
            hist1.Rebin(rebinValue)
        if "Efficient" not in hist1.GetName():
            triggerName = hist1.GetName().replace('h_PtLeadingReference_','')
            for j,hist2 in enumerate(histList):
                #print "hist test:", hist1.GetName(), hist2.GetName()
                if (triggerName in hist2.GetName()) and ("Efficient" in hist2.GetName()):
                    ##NOTE:
                    ##hist1 = all events
                    ##hist2 = efficient only
                    print "Matching hists: ", hist1.GetName(), hist2.GetName()
                    hist1.SetLineColor(goodColors[i])
                    hist2.SetLineColor(goodColors[i])
        if i == 0:
            TriggerCanvas = ROOT.TCanvas("cTriggers","2017 Leading pT")
            if setLogX is True:
                TriggerCanvas.SetLogx()
            if setLogY is True:
                TriggerCanvas.SetLogy()
            legend = ROOT.TLegend(0.825224,0.435737,0.979478,0.917304)
            legend.AddEntry(hist1,legendLabels[i],"l")
            hist1.SetTitle(plotTitle)
            hist1.GetXaxis().SetTitle("p_{T, Lead} [GeV]")
            hist1.GetYaxis().SetTitle("Events Recorded")
            singleTriggerLegend = ROOT.TLegend(0.71,0.67,0.9,0.77)
            #hist.SetLineColor(goodColors[i])
            hist1.SetStats(False)
            #hist2.Draw(False)
            hist1.Draw("hist")
            #hist2.Draw("hist")
            #stack.Add(hist)
        else:
            hist1.Draw("hist same")
            #hist1.SetLineColor(goodColors[i])
            legend.AddEntry(hist1,legendLabels[i],"l")
            #stack.Add(hist)
            
    legend.Draw()
    TriggerCanvas.Update()
    TriggerCanvas.Print(outputPDF + ".pdf","pdf")

    ##Stacked histogram
    histList.sort(reverse=False, key=getMax)
    for i,hist in enumerate(histList):
        if "allTriggers" not in hist.GetName():
            hist.SetFillColor(hist.GetLineColor())
            stack.Add(hist)
    stackCanvas = ROOT.TCanvas("cStack","2017 Leading pT")
    stack.Draw("hist NOSTACK")
    stack.GetXaxis().SetTitle("p_{T,Lead} [GeV]")
    stack.GetYaxis().SetTitle("Number of Recorded Events")
    #stack.Draw("hist")
    legend.Draw()
    stackCanvas.Update()
    stackCanvas.Print(outputPDF + "_THStack.pdf","pdf")

    ##sawtooth all trigger plots
    allTriggerCanvas = ROOT.TCanvas("cAllTrigger","2017 Leading pT")
    if setLogX is True:
        allTriggerCanvas.SetLogx()
    if setLogY is True:
        allTriggerCanvas.SetLogy()
    allTriggerHist = TFile1.Get("h_PtLeadingReference_allTriggers")
    allTriggerHist_efficient = TFile1.Get("h_PtLeadingReference_allTriggers_efficientEntriesOnly")
    allTriggerHist.SetTitle(plotTitle + "(All Triggers)")
    allTriggerHist.GetXaxis().SetTitle("#it{p}_{T,Lead} [GeV]")
    allTriggerHist.GetXaxis().SetTitleOffset(1.4)
    allTriggerHist.GetYaxis().SetTitle("Events/1 GeV")
    allTriggerHist.SetStats(False)
    allTriggerHist.SetLineColor(ROOT.kBlack)
    allTriggerHist.SetFillColor(ROOT.kWhite)
    allTriggerHist_efficient.SetLineColor(ROOT.kBlack)
    allTriggerHist_efficient.SetFillColor(ROOT.kBlack)
    allTriggerHist_efficient.SetLineStyle(ROOT.kDashed)
    allTriggerHist.SetFillStyle(3144)
    allTriggerHist_efficient.SetFillStyle(3144)
    if rebin:
            allTriggerHist.Rebin(rebinValue)
            allTriggerHist_efficient.Rebin(rebinValue)
    if setLogX is True:
        allTriggerHist.GetXaxis().SetRange(2,1000)
    allTriggerHist.Draw("hist")
    allTriggerHist_efficient.Draw("hist same")
    efficiencyPercentage = calculateEffPercent(allTriggerHist, allTriggerHist_efficient)
    effPercentLabel = ROOT.TLatex(0.7, 0.78,"Efficient Entries: "+ str(round(efficiencyPercentage, 3))+"%")
    effPercentLabel.SetNDC(ROOT.kTRUE)
    effPercentLabel.SetTextSize(0.03)
    effPercentLabel.Draw()
    effPercentDict["allTriggers"] = efficiencyPercentage
    atlasText = ROOT.TLatex(0.7, 0.88, "#it{#bf{ATLAS}} Internal")
    atlasText.SetNDC(ROOT.kTRUE)
    atlasText.Draw()
    atlasDetails = ROOT.TLatex(0.7, 0.83, "#sqrt{s} = 13 TeV, X.X fb^{#minus 1}")
    atlasDetails.SetNDC(ROOT.kTRUE)
    atlasDetails.SetTextSize(0.03)
    atlasDetails.Draw()
    legend_allTrig = ROOT.TLegend(0.71,0.67,0.9,0.77)
    legend_allTrig.AddEntry(allTriggerHist,"All Entries","l")
    legend_allTrig.AddEntry(allTriggerHist_efficient,"Efficient Entries","l")
    legend_allTrig.Draw()
    allTriggerCanvas.Update()
    allTriggerCanvas.Print(outputPDF + "_allTrigger.pdf","pdf")

    ##Match standard pT spectra to corresponding efficient pT spectra
    ##Plot each pair individually, save to one pdf
    singleTriggerCanvas = ROOT.TCanvas("cSingleTriggers","2017 Single Jet Leading pT")
    singleTriggerCanvas.Print(outputPDF + "_efficientHistComparisons.pdf[","pdf")
    if setLogX is True:
        singleTriggerCanvas.SetLogx()
    if setLogY is True:
        singleTriggerCanvas.SetLogy()
    for j,hist1 in enumerate(histList):
        singleTriggerLegend = ROOT.TLegend(0.71,0.67,0.9,0.77)
        if "Efficient" not in hist1.GetName():
            triggerName = hist1.GetName().replace('h_PtLeadingReference_','')
            for hist2 in histList:
                #print "hist test:", hist1.GetName(), hist2.GetName()
                if (triggerName in hist2.GetName()) and ("Efficient" in hist2.GetName()):
                    ##NOTE:
                    ##hist1 = all events
                    ##hist2 = efficient only
                    print "Matching hists: ", hist1.GetName(), hist2.GetName()
                    hist1.SetTitle(plotTitle)
                    hist1.GetXaxis().SetTitle("#it{p}_{T,Lead} " + triggerName + " [GeV]")
                    hist1.GetXaxis().SetTitleOffset(1.4)
                    hist1.GetYaxis().SetTitle("Events/1 GeV")
                    #hist2.SetLineStyle(2)
                    #hist1.SetLineColor(ROOT.kRed)
                    hist1.SetLineColor(ROOT.kBlack)
                    hist2.SetLineColor(ROOT.kBlack)
                    #hist1.SetFillColor(ROOT.kRed)
                    hist1.SetFillColor(ROOT.kWhite)
                    hist2.SetFillColor(ROOT.kBlack)
                    hist2.SetLineStyle(ROOT.kDashed)
                    hist1.SetFillStyle(3144)
                    hist2.SetFillStyle(3144)
                    hist1.SetStats(False)
                    if rebin:
                        hist1.Rebin(rebinValue)
                        hist2.Rebin(rebinValue)
                    #re-scale xaxis
                    rescaledHist1 = rescaleXAxis(hist1, hist2, triggerName)
                    rescaledHist2 = rescaleXAxis(hist2, hist2, triggerName)
                    rescaledHist1.Draw("hist")
                    rescaledHist2.Draw("hist same")
                    ###hist1.Draw("hist")
                    ###hist2.Draw("hist same")
                    efficiencyPercentage = calculateEffPercent(hist1, hist2)
                    effPercentLabel = ROOT.TLatex(0.70, 0.78,"Efficient Entries: "+ str(round(efficiencyPercentage, 3))+"%")
                    effPercentLabel.SetNDC(ROOT.kTRUE)
                    effPercentLabel.SetTextSize(0.03)
                    effPercentLabel.Draw()
                    effPercentDict[triggerName] = efficiencyPercentage
                    atlasText = ROOT.TLatex(0.70, 0.88, "#it{#bf{ATLAS}} Internal")
                    atlasText.SetNDC(ROOT.kTRUE)
                    atlasText.Draw()
                    atlasDetails = ROOT.TLatex(0.70, 0.83, "#sqrt{s} = 13 TeV, X.X fb^{#minus 1}")
                    atlasDetails.SetNDC(ROOT.kTRUE)
                    atlasDetails.SetTextSize(0.03)
                    atlasDetails.Draw()
                    singleTriggerLegend.AddEntry(hist1,"All Entries","l")
                    singleTriggerLegend.AddEntry(hist2,"Efficient Entries","l")
                    singleTriggerLegend.Draw()
                    singleTriggerCanvas.Update()
                    #if j == 0:
                    #    singleTriggerCanvas.Print(outputPDF + "_efficientHistComparisons.pdf[","pdf")
                    #else:
                    singleTriggerCanvas.Print(outputPDF + "_efficientHistComparisons.pdf","pdf")
    singleTriggerCanvas.Print(outputPDF + "_efficientHistComparisons.pdf]","pdf")

    pp = pprint.PrettyPrinter(indent=1)
    with open(outputPDF + "_effPercentDict.py", "w") as filePy:
        filePy.write(str(pp.pformat(effPercentDict)))

def getMax(histogram):
    return histogram.GetMaximum()

def makeNamesAndEffPointDict(effDictPath):
    namesAndEffs = {}
    with open(effDictPath) as f:
        effDict = json.load(f)

    for key1 in effDict.keys():
        #print key1
        #print(effDict[key1])
        tempProbe1 = key1.split('-', 1)[0]
        tempRef1 = key1.rsplit('-', 1)[1]
        #print key1.split('-', 1)
        #print "probe jet: ", tempProbe1
        #print "ref jet: ", tempRef1
        tempRefThreshold1 = tempRef1.split('j', 1)[-1].split('_L1', 1)[0]
        #namesAndEffs[tempProbe1] = effDict[key1]
        #print tempRefThreshold1
        for key2 in effDict.keys():
            tempProbe2 = key2.split('-', 1)[0]
            tempRef2 = key2.rsplit('-', 1)[1]
            tempRefThreshold2 = tempRef2.split('j', 1)[-1].split('_L1', 1)[0]
            #print "threshold 1: ", float(tempRefThreshold1), " threshold 2: ", float(tempRefThreshold2)
            if ((tempProbe2 == tempProbe1) and (float(tempRefThreshold2) > float(tempRefThreshold1))):
                namesAndEffs[tempProbe1] = effDict[key2]
        #print namesAndEffs
        
    return namesAndEffs

def drawHistsWithEfficiencyPoints(hist, label, namesEffDict, canvas):
    if label not in namesEffDict.keys():
        print label, " does not exist in dictionaries"
        return None
    for key in namesEffDict.keys():
        if key == label:
            print "key == label success"
            effPoint95 = namesEffDict[key]['0.95']
            #print effPoint95
            effPoint99 = namesEffDict[key]['0.99']
            effPoint995 = namesEffDict[key]['0.995']
            hist.Draw("hist")
            canvas.Update()
            effHist95 = hist.Clone()
            effHist99 = hist.Clone()
            effHist995 = hist.Clone()
            #print "effHist: ", effHist
            for bin in range(hist.GetNbinsX()):
                if bin >= 1 and bin < effPoint95:
                    effHist95.SetBinContent(bin, 0.0)
                if bin >= 1 and bin < effPoint99:
                    effHist99.SetBinContent(bin, 0.0)
                if bin >= 1 and bin < effPoint995:
                    effHist995.SetBinContent(bin, 0.0)
            #ymax = hist.GetMaximum()
            #ymax = ROOT.gPad.GetUymax()
            #print "ymax: ", ymax
            #line95 = ROOT.TLine(effPoint95,0,effPoint95,ymax)
            #line95.SetLineColor(2)
            #line95.SetLineStyle(9)
            #line95.Draw()
            effHist95.SetLineStyle(2)
            effHist95.Draw("hist")
            effHist99.SetLineStyle(2)
            effHist99.Draw("hist")
            effHist995.SetLineStyle(2)
            effHist995.Draw("hist")
            canvas.Update()
            return effHist995
            #return effHist99
            #return effHist95

def calculateEffPercent(stdHist, effHist):
    numEventsStd = stdHist.Integral()
    numEventsEff = effHist.Integral()
    if numEventsStd == 0:
        effPercent = 0
    else:
        effFrac = numEventsEff/numEventsStd
        effPercent = effFrac*100.0
    return effPercent

def rescaleXAxis(hist, effHist, trigName):
    rescaledHist = hist
    ##syntax: 
    ##FindFirstBinAbove(<double threshold>,<int axis [1=x,2=y,3=z]>)
    firstFilledBin = hist.FindFirstBinAbove(0.0, 1)
    lastFilledBin = hist.FindLastBinAbove(0.0, 1)

    firstBinLowEdge = hist.GetXaxis().GetBinLowEdge(firstFilledBin)
    lastBinHighEdge = hist.GetXaxis().GetBinUpEdge(lastFilledBin)
    xmin = firstBinLowEdge - 1.0
    xmax = lastBinHighEdge - 1.0
    
    ##Play with ways to ignore single-entry bins that throw off the axis range
    print trigName
    #trigThreshold = float(filter(str.isdigit, trigName))
    trigThresholdSearch = re.search('j(\d+)', trigName)
    #print trigThresholdSearch
    trigThreshold = int(trigThresholdSearch.group(1))
    print trigThreshold

    effPoint = effHist.GetXaxis().GetBinLowEdge(effHist.FindFirstBinAbove(0.0, 1))

    #rescaledHist.GetXaxis().SetLimits((firstBinLowEdge - 2.0), (lastBinHighEdge + 2.0))
    if (firstBinLowEdge < trigThreshold/2.0 and trigThreshold > 30 and trigThreshold != 0):
         xmin = int(trigThreshold/2.5)
         if (trigThreshold > 300):
             xmin = trigThreshold/1.33
             
    if (lastBinHighEdge > effPoint*4 and trigThreshold != 0):
        xmax = int(effPoint*4)

    #rescaledHist.GetXaxis().SetRangeUser((firstBinLowEdge - 1.0), (lastBinHighEdge + 1.0))
    rescaledHist.GetXaxis().SetRangeUser(xmin, xmax)
    rescaledHist.GetXaxis().GetMoreLogLabels()
    
    return rescaledHist

main()
